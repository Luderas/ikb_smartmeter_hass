"""Decrypts Kaifa MA309 (IKB) M-Bus frames using AES-128-CTR.

Frame layout (M-Bus Long Frame):
  68 L L 68                     <- M-Bus start  (L = payload length)
    53 FF 00 01 xx               <- CI + address bytes
    DB 08 [8 bytes system-title] <- DLMS system title tag (e.g. "KFM...")
    82 01 09                     <- BER-encoded APDU length
    21                           <- security control byte
    [4 bytes frame counter]      <- big-endian, monotonically increasing
    [encrypted payload]          <- AES-128-CTR
  CS 16                          <- M-Bus checksum + stop

IV for AES-128-CTR (16 bytes):
  system-title (8) || frame-counter (4) || 0x00000002 (4)
"""

import binascii
import struct

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .constants import DataType, PhysicalUnits
from .exceptions import SmartmeterException
from .obis import Obis
from .obisvalue import ObisValueBytes, ObisValueFloat

# -------------------------------------------------------------------
# M-Bus frame layout constants
# -------------------------------------------------------------------
MBUS_START = 0x68
MBUS_STOP  = 0x16

# Inner frame offsets (after stripping outer 68 L L 68 header)
#   [0]      CI byte  0x53
#   [1..4]   address / flags
#   [5]      tag 0xDB  (system title follows)
#   [6]      0x08      (system title length)
#   [7..14]  system title (8 bytes)
#   [15..17] BER length  (82 01 09)
#   [18]     security control byte  (0x21)
#   [19..22] frame counter (4 bytes big-endian)
#   [23..]   encrypted payload

SYSTITLE_OFFSET  = 7
SYSTITLE_LEN     = 8
FRAMECTR_OFFSET  = 19
FRAMECTR_LEN     = 4
ENC_DATA_OFFSET  = 23
MIN_INNER_LEN    = 24

# AES-CTR IV suffix
IV_SUFFIX = struct.pack(">I", 2)   # 0x00000002

# DLMS scaler/unit structure prefix: 02 02 0F <scaler:int8> 16 <unit:uint8>
SCALER_UNIT_HDR  = (0x02, 0x02, 0x0F)
SCALER_UNIT_SIZE = 6

# Value data type sizes
DOUBLELONG_SIZE = 4   # uint32 / int32
LONG_SIZE       = 2   # uint16 / int16


