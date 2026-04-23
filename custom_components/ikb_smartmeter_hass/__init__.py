"""The Smart Meter Austria integration (IKB / Kaifa MA309)."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    CONF_COM_PORT,
    CONF_KEY_HEX,
    DOMAIN,
    OPT_DATA_INTERVAL,
    OPT_DATA_INTERVAL_VALUE,
    PLATFORMS,
    STARTUP_MESSAGE,
)
from .coordinator import SmartmeterDataCoordinator
from .smartmeter import Smartmeter
from .smartmeter_data import SmartMeterConfigEntry, SmartMeterData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: SmartMeterConfigEntry) -> bool:
    """Set up this integration using UI."""
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.debug(STARTUP_MESSAGE)

    port    = entry.data.get(CONF_COM_PORT)
    key_hex = entry.data.get(CONF_KEY_HEX)

    data_interval = entry.options.get(OPT_DATA_INTERVAL, OPT_DATA_INTERVAL_VALUE)

    try:
        adapter  = Smartmeter(port, key_hex)
        obisdata = await hass.async_add_executor_job(adapter.read)
    except Exception as err:
        raise ConfigEntryNotReady from err

    device_number = obisdata.DeviceNumber.value or port
    device_info   = DeviceInfo(
        identifiers={(DOMAIN, device_number)},
        name=f"Smart Meter '{device_number}'",
    )

    coordinator = SmartmeterDataCoordinator(hass, adapter)
    coordinator.update_interval = timedelta(seconds=data_interval)
    coordinator.logger = _LOGGER

    await coordinator.async_config_entry_first_refresh()

    data = SmartMeterData(
        coordinator=coordinator,
        device_info=device_info,
        device_number=device_number,
    )
    entry.runtime_data = data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_options_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: SmartMeterConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_options_update_listener(
    hass: HomeAssistant, config_entry: SmartMeterConfigEntry
) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)
