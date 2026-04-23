"""Description of all sensors for Kaifa MA309 (IKB)."""
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.helpers.entity import EntityCategory

SENSOR_DESCRIPTIONS: dict[str, SensorEntityDescription] = {
    # ------------------------------------------------------------------
    # Voltages
    # ------------------------------------------------------------------
    "VoltageL1": SensorEntityDescription(
        key="voltagel1",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        name="Voltage L1",
        icon="mdi:flash-triangle-outline",
        has_entity_name=True,
    ),
    "VoltageL2": SensorEntityDescription(
        key="voltagel2",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        name="Voltage L2",
        icon="mdi:flash-triangle-outline",
        has_entity_name=True,
    ),
    "VoltageL3": SensorEntityDescription(
        key="voltagel3",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        name="Voltage L3",
        icon="mdi:flash-triangle-outline",
        has_entity_name=True,
    ),
    # ------------------------------------------------------------------
    # Currents
    # ------------------------------------------------------------------
    "CurrentL1": SensorEntityDescription(
        key="currentl1",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        name="Current L1",
        icon="mdi:current-ac",
        has_entity_name=True,
    ),
    "CurrentL2": SensorEntityDescription(
        key="currentl2",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        name="Current L2",
        icon="mdi:current-ac",
        has_entity_name=True,
    ),
    "CurrentL3": SensorEntityDescription(
        key="currentl3",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        name="Current L3",
        icon="mdi:current-ac",
        has_entity_name=True,
    ),
    # ------------------------------------------------------------------
    # Total power
    # ------------------------------------------------------------------
    "RealPowerIn": SensorEntityDescription(
        key="realpowerin",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power in",
        icon="mdi:transmission-tower-export",
        has_entity_name=True,
    ),
    "RealPowerOut": SensorEntityDescription(
        key="realpowerout",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power out",
        icon="mdi:transmission-tower-import",
        has_entity_name=True,
    ),
    "RealPowerDelta": SensorEntityDescription(
        key="realpowerdelta",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power delta",
        icon="mdi:transmission-tower",
        has_entity_name=True,
    ),
    # ------------------------------------------------------------------
    # Per-phase power
    # ------------------------------------------------------------------
    "RealPowerL1In": SensorEntityDescription(
        key="realpowerl1in",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power L1 in",
        icon="mdi:transmission-tower-export",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    "RealPowerL1Out": SensorEntityDescription(
        key="realpowerl1out",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power L1 out",
        icon="mdi:transmission-tower-import",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    "RealPowerL2In": SensorEntityDescription(
        key="realpowerl2in",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power L2 in",
        icon="mdi:transmission-tower-export",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    "RealPowerL2Out": SensorEntityDescription(
        key="realpowerl2out",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power L2 out",
        icon="mdi:transmission-tower-import",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    "RealPowerL3In": SensorEntityDescription(
        key="realpowerl3in",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power L3 in",
        icon="mdi:transmission-tower-export",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    "RealPowerL3Out": SensorEntityDescription(
        key="realpowerl3out",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfPower.WATT,
        name="Real power L3 out",
        icon="mdi:transmission-tower-import",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    # ------------------------------------------------------------------
    # Reactive power
    # ------------------------------------------------------------------
    "ReactivePowerPlus": SensorEntityDescription(
        key="reactivepowerplus",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        name="Reactive power +",
        icon="mdi:sine-wave",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    "ReactivePowerMinus": SensorEntityDescription(
        key="reactivepowerminus",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement="var",
        name="Reactive power -",
        icon="mdi:sine-wave",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    # ------------------------------------------------------------------
    # Energy counters
    # ------------------------------------------------------------------
    "RealEnergyIn": SensorEntityDescription(
        key="realenergyin",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        name="Real energy in",
        icon="mdi:transmission-tower-export",
        has_entity_name=True,
    ),
    "RealEnergyOut": SensorEntityDescription(
        key="realenergyout",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        name="Real energy out",
        icon="mdi:transmission-tower-import",
        has_entity_name=True,
    ),
    "ReactiveEnergyIn": SensorEntityDescription(
        key="reactiveenergyin",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        name="Reactive energy in",
        icon="mdi:transmission-tower-export",
        has_entity_name=True,
    ),
    "ReactiveEnergyOut": SensorEntityDescription(
        key="reactiveenergyout",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        name="Reactive energy out",
        icon="mdi:transmission-tower-import",
        has_entity_name=True,
    ),
    "ReactiveEnergyQ1": SensorEntityDescription(
        key="reactiveenergyq1",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        name="Reactive energy Q1",
        icon="mdi:sine-wave",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    "ReactiveEnergyQ2": SensorEntityDescription(
        key="reactiveenergyq2",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        name="Reactive energy Q2",
        icon="mdi:sine-wave",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    "ReactiveEnergyQ3": SensorEntityDescription(
        key="reactiveenergyq3",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        name="Reactive energy Q3",
        icon="mdi:sine-wave",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
    "ReactiveEnergyQ4": SensorEntityDescription(
        key="reactiveenergyq4",
        state_class=SensorStateClass.TOTAL_INCREASING,
        native_unit_of_measurement="varh",
        name="Reactive energy Q4",
        icon="mdi:sine-wave",
        entity_category=EntityCategory.DIAGNOSTIC,
        has_entity_name=True,
    ),
}

DEFAULT_SENSOR = SensorEntityDescription(
    key="_",
    state_class=SensorStateClass.MEASUREMENT,
    entity_category=EntityCategory.DIAGNOSTIC,
)
