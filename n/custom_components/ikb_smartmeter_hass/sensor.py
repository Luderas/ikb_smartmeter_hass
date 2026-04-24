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



# Only expose sensor IDs that have a description entry
_SENSOR_IDS = [sid for sid in SUPPLIED_VALUES if sid in SENSOR_DESCRIPTIONS]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: SmartMeterConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor platform."""
    smartmeter_data: SmartMeterData = entry.runtime_data
    coordinator: SmartmeterDataCoordinator = smartmeter_data.coordinator
    device_info: DeviceInfo = smartmeter_data.device_info
    device_number: str = smartmeter_data.device_number

    entities = [
        SmartmeterSensor(coordinator, device_info, device_number, sensor_id)
        for sensor_id in _SENSOR_IDS
    ]
    async_add_entities(entities)


class SmartmeterSensor(CoordinatorEntity, SensorEntity):
    """Entity representing a single OBIS value from the Kaifa MA309."""

    def __init__(
        self,
        coordinator: SmartmeterDataCoordinator,
        device_info: DeviceInfo,
        device_number: str,
        sensor_id: str,
    ) -> None:
        """Initialisiert den Sensor.

        Args:
            coordinator:   Datenquelle (aktualisiert periodisch)
            device_info:   HA-Geräteinformationen (für Gerätekarte)
            device_number: Seriennummer des Zählers (für unique_id)
            sensor_id:     OBIS-Attributname, z. B. "VoltageL1"
        """
        super().__init__(coordinator)
        self._attr_unique_id    = f"{DOMAIN}_{device_number}_{sensor_id}"
        self._attr_device_info  = device_info
        self.entity_description = SENSOR_DESCRIPTIONS.get(sensor_id, DEFAULT_SENSOR)
        self._sensor_id         = sensor_id
        self._previous_value    = None
        self.my_coordinator     = coordinator

    @property
    def native_value(self) -> float | str | None:
        """Gibt den aktuellen Messwert zurück.

        Bei fehlenden Daten (Coordinator noch nicht bereit) wird
        ConfigEntryNotReady ausgelöst, damit HA die Entität als
        „unavailable" markiert.
        """
        obisdata: ObisData | None = self.my_coordinator.data
        if obisdata is None:
            raise ConfigEntryNotReady("Coordinator hat noch keine Daten.")

        try:
            obis_value: ObisValueFloat | ObisValueBytes | None = getattr(
                obisdata, self._sensor_id, None
            )
            if obis_value is None:
                _LOGGER.debug("obisdata.%s is None.", self._sensor_id)
                raise ConfigEntryNotReady(f"Kein Wert für '{self._sensor_id}'.")

            new_value = obis_value.value
            self._previous_value = new_value
            return new_value

        except SmartmeterException as exc:
            _LOGGER.debug(
                "native_value error for %s: %s", self._sensor_id, exc, exc_info=True
            )
            raise ConfigEntryNotReady() from exc

        except ConfigEntryNotReady:
            raise

        except Exception as exc:
            _LOGGER.warning(
                "native_value generic error for %s: %s",
                self._sensor_id, exc, exc_info=True,
            )
            raise ConfigEntryNotReady() from exc

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Disable diagnostic entities by default."""
        return self.entity_description.entity_category != EntityCategory.DIAGNOSTIC
