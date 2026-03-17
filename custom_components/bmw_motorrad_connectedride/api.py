from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import logging
from typing import Any

import aiohttp

from .const import BIKES_ENDPOINT_TMPL, DEVICE_CODE_ENDPOINT, SCOPES, TOKEN_ENDPOINT
from .models import BikeData

_LOGGER = logging.getLogger(__name__)


class BMWMotorradApiError(Exception):
    """Base API error."""


class BMWMotorradAuthError(BMWMotorradApiError):
    """Authentication failure."""


@dataclass(slots=True)
class DeviceCodeData:
    device_code: str
    user_code: str
    verification_uri: str
    expires_in: int
    interval: int


@dataclass(slots=True)
class TokenData:
    access_token: str
    refresh_token: str | None
    id_token: str | None
    expires_at: datetime

    @classmethod
    def from_token_response(cls, data: dict[str, Any]) -> "TokenData":
        expires_in = int(data.get("expires_in", 3600))
        return cls(
            access_token=data["access_token"],
            refresh_token=data.get("refresh_token"),
            id_token=data.get("id_token"),
            expires_at=datetime.now(tz=UTC) + timedelta(seconds=expires_in - 60),
        )


class BMWMotorradApiClient:
    """Minimal API client.

    Notes:
    - The device-code endpoints are taken from BMW CarData documentation.
    - The Motorrad data endpoint is based on the ConnectedRide endpoint provided by the user.
    - If BMW uses a different audience/token host for Motorrad in your account, adapt
      `device_code_host` / `token_host` / scopes accordingly.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        *,
        client_id: str,
        api_host: str,
        device_code_host: str,
        token_host: str,
        country: str,
        verify_ssl: bool,
    ) -> None:
        self._session = session
        self._client_id = client_id
        self._api_host = api_host.rstrip("/")
        self._device_code_host = device_code_host.rstrip("/")
        self._token_host = token_host.rstrip("/")
        self._country = country
        self._verify_ssl = verify_ssl
        self._token: TokenData | None = None

    @property
    def token(self) -> TokenData | None:
        return self._token

    def set_token(self, token: TokenData | None) -> None:
        self._token = token

    async def async_request_device_code(self) -> DeviceCodeData:
        url = f"{self._device_code_host}{DEVICE_CODE_ENDPOINT}"
        payload = {
            "client_id": self._client_id,
            "scope": " ".join(SCOPES),
        }
        async with self._session.post(url, data=payload, ssl=self._verify_ssl) as resp:
            data = await resp.json(content_type=None)
            if resp.status >= 400:
                raise BMWMotorradAuthError(f"Device code request failed: {resp.status} {data}")
            return DeviceCodeData(
                device_code=data["device_code"],
                user_code=data["user_code"],
                verification_uri=data.get("verification_uri") or data.get("verification_uri_complete"),
                expires_in=int(data.get("expires_in", 600)),
                interval=int(data.get("interval", 5)),
            )

    async def async_exchange_device_code(self, device_code: str) -> TokenData:
        url = f"{self._token_host}{TOKEN_ENDPOINT}"
        payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": self._client_id,
            "device_code": device_code,
        }
        async with self._session.post(url, data=payload, ssl=self._verify_ssl) as resp:
            data = await resp.json(content_type=None)
            if resp.status >= 400:
                raise BMWMotorradAuthError(f"Token exchange failed: {resp.status} {data}")
            self._token = TokenData.from_token_response(data)
            return self._token

    async def async_refresh_token(self) -> TokenData:
        if not self._token or not self._token.refresh_token:
            raise BMWMotorradAuthError("No refresh token available")
        url = f"{self._token_host}{TOKEN_ENDPOINT}"
        payload = {
            "grant_type": "refresh_token",
            "client_id": self._client_id,
            "refresh_token": self._token.refresh_token,
        }
        async with self._session.post(url, data=payload, ssl=self._verify_ssl) as resp:
            data = await resp.json(content_type=None)
            if resp.status >= 400:
                raise BMWMotorradAuthError(f"Refresh failed: {resp.status} {data}")
            self._token = TokenData.from_token_response(data)
            return self._token

    async def _ensure_token(self) -> None:
        if not self._token:
            raise BMWMotorradAuthError("Not authenticated")
        if self._token.expires_at <= datetime.now(tz=UTC):
            await self.async_refresh_token()

    async def async_get_bikes(self) -> list[BikeData]:
        await self._ensure_token()
        url = f"{self._api_host}{BIKES_ENDPOINT_TMPL.format(country=self._country)}"
        headers = {"Authorization": f"Bearer {self._token.access_token}"}
        async with self._session.get(url, headers=headers, ssl=self._verify_ssl) as resp:
            data = await resp.json(content_type=None)
            if resp.status == 401:
                _LOGGER.debug("401 from Motorrad endpoint, attempting token refresh")
                await self.async_refresh_token()
                headers["Authorization"] = f"Bearer {self._token.access_token}"
                async with self._session.get(url, headers=headers, ssl=self._verify_ssl) as retry_resp:
                    retry_data = await retry_resp.json(content_type=None)
                    if retry_resp.status >= 400:
                        raise BMWMotorradAuthError(
                            f"Unauthorized after refresh: {retry_resp.status} {retry_data}"
                        )
                    return self._parse_bikes(retry_data)
            if resp.status >= 400:
                raise BMWMotorradApiError(f"Bike fetch failed: {resp.status} {data}")
            return self._parse_bikes(data)

    def _parse_bikes(self, data: Any) -> list[BikeData]:
        if isinstance(data, dict):
            # Support either a list payload or wrapped payloads.
            if "items" in data and isinstance(data["items"], list):
                items = data["items"]
            elif "bikes" in data and isinstance(data["bikes"], list):
                items = data["bikes"]
            else:
                items = [data]
        elif isinstance(data, list):
            items = data
        else:
            raise BMWMotorradApiError(f"Unexpected payload type: {type(data)!r}")
        return [BikeData.from_api(item) for item in items]
