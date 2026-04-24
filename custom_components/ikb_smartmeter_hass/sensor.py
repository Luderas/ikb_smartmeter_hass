"""Sensor-Plattform für den IKB Smart Meter (Kaifa MA309)."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SmartmeterDataCoordinator
from .exceptions import SmartmeterException
from .obisdata import ObisData, SUPPLIED_VALUES
from .obisvalue import ObisValueBytes, ObisValueFloat
from .sensor_descriptions import DEFAULT_SENSOR, SENSOR_DESCRIPTIONS
from .smartmeter_data import SmartMeterConfigEntry, SmartMeterData

_LOGGER = logging.getLogger(__name__)

# Nur ein paralleles Update, da der serielle Port ein Engpass ist
PARALLEL_UPDATES = 1

# Nur Sensor-IDs exposieren, für die eine Beschreibung vorhanden ist
_SENSOR_IDS = [sid for sid in SUPPLIED_VALUES if sid in SENSOR_DESCRIPTIONS]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartMeterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Richtet alle Sensor-Entitäten für das Config-Entry ein."""
    data: SmartMeterData = entry.runtime_data

    entities = [
        SmartmeterSensor(
            coordinator   = data.coordinator,
            device_info   = data.device_info,
            device_number = data.device_number,
            sensor_id     = sensor_id,
        )
        for sensor_id in _SENSOR_IDS
    ]
    async_add_entities(entities)


class SmartmeterSensor(CoordinatorEntity[SmartmeterDataCoordinator], SensorEntity):
    """Repräsentiert einen einzelnen OBIS-Messwert des Kaifa MA309 als HA-Entität."""

    def __init__(
        self,
        coordinator:   SmartmeterDataCoordinator,
        device_info:   DeviceInfo,
        device_number: str,
        sensor_id:     str,
    ) -> None:
        """Initialisiert den Sensor.

        Args:
            coordinator:   Datenquelle (aktualisiert periodisch)
            device_info:   HA-Geräteinformationen (für Gerätekarte)
            device_number: Seriennummer des Zählers (für unique_id)
            sensor_id:     OBIS-Attributname, z. B. "VoltageL1"
        """
        super().__init__(coordinator)

        self._sensor_id = sensor_id

        # Stabile unique_id: Domain + Seriennummer + Sensor-Name
        self._attr_unique_id    = f"{DOMAIN}_{device_number}_{sensor_id}"
        self._attr_device_info  = device_info
        self.entity_description = SENSOR_DESCRIPTIONS.get(sensor_id, DEFAULT_SENSOR)

    @property
    def native_value(self) -> float | str | None:
        """Gibt den aktuellen Messwert zurück.

        Bei fehlenden Daten (Coordinator noch nicht bereit) wird
        ConfigEntryNotReady ausgelöst, damit HA die Entität als
        „unavailable" markiert.
        """
        obisdata: ObisData | None = self.coordinator.data
        if obisdata is None:
            raise ConfigEntryNotReady("Coordinator hat noch keine Daten.")

        try:
            obis_value: ObisValueFloat | ObisValueBytes | None = getattr(
                obisdata, self._sensor_id, None
            )
            if obis_value is None:
                _LOGGER.debug("obisdata.%s ist None.", self._sensor_id)
                raise ConfigEntryNotReady(f"Kein Wert für '{self._sensor_id}'.")

            return obis_value.value

        except SmartmeterException as exc:
            _LOGGER.debug(
                "Fehler beim Lesen von %s: %s", self._sensor_id, exc, exc_info=True
            )
            raise ConfigEntryNotReady() from exc

        except ConfigEntryNotReady:
            raise

        except Exception as exc:
            _LOGGER.warning(
                "Unerwarteter Fehler beim Lesen von %s: %s",
                self._sensor_id, exc, exc_info=True,
            )
            raise ConfigEntryNotReady() from exc

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Diagnose-Entitäten sind standardmäßig deaktiviert."""
        return self.entity_description.entity_category != EntityCategory.DIAGNOSTIC
