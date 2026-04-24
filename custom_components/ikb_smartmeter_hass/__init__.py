"""IKB Smart Meter Integration für Home Assistant (Kaifa MA309)."""

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
    OPT_DATA_INTERVAL_DEFAULT,
    PLATFORMS,
    STARTUP_MESSAGE,
)
from .coordinator import SmartmeterDataCoordinator
from .smartmeter import Smartmeter
from .smartmeter_data import SmartMeterConfigEntry, SmartMeterData

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: SmartMeterConfigEntry) -> bool:
    """Richtet die Integration beim Laden eines Config-Entry ein.

    Ablauf:
    1. Erstverbindung zum Zähler herstellen und Gerätenummer auslesen
    2. DeviceInfo aufbauen
    3. Coordinator initialisieren und ersten Refresh durchführen
    4. Plattformen (Sensor) einrichten
    5. Options-Listener registrieren
    """
    if hass.data.get(DOMAIN) is None:
        hass.data.setdefault(DOMAIN, {})
        _LOGGER.info(STARTUP_MESSAGE)

    port    = entry.data[CONF_COM_PORT]
    key_hex = entry.data[CONF_KEY_HEX]

    # Update-Intervall aus den Options lesen (Fallback auf Default)
    data_interval = entry.options.get(OPT_DATA_INTERVAL, OPT_DATA_INTERVAL_DEFAULT)

    # Erstverbindung – schlägt fehl → ConfigEntryNotReady → HA versucht es später erneut
    try:
        adapter  = Smartmeter(port, key_hex)
        obisdata = await hass.async_add_executor_job(adapter.read)
    except Exception as exc:
        raise ConfigEntryNotReady(
            f"Verbindung zu Smartmeter auf Port '{port}' fehlgeschlagen."
        ) from exc

    # Gerätenummer als eindeutigen Identifier verwenden; Port als Fallback
    device_number = obisdata.DeviceNumber.value or port

    device_info = DeviceInfo(
        identifiers={(DOMAIN, device_number)},
        name=f"IKB Smart Meter '{device_number}'",
        manufacturer="Kaifa",
        model="MA309",
    )

    # Coordinator aufbauen und ersten Refresh ausführen
    coordinator = SmartmeterDataCoordinator(hass, adapter)
    coordinator.update_interval = timedelta(seconds=data_interval)
    await coordinator.async_config_entry_first_refresh()

    # Laufzeitdaten im Entry speichern
    entry.runtime_data = SmartMeterData(
        coordinator=coordinator,
        device_info=device_info,
        device_number=device_number,
    )

    # Sensor-Plattform einrichten
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Options-Listener: bei Änderung des Update-Intervalls Entry neu laden
    entry.async_on_unload(entry.add_update_listener(_async_options_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: SmartMeterConfigEntry) -> bool:
    """Entfernt alle zur Integration gehörenden Entitäten und Dienste."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_options_update_listener(
    hass: HomeAssistant, entry: SmartMeterConfigEntry
) -> None:
    """Wird aufgerufen, wenn der Nutzer die Options (Update-Intervall) ändert.

    Lädt das Config-Entry neu, damit der neue Wert übernommen wird.
    """
    _LOGGER.debug("Options geändert – lade Entry '%s' neu.", entry.entry_id)
    await hass.config_entries.async_reload(entry.entry_id)
