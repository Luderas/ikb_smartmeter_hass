"""The Smartmeter data coordinator."""
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


class SmartmeterDataCoordinator(DataUpdateCoordinator[ObisData]):
    """Fetches data from the Kaifa MA309 via serial."""

    def __init__(self, hass: HomeAssistant, adapter: Smartmeter) -> None:
        """Initialize."""
        self.adapter: Smartmeter = adapter

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=OPT_DATA_INTERVAL_VALUE),
        )

    async def _async_update_data(self) -> ObisData:
        """Update data over the USB device."""
        try:
            self.last_update_success = True
            obisdata = await self.hass.async_add_executor_job(self.adapter.read)
            return obisdata

        except SmartmeterTimeoutException as exc:
            self.logger.warning(
                "smartmeter.read() timeout error. %s", exc, exc_info=True
            )
            self.last_update_success = False
            await asyncio.sleep(10)
            raise UpdateFailed() from exc

        except SmartmeterSerialException as exc:
            self.logger.warning(
                "smartmeter.read() serial exception. %s", exc, exc_info=True
            )
            self.last_update_success = False
            await asyncio.sleep(10)
            raise UpdateFailed() from exc

        except SmartmeterException as exc:
            self.logger.warning(
                "smartmeter.read() smartmeter exception. %s", exc, exc_info=True
            )
            self.last_update_success = False
            await asyncio.sleep(10)
            raise UpdateFailed() from exc

        except Exception as exc:
            self.logger.error(
                "smartmeter.read() unexpected exception. %s", exc, exc_info=True
            )
            self.last_update_success = False
            await asyncio.sleep(30)
            raise UpdateFailed() from exc
