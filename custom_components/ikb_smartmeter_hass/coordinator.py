"""DataUpdateCoordinator für den Kaifa MA309 (IKB)."""
from __future__ import annotations

import asyncio
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN, OPT_DATA_INTERVAL_VALUE
from .exceptions import (
    SmartmeterException,
    SmartmeterSerialException,
    SmartmeterTimeoutException,
)
from .obisdata import ObisData
from .smartmeter import Smartmeter

_LOGGER = logging.getLogger(__name__)

# Wartezeit nach einem Fehler, bevor der nächste Update-Versuch stattfindet
_RETRY_DELAY_TRANSIENT_S = 10   # bei Timeout / seriellen Fehlern
_RETRY_DELAY_GENERIC_S   = 30   # bei unbekannten Fehlern


class SmartmeterDataCoordinator(DataUpdateCoordinator[ObisData]):
    """Ruft periodisch Messdaten vom Kaifa MA309 über den seriellen Adapter ab.

    Fehlerbehandlung:
    - Timeout / serielle Fehler → kurze Pause, dann UpdateFailed
    - Unbekannte Fehler         → längere Pause, dann UpdateFailed
    In beiden Fällen markiert HA die Entitäten als „unavailable", bis der
    nächste erfolgreiche Update stattfindet.
    """

    def __init__(self, hass: HomeAssistant, adapter: Smartmeter) -> None:
        """Initialisiert den Coordinator.

        Args:
            hass:    Home Assistant Instanz
            adapter: Konfigurierter Smartmeter-Adapter (Port + Schlüssel)
        """
        self.adapter: Smartmeter = adapter

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=OPT_DATA_INTERVAL_VALUE),
        )

    async def _async_update_data(self) -> ObisData:
        """Liest einen Messrahmen vom Zähler (wird vom Coordinator-Framework aufgerufen).

        Returns:
            ObisData mit den aktuellen Messwerten.

        Raises:
            UpdateFailed: Bei allen Fehlertypen (nach optionaler Pause).
        """
        try:
            obisdata = await self.hass.async_add_executor_job(self.adapter.read)
            self.last_update_success = True
            return obisdata

        except SmartmeterTimeoutException as exc:
            _LOGGER.warning("Smartmeter Timeout: %s", exc, exc_info=True)
            self.last_update_success = False
            await asyncio.sleep(_RETRY_DELAY_TRANSIENT_S)
            raise UpdateFailed("Timeout beim Lesen des Smartmeters.") from exc

        except SmartmeterSerialException as exc:
            _LOGGER.warning("Smartmeter serieller Fehler: %s", exc, exc_info=True)
            self.last_update_success = False
            await asyncio.sleep(_RETRY_DELAY_TRANSIENT_S)
            raise UpdateFailed("Serieller Fehler beim Lesen des Smartmeters.") from exc

        except SmartmeterException as exc:
            _LOGGER.warning("Smartmeter Fehler: %s", exc, exc_info=True)
            self.last_update_success = False
            await asyncio.sleep(_RETRY_DELAY_TRANSIENT_S)
            raise UpdateFailed("Fehler beim Lesen des Smartmeters.") from exc

        except Exception as exc:
            _LOGGER.error("Unerwarteter Fehler beim Smartmeter-Update: %s", exc, exc_info=True)
            self.last_update_success = False
            await asyncio.sleep(_RETRY_DELAY_GENERIC_S)
            raise UpdateFailed("Unerwarteter Fehler beim Smartmeter-Update.") from exc
