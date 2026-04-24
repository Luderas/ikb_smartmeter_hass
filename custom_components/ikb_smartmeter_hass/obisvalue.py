"""Wert-Objekte für OBIS-Messdaten."""

import math

from .constants import PhysicalUnits


class ObisValueFloat:
    """Numerischer OBIS-Messwert mit Skalierung und physikalischer Einheit.
    
    Der tatsächliche Wert ergibt sich aus:  value = raw_value × 10^scale
    
    Beispiel: raw_value=2304, scale=-1  →  value=230.4 V
    """

    def __init__(
        self,
        raw_value: float,
        unit: PhysicalUnits = PhysicalUnits(0),
        scale: int = 0,
    ) -> None:
        self._raw_value = raw_value
        self._scale     = scale
        self._unit      = unit

    # ------------------------------------------------------------------
    # Arithmetik – nur bei gleicher Einheit sinnvoll
    # ------------------------------------------------------------------

    def __add__(self, other: "ObisValueFloat") -> "ObisValueFloat":
        """Addition zweier Werte gleicher Einheit."""
        if self._unit == other._unit:
            return ObisValueFloat(self.value + other.value, self._unit)
        return ObisValueFloat(math.nan)

    def __sub__(self, other: "ObisValueFloat") -> "ObisValueFloat":
        """Subtraktion zweier Werte gleicher Einheit."""
        if self._unit == other._unit:
            return ObisValueFloat(self.value - other.value, self._unit)
        return ObisValueFloat(math.nan)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def raw_value(self) -> float:
        """Rohwert direkt aus dem M-Bus-Frame (unskaliert)."""
        return self._raw_value

    @property
    def scale(self) -> int:
        """Skalierungsexponent (Exponent zur Basis 10)."""
        return self._scale

    @property
    def unit(self) -> PhysicalUnits:
        """Physikalische Einheit des Messwertes."""
        return self._unit

    @property
    def value(self) -> float:
        """Skalierter Messwert in der angegebenen Einheit."""
        return self._raw_value * (10 ** self._scale)

    @property
    def value_string(self) -> str:
        """Messwert als formatierter String inkl. Einheit, z. B. '230.4 V'."""
        return f"{self.value} {self._unit.name}"


class ObisValueBytes:
    """Bytebasierter OBIS-Wert (z. B. Gerätenummer, Zeitstempel).
    
    Wird für Felder verwendet, die keine numerischen Messwerte darstellen,
    sondern Bezeichner oder Zeitangaben als ASCII/Byte-Sequenz liefern.
    """

    def __init__(self, raw_value: bytes) -> None:
        self._raw_value = raw_value

    @property
    def raw_value(self) -> bytes:
        """Rohbytes direkt aus dem M-Bus-Frame."""
        return self._raw_value

    @property
    def value(self) -> str:
        """Decoded ASCII-String, Null-Bytes werden entfernt."""
        return self._raw_value.decode("ascii", errors="replace").strip("\x00")
