from __future__ import annotations

from dataclasses import dataclass
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_CLIENT_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.device_registry import format_mac

from .api import BMWMotorradApiClient, TokenData
from .const import (
    CONF_API_HOST,
    CONF_COUNTRY,
    CONF_DEVICE_CODE_HOST,
    CONF_POLL_INTERVAL,
    CONF_TOKEN_HOST,
    CONF_VERIFY_SSL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import BMWMotorradCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class RuntimeData:
    client: BMWMotorradApiClient
    coordinator: BMWMotorradCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = async_get_clientsession(hass)
    client = BMWMotorradApiClient(
        session,
        client_id=entry.data[CONF_CLIENT_ID],
        api_host=entry.data[CONF_API_HOST],
        device_code_host=entry.data[CONF_DEVICE_CODE_HOST],
        token_host=entry.data[CONF_TOKEN_HOST],
        country=entry.data[CONF_COUNTRY],
        verify_ssl=entry.data[CONF_VERIFY_SSL],
    )
    if token_data := entry.data.get("token"):
        client.set_token(TokenData.from_token_response(token_data))
    coordinator = BMWMotorradCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = RuntimeData(client=client, coordinator=coordinator)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
