"""Defines the OBIS objects for Kaifa MA309 (IKB)."""


class Obis:
    """Defines the OBIS object."""

    @staticmethod
    def to_bytes(code: str) -> bytes:
        """Returns the code as byte array."""
        return bytes([int(a) for a in code.split(".")])

    # -----------------------------------------------------------------------
    # Active OBIS codes for Kaifa MA309 / IKB
    # Format used here: dot-separated, matching the MA309 frame output
    # -----------------------------------------------------------------------

    # Timestamp / metadata
    Timestamp:           bytes = to_bytes("0.0.1.0.0.255")
    DeviceNumber:        bytes = to_bytes("0.0.96.1.0.255")
    LogicalDeviceNumber: bytes = to_bytes("0.0.42.0.0.255")

    # Voltages
    VoltageL1: bytes = to_bytes("1.0.32.7.0.255")
    VoltageL2: bytes = to_bytes("1.0.52.7.0.255")
    VoltageL3: bytes = to_bytes("1.0.72.7.0.255")

    # Currents
    CurrentL1: bytes = to_bytes("1.0.31.7.0.255")
    CurrentL2: bytes = to_bytes("1.0.51.7.0.255")
    CurrentL3: bytes = to_bytes("1.0.71.7.0.255")

    # Instantaneous power
    RealPowerIn:  bytes = to_bytes("1.0.1.7.0.255")   # Active power import  [W]
    RealPowerOut: bytes = to_bytes("1.0.2.7.0.255")   # Active power export  [W]

    # Per-phase power (MA309 provides these)
    RealPowerL1In:  bytes = to_bytes("1.0.21.7.0.255")
    RealPowerL1Out: bytes = to_bytes("1.0.22.7.0.255")
    RealPowerL2In:  bytes = to_bytes("1.0.41.7.0.255")
    RealPowerL2Out: bytes = to_bytes("1.0.42.7.0.255")
    RealPowerL3In:  bytes = to_bytes("1.0.61.7.0.255")
    RealPowerL3Out: bytes = to_bytes("1.0.62.7.0.255")

    # Reactive power
    ReactivePowerPlus:  bytes = to_bytes("1.0.3.7.0.255")   # +var
    ReactivePowerMinus: bytes = to_bytes("1.0.4.7.0.255")   # -var

    # Energy counters
    RealEnergyIn:      bytes = to_bytes("1.0.1.8.0.255")   # +Wh
    RealEnergyOut:     bytes = to_bytes("1.0.2.8.0.255")   # -Wh
    ReactiveEnergyIn:  bytes = to_bytes("1.0.3.8.0.255")   # +varh
    ReactiveEnergyOut: bytes = to_bytes("1.0.4.8.0.255")   # -varh

    # Reactive energy quadrants (MA309 specific)
    ReactiveEnergyQ1: bytes = to_bytes("1.0.5.8.0.255")
    ReactiveEnergyQ2: bytes = to_bytes("1.0.6.8.0.255")
    ReactiveEnergyQ3: bytes = to_bytes("1.0.7.8.0.255")
    ReactiveEnergyQ4: bytes = to_bytes("1.0.8.8.0.255")

    # -----------------------------------------------------------------------
    # Original OBIS codes from NECH2004/smartmeter_austria_energy
    # (TINETZ / EVN / SALZBURGNETZ - kept for reference, not used)
    # -----------------------------------------------------------------------
    # VoltageL1: bytes = to_bytes("01.0.32.7.0.255")
    # VoltageL2: bytes = to_bytes("01.0.52.7.0.255")
    # VoltageL3: bytes = to_bytes("01.0.72.7.0.255")
    # CurrentL1: bytes = to_bytes("1.0.31.7.0.255")
    # CurrentL2: bytes = to_bytes("1.0.51.7.0.255")
    # CurrentL3: bytes = to_bytes("1.0.71.7.0.255")
    # RealPowerIn:  bytes = to_bytes("1.0.1.7.0.255")
    # RealPowerOut: bytes = to_bytes("1.0.2.7.0.255")
    # RealEnergyIn:      bytes = to_bytes("1.0.1.8.0.255")
    # RealEnergyOut:     bytes = to_bytes("1.0.2.8.0.255")
    # ReactiveEnergyIn:  bytes = to_bytes("1.0.3.8.0.255")
    # ReactiveEnergyOut: bytes = to_bytes("1.0.4.8.0.255")
    # Factor:            bytes = to_bytes("01.0.13.7.0.255")
    # DeviceNumber:      bytes = to_bytes("0.0.96.1.0.255")
    # LogicalDeviceNumber: bytes = to_bytes("0.0.42.0.0.255")