class Decrypt:
    """Decrypts and parses a single Kaifa MA309 M-Bus frame."""

    def __init__(self, frame: bytes, key_hex_string: str) -> None:
        """
        Parameters
        ----------
        frame           : complete M-Bus frame bytes (68 L L 68 ... CS 16)
        key_hex_string  : AES-128 key as 32-character hex string
        """
        self.obis_values: dict[bytes, ObisValueFloat | ObisValueBytes | None] = {}

        key  = binascii.unhexlify(key_hex_string)
        inner = frame[4:-2]   # strip 68 L L 68 header and CS 16 trailer

        if len(inner) < MIN_INNER_LEN or inner[0] != 0x53:
            raise SmartmeterException(
                f"Frame too short or wrong CI byte: {inner[:4].hex()}"
            )

        sys_title  = inner[SYSTITLE_OFFSET  : SYSTITLE_OFFSET + SYSTITLE_LEN]
        frame_ctr  = inner[FRAMECTR_OFFSET  : FRAMECTR_OFFSET + FRAMECTR_LEN]
        encrypted  = inner[ENC_DATA_OFFSET  :]

        iv = sys_title + frame_ctr + IV_SUFFIX

        try:
            cipher    = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            self._data_decrypted: bytes = decryptor.update(encrypted) + decryptor.finalize()
        except Exception as exc:
            raise SmartmeterException(f"AES-CTR decryption failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def parse_all(self) -> None:
        """Parse all OBIS entries from the decrypted payload."""
        plain = self._data_decrypted
        i = 0
        total = len(plain)
        self.obis_values = {}

        while i < total - 10:
            # OBIS marker: OctetString tag (0x09) + length 6 (0x06)
            if plain[i] == DataType.OctetString and plain[i + 1] == 0x06:
                obis_code = bytes(plain[i + 2 : i + 8])
                i += 8
                if i >= total:
                    break
                dtype = plain[i]

                if dtype == DataType.OctetString:
                    i = self._parse_octet_string(plain, i, obis_code)
                elif dtype == DataType.LongUnsigned:       # uint16  0x12
                    i = self._parse_long_unsigned(plain, i, obis_code)
                elif dtype == DataType.Long:               # int16   0x10
                    i = self._parse_long(plain, i, obis_code)
                elif dtype == DataType.DoubleLongUnsigned: # uint32  0x06
                    i = self._parse_double_long_unsigned(plain, i, obis_code)
                elif dtype == DataType.DoubleLong:         # int32   0x05
                    i = self._parse_double_long(plain, i, obis_code)
                else:
                    i += 1
            else:
                i += 1

    def get_obis_value(self, name: str) -> ObisValueFloat | ObisValueBytes | None:
        """Return the parsed value for a named OBIS attribute."""
        obis_code = getattr(Obis, name, None)
        if obis_code is None:
            return None
        return self.obis_values.get(obis_code)

    # ------------------------------------------------------------------
    # Private parsers
    # ------------------------------------------------------------------

    @staticmethod
    def _read_scaler_unit(plain: bytes, pos: int) -> tuple[int, int, int]:
        """
        Try to read a DLMS scaler/unit structure at *pos*.
        Returns (scaler, unit_code, bytes_consumed).
        Returns (0, 0, 0) if the structure is not present.
        """
        if (
            pos + SCALER_UNIT_SIZE <= len(plain)
            and plain[pos]     == SCALER_UNIT_HDR[0]
            and plain[pos + 1] == SCALER_UNIT_HDR[1]
            and plain[pos + 2] == SCALER_UNIT_HDR[2]
            and plain[pos + 4] == DataType.Enum
        ):
            scaler = struct.unpack_from("b", plain, pos + 3)[0]   # signed int8
            unit   = plain[pos + 5]
            return scaler, unit, SCALER_UNIT_SIZE
        return 0, 0, 0

    def _parse_octet_string(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        slen = plain[pos + 1]
        raw  = bytes(plain[pos + 2 : pos + 2 + slen])
        pos += 2 + slen

        if slen == 12:
            # DLMS DateTime: YY YY MM DD DoW HH MM SS hh tz dst status
            try:
                yr = struct.unpack_from(">H", raw, 0)[0]
                mo, dy, hh, mm, ss = raw[2], raw[3], raw[5], raw[6], raw[7]
                val_str = f"{yr}-{mo:02d}-{dy:02d} {hh:02d}:{mm:02d}:{ss:02d}"
            except Exception:
                val_str = raw.hex()
            self.obis_values[obis_code] = ObisValueBytes(val_str.encode())
        else:
            self.obis_values[obis_code] = ObisValueBytes(raw)

        return pos

    def _parse_long_unsigned(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        raw_val           = struct.unpack_from(">H", plain, pos + 1)[0]
        scaler, unit, n   = self._read_scaler_unit(plain, pos + 3)
        pos              += 3 + n
        try:
            pu = PhysicalUnits(unit)
        except ValueError:
            pu = PhysicalUnits.Undef
        self.obis_values[obis_code] = ObisValueFloat(raw_val, pu, scaler)
        return pos

    def _parse_long(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        raw_val           = struct.unpack_from(">h", plain, pos + 1)[0]
        scaler, unit, n   = self._read_scaler_unit(plain, pos + 3)
        pos              += 3 + n
        try:
            pu = PhysicalUnits(unit)
        except ValueError:
            pu = PhysicalUnits.Undef
        self.obis_values[obis_code] = ObisValueFloat(raw_val, pu, scaler)
        return pos

    def _parse_double_long_unsigned(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        raw_val           = struct.unpack_from(">I", plain, pos + 1)[0]
        scaler, unit, n   = self._read_scaler_unit(plain, pos + 5)
        pos              += 5 + n
        try:
            pu = PhysicalUnits(unit)
        except ValueError:
            pu = PhysicalUnits.Undef
        self.obis_values[obis_code] = ObisValueFloat(raw_val, pu, scaler)
        return pos

    def _parse_double_long(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        raw_val           = struct.unpack_from(">i", plain, pos + 1)[0]
        scaler, unit, n   = self._read_scaler_unit(plain, pos + 5)
        pos              += 5 + n
        try:
            pu = PhysicalUnits(unit)
        except ValueError:
            pu = PhysicalUnits.Undef
        self.obis_values[obis_code] = ObisValueFloat(raw_val, pu, scaler)
        return pos
