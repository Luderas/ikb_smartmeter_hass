"""Serielle Kommunikation mit dem Kaifa MA309 (IKB) – M-Bus Single-Frame, AES-128-CTR.

Der Kaifa MA309 sendet alle ~5 Sekunden selbstständig einen vollständigen
M-Bus Long Frame mit allen Messwerten. Dieser wird hier empfangen,
gesucht, extrahiert und zur Entschlüsselung weitergegeben.
"""

from __future__ import annotations
import logging
import time

import serial
from serial.serialutil import (
    EIGHTBITS,
    PARITY_NONE,
    STOPBITS_ONE,
    SerialException,
    SerialTimeoutException,
)

from .decrypt import Decrypt, MBUS_START, MBUS_STOP
from .exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)
from .obisdata import ObisData

_LOGGER = logging.getLogger(__name__)

# Kaifa MA309 sends one self-contained M-Bus Long Frame every ~5 s.
# Zeitlimit in Sekunden, bis ein vollständiger M-Bus-Frame empfangen sein muss
_READ_TIMEOUT_S = 15

# Poll-Intervall beim Warten auf neue Bytes vom seriellen Port
_POLL_INTERVAL_S = 0.05


def _find_next_frame(buf: bytearray) -> tuple[int, bytes] | None:
    """Sucht im Puffer nach dem nächsten gültigen M-Bus Long Frame.

    M-Bus Long Frame-Struktur:
        68 LL LL 68  …Payload…  CS 16

    Args:
        buf: Empfangspuffer mit rohen seriellen Daten

    Returns:
        (start_offset, frame_bytes) wenn ein gültiger Frame gefunden wurde,
        sonst None.
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
    """Liest einen Messrahmen vom Kaifa MA309 über einen seriellen M-Bus-Adapter.

    Verwendung:
        sm = Smartmeter("/dev/ttyUSB0", "0123456789ABCDEF0123456789ABCDEF")
        obisdata = sm.read()
        print(obisdata.VoltageL1.value)

    Das Objekt ist nicht thread-sicher. Für parallele Zugriffe jeweils eine
    eigene Instanz verwenden.
    """

    def __init__(
        self,
        port: str,
        key_hex_string: str,
        baudrate: int    = 2400,         # Kaifa MA309 kommuniziert mit 2400 Baud
        parity: str      = PARITY_NONE,
        stopbits: int    = STOPBITS_ONE,
        bytesize: int    = EIGHTBITS,
    ) -> None:
        """Initialisiert den Smartmeter-Reader.

        Args:
            port:           Serieller Port, z. B. /dev/ttyUSB0 oder
                            /dev/serial/by-id/usb-...
            key_hex_string: AES-128-Schlüssel als 32-stelliger Hex-String
            baudrate:       Baudrate (Standard: 2400 für Kaifa MA309)
            parity:         Parität (Standard: keine)
            stopbits:       Stoppbits (Standard: 1)
            bytesize:       Datenbits (Standard: 8)
        """
        self._port            = port
        self._key_hex_string  = key_hex_string
        self._baudrate        = baudrate
        self._parity          = parity
        self._stopbits        = stopbits
        self._bytesize        = bytesize
        self._serial: serial.Serial | None = None
        self._is_running      = False



    def read(self) -> ObisData:
        """Öffnet den seriellen Port, wartet auf einen vollständigen M-Bus-Frame
        und gibt die geparsten OBIS-Daten zurück.

        Returns:
            ObisData-Objekt mit allen vom Zähler gelieferten Messwerten.

        Raises:
            SmartmeterException:        Bei ungültigem Frame oder laufendem read()
            SmartmeterSerialException:  Port nicht verfügbar
            SmartmeterTimeoutException: Kein Frame innerhalb von _READ_TIMEOUT_S
        """
        if self._is_running:
            raise SmartmeterException("Smartmeter.read() is already running.")

        try:
            self._open_serial()
            self._is_running = True

            buf        = bytearray()
            start_time = time.monotonic()

            _LOGGER.debug("Waiting for M-Bus frame on %s …", self._port)

            while True:
                # Verfügbare Bytes in den Puffer lesen
                if self._serial.in_waiting > 0:
                    buf.extend(self._serial.read(self._serial.in_waiting))

                # Vollständigen Frame im Puffer suchen
                result = _find_next_frame(buf)
                if result is not None:
                    _, frame_bytes = result
                    _LOGGER.debug("Frame found (%d bytes), decrypting …", len(frame_bytes))

                    dec = Decrypt(frame_bytes, self._key_hex_string)
                    dec.parse_all()
                    return ObisData(dec)

                # Timeout-Prüfung
                if time.monotonic() - start_time > _READ_TIMEOUT_S:
                    raise SmartmeterTimeoutException(
                        f"Kein gültiger M-Bus-Frame innerhalb von {_READ_TIMEOUT_S} s empfangen."
                    )

                time.sleep(_POLL_INTERVAL_S)

        except SmartmeterException:
            raise  # Smartmeter-Ausnahmen direkt weitergeben
        except Exception as exc:
            raise SmartmeterException(f"Unexpected error in Smartmeter.read(): {exc}") from exc
        finally:
            self._is_running = False
            self._close_serial()

    # ------------------------------------------------------------------
    # Serial helpers
    # ------------------------------------------------------------------

    def _open_serial(self) -> None:
        """Öffnet den seriellen Port, falls noch nicht geöffnet."""
        if self._serial is not None and self._serial.is_open:
            _LOGGER.debug("Serial port '%s' already open.", self._port)
            return
        try:
            _LOGGER.debug(
                "Opening serial port '%s' @ %d baud.", self._port, self._baudrate
            )
            self._serial = serial.Serial(
                port     = self._port,
                baudrate = self._baudrate,
                parity   = self._parity,
                stopbits = self._stopbits,
                bytesize = self._bytesize,
                timeout  = 1,
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
        """Schließt den seriellen Port, falls geöffnet."""
        try:
            if self._serial is not None and self._serial.is_open:
                self._serial.close()
        except Exception as exc:
            raise SmartmeterException(
                f"Closing port '{self._port}' failed."
            ) from exc
