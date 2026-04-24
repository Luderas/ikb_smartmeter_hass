"""OBIS-Codes für den Kaifa MA309 (IKB Innsbruck).

OBIS steht für Object Identification System und ist ein standardisiertes
Adressierungsschema für Energiezählerwerte (IEC 62056-61).

Format der Codes hier: A.B.C.D.E.F als Punkt-getrennte Dezimalzahlen.
Der Kaifa MA309 überträgt genau diese Bytes im M-Bus-Frame.
"""


class Obis:
    """Sammlung aller relevanten OBIS-Codes für den Kaifa MA309."""

    @staticmethod
    def to_bytes(code: str) -> bytes:
        """Wandelt einen Punkt-getrennten OBIS-Code in Bytes um.
        
        Beispiel: "1.0.32.7.0.255" → b'\\x01\\x00\\x20\\x07\\x00\\xff'
        """
        return bytes(int(part) for part in code.split("."))

    # ------------------------------------------------------------------
    # Metadaten / Identifikation
    # ------------------------------------------------------------------

    Timestamp:           bytes = to_bytes("0.0.1.0.0.255")   # Zeitstempel des Zählers
    DeviceNumber:        bytes = to_bytes("0.0.96.1.0.255")  # Seriennummer (ASCII)
    LogicalDeviceNumber: bytes = to_bytes("0.0.42.0.0.255")  # COSEM-Gerätename

    # ------------------------------------------------------------------
    # Spannungen (Momentanwerte)
    # ------------------------------------------------------------------

    VoltageL1: bytes = to_bytes("1.0.32.7.0.255")  # Spannung Phase L1 [V]
    VoltageL2: bytes = to_bytes("1.0.52.7.0.255")  # Spannung Phase L2 [V]
    VoltageL3: bytes = to_bytes("1.0.72.7.0.255")  # Spannung Phase L3 [V]

    # ------------------------------------------------------------------
    # Ströme (Momentanwerte)
    # ------------------------------------------------------------------

    CurrentL1: bytes = to_bytes("1.0.31.7.0.255")  # Strom Phase L1 [A]
    CurrentL2: bytes = to_bytes("1.0.51.7.0.255")  # Strom Phase L2 [A]
    CurrentL3: bytes = to_bytes("1.0.71.7.0.255")  # Strom Phase L3 [A]

    # ------------------------------------------------------------------
    # Wirkleistung gesamt (Momentanwerte)
    # ------------------------------------------------------------------

    RealPowerIn:  bytes = to_bytes("1.0.1.7.0.255")  # Bezug gesamt  [W]
    RealPowerOut: bytes = to_bytes("1.0.2.7.0.255")  # Einspeisung gesamt [W]

    # ------------------------------------------------------------------
    # Wirkleistung je Phase (Momentanwerte) – MA309-spezifisch
    # ------------------------------------------------------------------

    RealPowerL1In:  bytes = to_bytes("1.0.21.7.0.255")  # L1 Bezug  [W]
    RealPowerL1Out: bytes = to_bytes("1.0.22.7.0.255")  # L1 Einspeisung [W]
    RealPowerL2In:  bytes = to_bytes("1.0.41.7.0.255")  # L2 Bezug  [W]
    RealPowerL2Out: bytes = to_bytes("1.0.42.7.0.255")  # L2 Einspeisung [W]
    RealPowerL3In:  bytes = to_bytes("1.0.61.7.0.255")  # L3 Bezug  [W]
    RealPowerL3Out: bytes = to_bytes("1.0.62.7.0.255")  # L3 Einspeisung [W]

    # ------------------------------------------------------------------
    # Blindleistung gesamt (Momentanwerte)
    # ------------------------------------------------------------------

    ReactivePowerPlus:  bytes = to_bytes("1.0.3.7.0.255")  # induktiv  [var]
    ReactivePowerMinus: bytes = to_bytes("1.0.4.7.0.255")  # kapazitiv [var]

    # ------------------------------------------------------------------
    # Wirkenergie-Zähler (kumuliert)
    # ------------------------------------------------------------------

    RealEnergyIn:  bytes = to_bytes("1.0.1.8.0.255")  # Bezug kumuliert    [Wh]
    RealEnergyOut: bytes = to_bytes("1.0.2.8.0.255")  # Einspeisung kumuliert [Wh]

    # ------------------------------------------------------------------
    # Blindenergie-Zähler (kumuliert)
    # ------------------------------------------------------------------

    ReactiveEnergyIn:  bytes = to_bytes("1.0.3.8.0.255")  # induktiv kumuliert  [varh]
    ReactiveEnergyOut: bytes = to_bytes("1.0.4.8.0.255")  # kapazitiv kumuliert [varh]

    # Quadranten Q1–Q4 (MA309-spezifisch)
    ReactiveEnergyQ1: bytes = to_bytes("1.0.5.8.0.255")  # Quadrant I   [varh]
    ReactiveEnergyQ2: bytes = to_bytes("1.0.6.8.0.255")  # Quadrant II  [varh]
    ReactiveEnergyQ3: bytes = to_bytes("1.0.7.8.0.255")  # Quadrant III [varh]
    ReactiveEnergyQ4: bytes = to_bytes("1.0.8.8.0.255")  # Quadrant IV  [varh]
