from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_CLIENT_ID
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BMWMotorradApiClient, BMWMotorradAuthError
from .const import (
    CONF_API_HOST,
    CONF_AUTH_HOST,
    CONF_COUNTRY,
    CONF_POLL_INTERVAL,
    CONF_VERIFY_SSL,
    DEFAULT_API_HOST,
    DEFAULT_AUTH_HOST,
    DEFAULT_COUNTRY,
    DEFAULT_POLL_INTERVAL,
    DOMAIN,
)


class BMWMotorradConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    def __init__(self) -> None:
        self._user_input: dict[str, Any] | None = None
        self._device_code: str | None = None
        self._verification_uri: str | None = None
        self._verification_uri_complete: str | None = None
        self._user_code: str | None = None
        self._code_verifier: str | None = None

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._user_input = user_input
            await self.async_set_unique_id(user_input[CONF_CLIENT_ID])
            self._abort_if_unique_id_configured()

            client = BMWMotorradApiClient(
                async_get_clientsession(self.hass),
                client_id=user_input[CONF_CLIENT_ID],
                api_host=user_input[CONF_API_HOST],
                auth_host=user_input[CONF_AUTH_HOST],
                country=user_input[CONF_COUNTRY],
                verify_ssl=user_input[CONF_VERIFY_SSL],
            )

            try:
                code = await client.async_request_device_code()
            except BMWMotorradAuthError:
                errors["base"] = "cannot_connect"
            else:
                self._device_code = code.device_code
                self._verification_uri = code.verification_uri
                self._verification_uri_complete = code.verification_uri_complete
                self._user_code = code.user_code
                self._code_verifier = code.code_verifier
                return await self.async_step_authorize()

        schema = vol.Schema(
            {
                vol.Required(CONF_CLIENT_ID): str,
                vol.Required(CONF_COUNTRY, default=DEFAULT_COUNTRY): str,
                vol.Required(CONF_API_HOST, default=DEFAULT_API_HOST): str,
                vol.Required(CONF_AUTH_HOST, default=DEFAULT_AUTH_HOST): str,
                vol.Required(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
                vol.Required(CONF_VERIFY_SSL, default=True): bool,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_authorize(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        placeholders = {
            "verification_uri": self._verification_uri or "",
            "verification_uri_complete": self._verification_uri_complete or "",
            "user_code": self._user_code or "",
        }

        if user_input is not None and self._user_input and self._device_code and self._code_verifier:
            client = BMWMotorradApiClient(
                async_get_clientsession(self.hass),
                client_id=self._user_input[CONF_CLIENT_ID],
                api_host=self._user_input[CONF_API_HOST],
                auth_host=self._user_input[CONF_AUTH_HOST],
                country=self._user_input[CONF_COUNTRY],
                verify_ssl=self._user_input[CONF_VERIFY_SSL],
            )
            try:
                token = await client.async_exchange_device_code(
                    self._device_code,
                    self._code_verifier,
                )
                await client.async_get_bikes()
            except BMWMotorradAuthError:
                errors["base"] = "authorize_failed"
            else:
                data = dict(self._user_input)
                data["token"] = token.as_storage_dict()
                return self.async_create_entry(title="BMW Motorrad ConnectedRide", data=data)

        return self.async_show_form(
            step_id="authorize",
            data_schema=vol.Schema({}),
            errors=errors,
            description_placeholders=placeholders,
        )

    async def async_step_reauth(self, entry_data: dict[str, Any]) -> FlowResult:
        self._user_input = dict(entry_data)
        return await self.async_step_user(self._user_input)
