"""Config Flow für die IKB Smart Meter Integration (Kaifa MA309).

Zweistufiger Einrichtungsassistent:
    Schritt 1 (user):  Port-Typ wählen (by-id oder ttyUSB/ttyACM)
    Schritt 2 (port):  Konkreten Port auswählen + AES-128-Schlüssel eingeben

Options Flow:
    Update-Intervall in Sekunden konfigurieren (5–3600 s)
"""

from __future__ import annotations

import glob
import logging
from typing import Any

import serial.tools.list_ports
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_COM_PORT,
    CONF_KEY_HEX,
    CONF_PORT_TYPE,
    CONF_SERIAL_NO,
    DOMAIN,
    OPT_DATA_INTERVAL,
    OPT_DATA_INTERVAL_VALUE,
    PORT_TYPE_BY_ID,
    PORT_TYPE_TTY,
)
from .exceptions import SmartmeterException
from .smartmeter import Smartmeter

_LOGGER = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Port-Scan-Hilfsfunktionen (laufen im Thread-Pool, nicht im Event-Loop)
# ---------------------------------------------------------------------------

def _get_by_id_ports() -> list[str]:
    """Gibt alle Einträge unter /dev/serial/by-id/ zurück (stabile Symlinks)."""
    return sorted(glob.glob("/dev/serial/by-id/*"))


def _get_tty_ports() -> list[str]:
    """Gibt ttyUSB*- und ttyACM*-Geräte zurück (via pyserial, Fallback: glob)."""
    ports = serial.tools.list_ports.comports(include_links=True)
    result = sorted(
        p.device for p in ports
        if "ttyUSB" in p.device or "ttyACM" in p.device
    )
    if not result:
        # Fallback, falls pyserial keine Ergebnisse liefert
        result = sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
    return result


def _get_ports_for_type(port_type: str) -> list[str]:
    """Gibt die passende Port-Liste für den gewählten Port-Typ zurück."""
    return _get_by_id_ports() if port_type == PORT_TYPE_BY_ID else _get_tty_ports()


# ---------------------------------------------------------------------------
# Verbindungstest
# ---------------------------------------------------------------------------

def _validate_and_connect(data: dict[str, Any]) -> dict[str, str]:
    """Testet die Verbindung zum Zähler und liest die Gerätenummer aus.

    Args:
        data: Dict mit CONF_COM_PORT und CONF_KEY_HEX

    Returns:
        Dict mit 'title' und 'device_number'

    Raises:
        SmartmeterException: Wenn keine Verbindung hergestellt werden kann.
    """
    com_port = data[CONF_COM_PORT]
    key_hex  = data[CONF_KEY_HEX]

    _LOGGER.debug("Validating connection on port=%s", com_port)
    try:
        adapter   = Smartmeter(com_port, key_hex)
        obisdata  = adapter.read()
        device_no = obisdata.DeviceNumber.value or com_port
        return {
            "title":         f"Smart Meter '{device_no}'",
            "device_number": device_no,
        }
    except SmartmeterException as exc:
        _LOGGER.warning("Could not connect to device=%s: %s", com_port, exc)
        raise


# ---------------------------------------------------------------------------
# Config Flow
# ---------------------------------------------------------------------------

class SmartmeterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Zweistufiger Einrichtungsassistent für den IKB Smart Meter."""

    VERSION = 1

    def __init__(self) -> None:
        self._port_type: str | None  = None
        self._ports_list: list[str]  = []

    # ------------------------------------------------------------------
    # Schritt 1 – Port-Typ wählen
    # ------------------------------------------------------------------

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Erster Schritt: Auswahl des Port-Typs."""
        if user_input is not None:
            self._port_type = user_input[CONF_PORT_TYPE]
            return await self.async_step_port()

        schema = vol.Schema(
            {
                vol.Required(CONF_PORT_TYPE, default=PORT_TYPE_BY_ID): SelectSelector(
                    SelectSelectorConfig(
                        options=[PORT_TYPE_BY_ID, PORT_TYPE_TTY],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    # ------------------------------------------------------------------
    # Schritt 2 – Port und Schlüssel eingeben
    # ------------------------------------------------------------------

    async def async_step_port(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Second screen: select port + enter key."""
        # Scan ports (executor so we don't block the event loop)
        self._ports_list = await self.hass.async_add_executor_job(
            _get_ports_for_type, self._port_type
        )
        if not self._ports_list:
            return self.async_abort(reason="no_serial_ports")

        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await self.hass.async_add_executor_job(
                    _validate_and_connect, user_input
                )
            except SmartmeterException:
                _LOGGER.warning(
                    "Verbindungstest auf Port %s fehlgeschlagen.",
                    user_input.get(CONF_COM_PORT),
                )
                return self.async_abort(reason="cannot_connect")
            else:
                device_unique_id = info["device_number"]
                await self.async_set_unique_id(device_unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_COM_PORT:  user_input[CONF_COM_PORT],
                        CONF_KEY_HEX:   user_input[CONF_KEY_HEX],
                        CONF_SERIAL_NO: device_unique_id,
                    },
                )

        default_port = self._ports_list[0]
        schema = vol.Schema(
            {
                vol.Required(CONF_COM_PORT, default=default_port): SelectSelector(
                    SelectSelectorConfig(
                        options=self._ports_list,
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(CONF_KEY_HEX): str,
            }
        )
        return self.async_show_form(
            step_id="port", data_schema=schema, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> "SmartMeterOptionsFlowHandler":
        """Get the options flow for this handler."""
        return SmartMeterOptionsFlowHandler()


# ---------------------------------------------------------------------------
# Options flow (update interval)
# ---------------------------------------------------------------------------

class SmartMeterOptionsFlowHandler(OptionsFlow):
    """Configurable options for the smart meter."""

    async def async_step_init(self, user_input=None) -> ConfigFlowResult:
        """Manage the options."""
        _errors: dict[str, str] = {}

        if user_input is not None:
            interval = user_input[OPT_DATA_INTERVAL]
            if interval is None:
                _errors["base"] = "data_interval_empty"
            elif not 5 <= interval <= 3600:
                _errors["base"] = "data_interval_wrong"
            else:
                return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        OPT_DATA_INTERVAL,
                        default=self.config_entry.options.get(
                            OPT_DATA_INTERVAL, OPT_DATA_INTERVAL_VALUE
                        ),
                    ): int,
                }
            ),
            errors=_errors,
        )
