"""AES-128-CTR Entschlüsselung für Kaifa MA309 M-Bus-Frames (IKB).

Frame-Aufbau (M-Bus Long Frame):
    68 LL LL 68              ← M-Bus Start-Delimiter (LL = Nutzdatenlänge)
      53 FF 00 01 xx         ← CI-Byte + Adressbytes
      DB 08 [8 Byte]         ← System-Titel-Tag + System-Titel ("KFM..." o.ä.)
      82 01 09               ← BER-kodierte APDU-Länge
      21                     ← Security-Control-Byte
      [4 Byte]               ← Frame-Counter (Big-Endian, monoton steigend)
      [verschlüsselte Daten] ← AES-128-CTR-Payload
    CS 16                    ← M-Bus Prüfsumme + Stop-Delimiter

IV für AES-128-CTR (16 Byte):
    System-Titel (8 Byte) || Frame-Counter (4 Byte) || 0x00000002 (4 Byte)
"""

from __future__ import annotations

import binascii
import struct

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from .constants import DataType, PhysicalUnits
from .exceptions import SmartmeterException
from .obis import Obis
from .obisvalue import ObisValueBytes, ObisValueFloat

# ---------------------------------------------------------------------------
# M-Bus-Frame-Konstanten
# ---------------------------------------------------------------------------

MBUS_START = 0x68  # Start-Delimiter für M-Bus Long Frame
MBUS_STOP  = 0x16  # Stop-Delimiter

# Offsets innerhalb des Inner Frames (nach Abschneiden von „68 LL LL 68"):
#   [0]      CI-Byte  (0x53)
#   [1..4]   Adress-/Flag-Bytes
#   [5]      Tag 0xDB (System-Titel folgt)
#   [6]      0x08     (Länge des System-Titels)
#   [7..14]  System-Titel (8 Byte)
#   [15..17] BER-Länge (82 01 09)
#   [18]     Security-Control-Byte (0x21)
#   [19..22] Frame-Counter (4 Byte, Big-Endian)
#   [23..]   Verschlüsselter Payload

_SYSTITLE_OFFSET = 7
_SYSTITLE_LEN    = 8
_FRAMECTR_OFFSET = 19
_FRAMECTR_LEN    = 4
_ENC_DATA_OFFSET = 23
_MIN_INNER_LEN   = 24

# Fester IV-Suffix (AES-CTR Initial-Counter-Value)
_IV_SUFFIX = struct.pack(">I", 2)  # 0x00000002

# DLMS Scaler/Unit-Struktur: 02 02 0F <scaler:int8> 16 <unit:uint8>
_SCALER_UNIT_HDR  = (0x02, 0x02, 0x0F)
_SCALER_UNIT_SIZE = 6


