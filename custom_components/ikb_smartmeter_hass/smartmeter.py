"""Smartmeter reader for Kaifa MA309 (IKB) – M-Bus single-frame, AES-128-CTR."""

import logging
import time

from serial.serialutil import (
    EIGHTBITS,
    PARITY_NONE,
    STOPBITS_ONE,
    SerialException,
    SerialTimeoutException,
)
import serial

from .decrypt import Decrypt, MBUS_START, MBUS_STOP
from .exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)
from .obisdata import ObisData

_LOGGER = logging.getLogger(__name__)

# Kaifa MA309 sends one self-contained M-Bus Long Frame every ~5 s.
# Minimum meaningful payload length (inner frame without header/trailer).
MIN_DATA_LEN = 23

# How long to wait for a complete frame (seconds)
READ_TIMEOUT_S = 15


def _find_next_frame(buf: bytearray) -> tuple[int, bytes] | None:
    """
    Search *buf* for the next valid M-Bus Long Frame.
    Returns (start_offset, frame_bytes) or None.
    """
    limit = len(buf) - 5
    i = 0
    while i < limit:
        if (
            buf[i] == MBUS_START
            and buf[i + 1] == buf[i + 2]
            and buf[i + 3] == MBUS_START
        ):
            length = buf[i + 1]
            total  = length + 6   # header(4) + payload(L) + CS(1) + stop(1)
            end    = i + total
            if end <= len(buf) and buf[end - 1] == MBUS_STOP:
                return i, bytes(buf[i:end])
        i += 1
    return None


class Smartmeter:
    """Connects to and reads data from a Kaifa MA309 smart meter."""

    def __init__(
        self,
        port: str,
        key_hex_string: str,
        baudrate: int = 2400,
        parity: str = PARITY_NONE,
        stopbits: int = STOPBITS_ONE,
        bytesize: int = EIGHTBITS,
    ) -> None:
        self._port           = port
        self._key_hex_string = key_hex_string
        self._baudrate       = baudrate
        self._parity         = parity
        self._stopbits       = stopbits
        self._bytesize       = bytesize
        self._my_serial: serial.Serial | None = None
        self._is_running     = False

    # ------------------------------------------------------------------

    def read(self) -> ObisData:
        """Open the serial port, wait for one complete frame and return ObisData."""
        if self._is_running:
            raise SmartmeterException("Smartmeter.read() is already running.")

        try:
            self._open_serial()
            self._is_running = True

            buf        = bytearray()
            start_time = time.monotonic()

            _LOGGER.debug("Waiting for M-Bus frame on %s …", self._port)

            while True:
                if self._my_serial.in_waiting > 0:
                    buf.extend(self._my_serial.read(self._my_serial.in_waiting))

                result = _find_next_frame(buf)
                if result is not None:
                    _, frame_bytes = result
                    _LOGGER.debug("Frame found (%d bytes), decrypting …", len(frame_bytes))

                    dec = Decrypt(frame_bytes, self._key_hex_string)
                    dec.parse_all()
                    return ObisData(dec)

                elapsed = time.monotonic() - start_time
                if elapsed > READ_TIMEOUT_S:
                    raise SmartmeterTimeoutException(
                        f"No valid M-Bus frame received within {READ_TIMEOUT_S} s."
                    )

                time.sleep(0.05)

        except SmartmeterException:
            raise
        except Exception as exc:
            raise SmartmeterException(f"Unexpected error in Smartmeter.read(): {exc}") from exc
        finally:
            self._is_running = False
            self._close_serial()

    # ------------------------------------------------------------------
    # Serial helpers
    # ------------------------------------------------------------------

    def _open_serial(self) -> None:
        if self._my_serial is not None and self._my_serial.is_open:
            _LOGGER.debug("Serial port '%s' already open.", self._port)
            return
        try:
            _LOGGER.debug(
                "Opening serial port '%s' @ %d baud.", self._port, self._baudrate
            )
            self._my_serial = serial.Serial(
                port      = self._port,
                baudrate  = self._baudrate,
                parity    = self._parity,
                stopbits  = self._stopbits,
                bytesize  = self._bytesize,
                timeout   = 1,
            )
        except SerialTimeoutException as exc:
            raise SmartmeterTimeoutException(
                f"Timeout opening port '{self._port}'."
            ) from exc
        except SerialException as exc:
            raise SmartmeterSerialException(
                f"Unable to open port '{self._port}'."
            ) from exc
        except Exception as exc:
            raise SmartmeterException(
                f"Connection to '{self._port}' failed."
            ) from exc

    def _close_serial(self) -> None:
        try:
            if self._my_serial is not None and self._my_serial.is_open:
                self._my_serial.close()
        except Exception as exc:
            raise SmartmeterException(
                f"Closing port '{self._port}' failed."
            ) from exc
