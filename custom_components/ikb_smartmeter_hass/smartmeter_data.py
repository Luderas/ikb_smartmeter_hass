"""Laufzeitdaten eines Config-Entry für den IKB Smart Meter."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .coordinator import SmartmeterDataCoordinator


@dataclass
class SmartMeterData:
    """Hält alle Laufzeitdaten, die einem Config-Entry zugeordnet sind.

    Wird in entry.runtime_data gespeichert und von allen Plattformen
    (Sensor, …) verwendet, um auf Coordinator und Geräteinformationen
    zuzugreifen.
    """

    coordinator:   SmartmeterDataCoordinator
    device_info:   DeviceInfo
    device_number: str


# Typalias für Config-Entries mit SmartMeterData als Runtime-Daten.
# Der Suffix 'ConfigEntry' ist HA-Konvention für diesen Typalias.
type SmartMeterConfigEntry = ConfigEntry[SmartMeterData]
