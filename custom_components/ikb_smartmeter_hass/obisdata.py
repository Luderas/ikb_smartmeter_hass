"""Defines the OBIS data object for Kaifa MA309 (IKB)."""

from .constants import PhysicalUnits
from .decrypt import Decrypt
from .obisvalue import ObisValueBytes, ObisValueFloat

# All value names that are read from the meter
SUPPLIED_VALUES: list[str] = [
    "Timestamp",
    "DeviceNumber",
    "LogicalDeviceNumber",
    "VoltageL1",
    "VoltageL2",
    "VoltageL3",
    "CurrentL1",
    "CurrentL2",
    "CurrentL3",
    "RealPowerIn",
    "RealPowerOut",
    "RealPowerL1In",
    "RealPowerL1Out",
    "RealPowerL2In",
    "RealPowerL2Out",
    "RealPowerL3In",
    "RealPowerL3Out",
    "ReactivePowerPlus",
    "ReactivePowerMinus",
    "RealEnergyIn",
    "RealEnergyOut",
    "ReactiveEnergyIn",
    "ReactiveEnergyOut",
    "ReactiveEnergyQ1",
    "ReactiveEnergyQ2",
    "ReactiveEnergyQ3",
    "ReactiveEnergyQ4",
]


class ObisData:
    """Holds all OBIS data for a Kaifa MA309 (IKB) reading."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, dec: Decrypt) -> None:
        # Metadata
        self._timestamp:             ObisValueBytes = ObisValueBytes(b"")
        self._device_number:         ObisValueBytes = ObisValueBytes(b"")
        self._logical_device_number: ObisValueBytes = ObisValueBytes(b"")

        # Voltages
        self._voltage_l1: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.V)
        self._voltage_l2: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.V)
        self._voltage_l3: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.V)

        # Currents
        self._current_l1: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.A)
        self._current_l2: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.A)
        self._current_l3: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.A)

        # Power
        self._real_power_in:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)
        self._real_power_out: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)

        self._real_power_l1_in:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)
        self._real_power_l1_out: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)
        self._real_power_l2_in:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)
        self._real_power_l2_out: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)
        self._real_power_l3_in:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)
        self._real_power_l3_out: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.W)

        self._reactive_power_plus:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.var)
        self._reactive_power_minus: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.var)

        # Energy
        self._real_energy_in:      ObisValueFloat = ObisValueFloat(0, PhysicalUnits.Wh)
        self._real_energy_out:     ObisValueFloat = ObisValueFloat(0, PhysicalUnits.Wh)
        self._reactive_energy_in:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.varh)
        self._reactive_energy_out: ObisValueFloat = ObisValueFloat(0, PhysicalUnits.varh)
        self._reactive_energy_q1:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.varh)
        self._reactive_energy_q2:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.varh)
        self._reactive_energy_q3:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.varh)
        self._reactive_energy_q4:  ObisValueFloat = ObisValueFloat(0, PhysicalUnits.varh)

        # Populate from decrypted data
        for key in SUPPLIED_VALUES:
            val = dec.get_obis_value(key)
            if val is not None:
                setattr(self, key, val)

    # ------------------------------------------------------------------
    # Properties – Metadata
    # ------------------------------------------------------------------

    @property
    def Timestamp(self) -> ObisValueBytes:
        """Meter timestamp."""
        return self._timestamp

    @Timestamp.setter
    def Timestamp(self, v: ObisValueBytes) -> None:
        self._timestamp = v

    @property
    def DeviceNumber(self) -> ObisValueBytes:
        """The device (serial) number."""
        return self._device_number

    @DeviceNumber.setter
    def DeviceNumber(self, v: ObisValueBytes) -> None:
        self._device_number = v

    @property
    def LogicalDeviceNumber(self) -> ObisValueBytes:
        """The logical device number (COSEM name)."""
        return self._logical_device_number

    @LogicalDeviceNumber.setter
    def LogicalDeviceNumber(self, v: ObisValueBytes) -> None:
        self._logical_device_number = v

    # ------------------------------------------------------------------
    # Properties – Voltages
    # ------------------------------------------------------------------

    @property
    def VoltageL1(self) -> ObisValueFloat:
        return self._voltage_l1

    @VoltageL1.setter
    def VoltageL1(self, v: ObisValueFloat) -> None:
        self._voltage_l1 = v

    @property
    def VoltageL2(self) -> ObisValueFloat:
        return self._voltage_l2

    @VoltageL2.setter
    def VoltageL2(self, v: ObisValueFloat) -> None:
        self._voltage_l2 = v

    @property
    def VoltageL3(self) -> ObisValueFloat:
        return self._voltage_l3

    @VoltageL3.setter
    def VoltageL3(self, v: ObisValueFloat) -> None:
        self._voltage_l3 = v

    # ------------------------------------------------------------------
    # Properties – Currents
    # ------------------------------------------------------------------

    @property
    def CurrentL1(self) -> ObisValueFloat:
        return self._current_l1

    @CurrentL1.setter
    def CurrentL1(self, v: ObisValueFloat) -> None:
        self._current_l1 = v

    @property
    def CurrentL2(self) -> ObisValueFloat:
        return self._current_l2

    @CurrentL2.setter
    def CurrentL2(self, v: ObisValueFloat) -> None:
        self._current_l2 = v

    @property
    def CurrentL3(self) -> ObisValueFloat:
        return self._current_l3

    @CurrentL3.setter
    def CurrentL3(self, v: ObisValueFloat) -> None:
        self._current_l3 = v

    # ------------------------------------------------------------------
    # Properties – Power
    # ------------------------------------------------------------------

    @property
    def RealPowerIn(self) -> ObisValueFloat:
        return self._real_power_in

    @RealPowerIn.setter
    def RealPowerIn(self, v: ObisValueFloat) -> None:
        self._real_power_in = v

    @property
    def RealPowerOut(self) -> ObisValueFloat:
        return self._real_power_out

    @RealPowerOut.setter
    def RealPowerOut(self, v: ObisValueFloat) -> None:
        self._real_power_out = v

    @property
    def RealPowerDelta(self) -> ObisValueFloat:
        """Difference between taken and given power (calculated)."""
        return self._real_power_in - self._real_power_out

    @property
    def RealPowerL1In(self) -> ObisValueFloat:
        return self._real_power_l1_in

    @RealPowerL1In.setter
    def RealPowerL1In(self, v: ObisValueFloat) -> None:
        self._real_power_l1_in = v

    @property
    def RealPowerL1Out(self) -> ObisValueFloat:
        return self._real_power_l1_out

    @RealPowerL1Out.setter
    def RealPowerL1Out(self, v: ObisValueFloat) -> None:
        self._real_power_l1_out = v

    @property
    def RealPowerL2In(self) -> ObisValueFloat:
        return self._real_power_l2_in

    @RealPowerL2In.setter
    def RealPowerL2In(self, v: ObisValueFloat) -> None:
        self._real_power_l2_in = v

    @property
    def RealPowerL2Out(self) -> ObisValueFloat:
        return self._real_power_l2_out

    @RealPowerL2Out.setter
    def RealPowerL2Out(self, v: ObisValueFloat) -> None:
        self._real_power_l2_out = v

    @property
    def RealPowerL3In(self) -> ObisValueFloat:
        return self._real_power_l3_in

    @RealPowerL3In.setter
    def RealPowerL3In(self, v: ObisValueFloat) -> None:
        self._real_power_l3_in = v

    @property
    def RealPowerL3Out(self) -> ObisValueFloat:
        return self._real_power_l3_out

    @RealPowerL3Out.setter
    def RealPowerL3Out(self, v: ObisValueFloat) -> None:
        self._real_power_l3_out = v

    @property
    def ReactivePowerPlus(self) -> ObisValueFloat:
        return self._reactive_power_plus

    @ReactivePowerPlus.setter
    def ReactivePowerPlus(self, v: ObisValueFloat) -> None:
        self._reactive_power_plus = v

    @property
    def ReactivePowerMinus(self) -> ObisValueFloat:
        return self._reactive_power_minus

    @ReactivePowerMinus.setter
    def ReactivePowerMinus(self, v: ObisValueFloat) -> None:
        self._reactive_power_minus = v

    # ------------------------------------------------------------------
    # Properties – Energy
    # ------------------------------------------------------------------

    @property
    def RealEnergyIn(self) -> ObisValueFloat:
        return self._real_energy_in

    @RealEnergyIn.setter
    def RealEnergyIn(self, v: ObisValueFloat) -> None:
        self._real_energy_in = v

    @property
    def RealEnergyOut(self) -> ObisValueFloat:
        return self._real_energy_out

    @RealEnergyOut.setter
    def RealEnergyOut(self, v: ObisValueFloat) -> None:
        self._real_energy_out = v

    @property
    def ReactiveEnergyIn(self) -> ObisValueFloat:
        return self._reactive_energy_in

    @ReactiveEnergyIn.setter
    def ReactiveEnergyIn(self, v: ObisValueFloat) -> None:
        self._reactive_energy_in = v

    @property
    def ReactiveEnergyOut(self) -> ObisValueFloat:
        return self._reactive_energy_out

    @ReactiveEnergyOut.setter
    def ReactiveEnergyOut(self, v: ObisValueFloat) -> None:
        self._reactive_energy_out = v

    @property
    def ReactiveEnergyQ1(self) -> ObisValueFloat:
        return self._reactive_energy_q1

    @ReactiveEnergyQ1.setter
    def ReactiveEnergyQ1(self, v: ObisValueFloat) -> None:
        self._reactive_energy_q1 = v

    @property
    def ReactiveEnergyQ2(self) -> ObisValueFloat:
        return self._reactive_energy_q2

    @ReactiveEnergyQ2.setter
    def ReactiveEnergyQ2(self, v: ObisValueFloat) -> None:
        self._reactive_energy_q2 = v

    @property
    def ReactiveEnergyQ3(self) -> ObisValueFloat:
        return self._reactive_energy_q3

    @ReactiveEnergyQ3.setter
    def ReactiveEnergyQ3(self, v: ObisValueFloat) -> None:
        self._reactive_energy_q3 = v

    @property
    def ReactiveEnergyQ4(self) -> ObisValueFloat:
        return self._reactive_energy_q4

    @ReactiveEnergyQ4.setter
    def ReactiveEnergyQ4(self, v: ObisValueFloat) -> None:
        self._reactive_energy_q4 = v
