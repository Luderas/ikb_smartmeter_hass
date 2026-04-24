"""Config flow for Smart Meter Austria (IKB / Kaifa MA309)."""
from __future__ import annotations

import glob
import logging
import os
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
# Port scanning helpers
# ---------------------------------------------------------------------------

def _get_by_id_ports() -> list[str]:
    """Return all entries under /dev/serial/by-id/."""
    paths = sorted(glob.glob("/dev/serial/by-id/*"))
    return paths if paths else []


def _get_tty_ports() -> list[str]:
    """Return ttyUSB* and ttyACM* devices detected by pyserial."""
    ports = serial.tools.list_ports.comports(include_links=True)
    result = sorted(
        p.device for p in ports
        if "ttyUSB" in p.device or "ttyACM" in p.device
    )
    # Fall back to a glob scan if pyserial returns nothing
    if not result:
        result = sorted(
            glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*")
        )
    return result


def _get_ports_for_type(port_type: str) -> list[str]:
    """Return the appropriate port list for the chosen type."""
    if port_type == PORT_TYPE_BY_ID:
        return _get_by_id_ports()
    return _get_tty_ports()


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------

def _validate_and_connect(data: dict[str, Any]) -> dict[str, str]:
    """Try to connect and read one frame; return title/device_number."""
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
# Config flow
# ---------------------------------------------------------------------------

class SmartmeterConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the smart meter."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialise."""
        self._port_type: str | None = None
        self._ports_list: list[str] = []

    # ------------------------------------------------------------------
    # Step 1 – choose port type (by-id or ttyUSB)
    # ------------------------------------------------------------------

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """First screen: select port type."""
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
    # Step 2 – pick a specific port and enter the key
    # ------------------------------------------------------------------

    async def async_step_port(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Second screen: select port + enter key."""
        errors: dict[str, str] = {}

        # Scan ports (executor so we don't block the event loop)
        self._ports_list = await self.hass.async_add_executor_job(
            _get_ports_for_type, self._port_type
        )
        if not self._ports_list:
            return self.async_abort(reason="no_serial_ports")

        if user_input is not None:
            try:
                info = await self.hass.async_add_executor_job(
                    _validate_and_connect, user_input
                )
            except SmartmeterException:
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