class Decrypt:
    """Entschlüsselt und parst einen einzelnen Kaifa MA309 M-Bus-Frame.
    
    Verwendung:
        dec = Decrypt(frame_bytes, "0123456789ABCDEF0123456789ABCDEF")
        dec.parse_all()
        voltage = dec.get_obis_value("VoltageL1")
    """

    def __init__(self, frame: bytes, key_hex_string: str) -> None:
        """Initialisiert und entschlüsselt den Frame.
        
        Args:
            frame:          Komplette M-Bus-Frame-Bytes (68 LL LL 68 … CS 16)
            key_hex_string: AES-128-Schlüssel als 32-stelliger Hex-String
            
        Raises:
            SmartmeterException: Bei ungültigem Frame-Format oder fehlgeschlagener
                                 AES-Entschlüsselung.
        """
        self.obis_values: dict[bytes, ObisValueFloat | ObisValueBytes | None] = {}

        key   = binascii.unhexlify(key_hex_string)
        inner = frame[4:-2]  # 68 LL LL 68 Header und CS 16 Trailer entfernen

        if len(inner) < _MIN_INNER_LEN or inner[0] != 0x53:
            raise SmartmeterException(
                f"Frame zu kurz oder falsches CI-Byte: {inner[:4].hex()}"
            )

        sys_title = inner[_SYSTITLE_OFFSET : _SYSTITLE_OFFSET + _SYSTITLE_LEN]
        frame_ctr = inner[_FRAMECTR_OFFSET : _FRAMECTR_OFFSET + _FRAMECTR_LEN]
        encrypted = inner[_ENC_DATA_OFFSET :]

        # IV = System-Titel || Frame-Counter || 0x00000002
        iv = sys_title + frame_ctr + _IV_SUFFIX

        try:
            cipher    = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            self._decrypted: bytes = decryptor.update(encrypted) + decryptor.finalize()
        except Exception as exc:
            raise SmartmeterException(f"AES-CTR-Entschlüsselung fehlgeschlagen: {exc}") from exc

    # ------------------------------------------------------------------
    # Öffentliche Methoden
    # ------------------------------------------------------------------

    def parse_all(self) -> None:
        """Parst alle OBIS-Einträge aus dem entschlüsselten Payload.
        
        Sucht im Byte-Stream nach OBIS-Markierungen (OctetString-Tag + Länge 6)
        und liest den jeweils folgenden Wert entsprechend seinem DLMS-Datentyp.
        """
        plain = self._decrypted
        i     = 0
        total = len(plain)
        self.obis_values = {}

        while i < total - 10:
            # OBIS-Marker: OctetString-Tag (0x09) gefolgt von Länge 6 (0x06)
            if plain[i] == DataType.OctetString and plain[i + 1] == 0x06:
                obis_code = bytes(plain[i + 2 : i + 8])
                i += 8
                if i >= total:
                    break

                dtype = plain[i]

                # Dispatch je nach DLMS-Datentyp
                if dtype == DataType.OctetString:
                    i = self._parse_octet_string(plain, i, obis_code)
                elif dtype == DataType.LongUnsigned:       # uint16
                    i = self._parse_long_unsigned(plain, i, obis_code)
                elif dtype == DataType.Long:               # int16
                    i = self._parse_long(plain, i, obis_code)
                elif dtype == DataType.DoubleLongUnsigned: # uint32
                    i = self._parse_double_long_unsigned(plain, i, obis_code)
                elif dtype == DataType.DoubleLong:         # int32
                    i = self._parse_double_long(plain, i, obis_code)
                else:
                    i += 1  # unbekannter Typ – überspringen
            else:
                i += 1

    def get_obis_value(self, name: str) -> ObisValueFloat | ObisValueBytes | None:
        """Gibt den geparsten Wert für einen benannten OBIS-Code zurück.
        
        Args:
            name: Attributname aus der Obis-Klasse, z. B. "VoltageL1"
            
        Returns:
            ObisValueFloat, ObisValueBytes oder None wenn nicht vorhanden.
        """
        obis_code = getattr(Obis, name, None)
        if obis_code is None:
            return None
        return self.obis_values.get(obis_code)

    # ------------------------------------------------------------------
    # Private Hilfsmethoden
    # ------------------------------------------------------------------

    @staticmethod
    def _read_scaler_unit(plain: bytes, pos: int) -> tuple[int, int, int]:
        """Liest eine DLMS-Scaler/Unit-Struktur an Position pos.
        
        Returns:
            (scaler, unit_code, bytes_consumed) – oder (0, 0, 0) wenn nicht vorhanden.
        """
        if (
            pos + _SCALER_UNIT_SIZE <= len(plain)
            and plain[pos]     == _SCALER_UNIT_HDR[0]
            and plain[pos + 1] == _SCALER_UNIT_HDR[1]
            and plain[pos + 2] == _SCALER_UNIT_HDR[2]
            and plain[pos + 4] == DataType.Enum
        ):
            scaler = struct.unpack_from("b", plain, pos + 3)[0]  # signed int8
            unit   = plain[pos + 5]
            return scaler, unit, _SCALER_UNIT_SIZE
        return 0, 0, 0

    @staticmethod
    def _to_physical_unit(unit_code: int) -> PhysicalUnits:
        """Konvertiert einen DLMS-Einheitscode in ein PhysicalUnits-Enum."""
        try:
            return PhysicalUnits(unit_code)
        except ValueError:
            return PhysicalUnits.Undef

    def _parse_octet_string(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        """Parst einen OctetString (z. B. Zeitstempel, Gerätenummer)."""
        slen = plain[pos + 1]
        raw  = bytes(plain[pos + 2 : pos + 2 + slen])
        pos += 2 + slen

        if slen == 12:
            # DLMS DateTime: JJJJ MM TT Wochentag HH MM SS Hundertstel TZ DST Status
            try:
                year  = struct.unpack_from(">H", raw, 0)[0]
                month, day, hour, minute, second = raw[2], raw[3], raw[5], raw[6], raw[7]
                val_str = f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
            except Exception:
                val_str = raw.hex()
            self.obis_values[obis_code] = ObisValueBytes(val_str.encode())
        else:
            self.obis_values[obis_code] = ObisValueBytes(raw)

        return pos

    def _parse_long_unsigned(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        """Parst einen uint16-Wert mit optionaler Scaler/Unit-Struktur."""
        raw_val          = struct.unpack_from(">H", plain, pos + 1)[0]
        scaler, unit, n  = self._read_scaler_unit(plain, pos + 3)
        self.obis_values[obis_code] = ObisValueFloat(
            raw_val, self._to_physical_unit(unit), scaler
        )
        return pos + 3 + n

    def _parse_long(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        """Parst einen int16-Wert mit optionaler Scaler/Unit-Struktur."""
        raw_val          = struct.unpack_from(">h", plain, pos + 1)[0]
        scaler, unit, n  = self._read_scaler_unit(plain, pos + 3)
        self.obis_values[obis_code] = ObisValueFloat(
            raw_val, self._to_physical_unit(unit), scaler
        )
        return pos + 3 + n

    def _parse_double_long_unsigned(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        """Parst einen uint32-Wert mit optionaler Scaler/Unit-Struktur."""
        raw_val          = struct.unpack_from(">I", plain, pos + 1)[0]
        scaler, unit, n  = self._read_scaler_unit(plain, pos + 5)
        self.obis_values[obis_code] = ObisValueFloat(
            raw_val, self._to_physical_unit(unit), scaler
        )
        return pos + 5 + n

    def _parse_double_long(self, plain: bytes, pos: int, obis_code: bytes) -> int:
        """Parst einen int32-Wert mit optionaler Scaler/Unit-Struktur."""
        raw_val          = struct.unpack_from(">i", plain, pos + 1)[0]
        scaler, unit, n  = self._read_scaler_unit(plain, pos + 5)
        self.obis_values[obis_code] = ObisValueFloat(
            raw_val, self._to_physical_unit(unit), scaler
        )
        return pos + 5 + n
