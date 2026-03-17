from __future__ import annotations

DOMAIN = "bmw_motorrad_connectedride"
PLATFORMS = ["sensor", "binary_sensor", "device_tracker"]

CONF_CLIENT_ID = "client_id"
CONF_COUNTRY = "country"
CONF_API_HOST = "api_host"
CONF_DEVICE_CODE_HOST = "device_code_host"
CONF_TOKEN_HOST = "token_host"
CONF_POLL_INTERVAL = "poll_interval"
CONF_VERIFY_SSL = "verify_ssl"

DEFAULT_API_HOST = "https://cpp.bmw-motorrad.com"
DEFAULT_DEVICE_CODE_HOST = "https://api-cardata.bmwgroup.com"
DEFAULT_TOKEN_HOST = "https://api-cardata.bmwgroup.com"
DEFAULT_COUNTRY = "nl-NL"
DEFAULT_POLL_INTERVAL = 300

ATTR_BIKE_ID = "bike_id"
ATTR_RAW = "raw"

DEVICE_CODE_ENDPOINT = "/gcdm/oauth/device/code"
TOKEN_ENDPOINT = "/gcdm/oauth/token"
BIKES_ENDPOINT_TMPL = "/v2/service/{country}/bmc-user-bikes"

SCOPES = [
    "cardata:api:read"
]
