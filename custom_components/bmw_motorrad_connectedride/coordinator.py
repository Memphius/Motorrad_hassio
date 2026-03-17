from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BMWMotorradApiClient, BMWMotorradApiError, BMWMotorradAuthError
from .const import CONF_POLL_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BMWMotorradCoordinator(DataUpdateCoordinator[dict[str, object]]):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: BMWMotorradApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.options.get(CONF_POLL_INTERVAL, entry.data[CONF_POLL_INTERVAL])),
        )
        self.entry = entry
        self.client = client

    async def _async_update_data(self) -> dict[str, object]:
        try:
            bikes = await self.client.async_get_bikes()
        except BMWMotorradAuthError as err:
            self.entry.async_start_reauth(self.hass)
            raise UpdateFailed(f"Authentication failed: {err}") from err
        except BMWMotorradApiError as err:
            raise UpdateFailed(str(err)) from err
        return {bike.bike_id: bike for bike in bikes}
