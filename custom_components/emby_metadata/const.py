from __future__ import annotations

from homeassistant.const import Platform

DOMAIN = "emby_metadata"

CONF_PROTOCOL = "protocol"
CONF_HOST = "host"
CONF_PORT = "port"
CONF_API_KEY = "api_key"
CONF_DEVICE_ID = "device_id"
CONF_DEVICE_NAME = "device_name"

DEFAULT_PROTOCOL = "http"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8096
DEFAULT_SCAN_INTERVAL = 5

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.IMAGE]
