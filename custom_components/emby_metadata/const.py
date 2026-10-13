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
CONF_IDLE_INTERVAL = "idle_interval"
CONF_PLAYING_INTERVAL = "playing_interval"
CONF_ABSENT_INTERVAL = "absent_interval"
POLL_DEFAULTS = {
    CONF_IDLE_INTERVAL: 5,
    CONF_PLAYING_INTERVAL: 5,
    CONF_ABSENT_INTERVAL: 30,
}
MIN_POLL_INTERVAL = 5
MAX_POLL_INTERVAL = 300


def polling_options(options):
    """Read saved options safely, including entries created before options existed."""
    result = {}
    for key, default in POLL_DEFAULTS.items():
        value = options.get(key, default)
        if isinstance(value, bool) or not isinstance(value, int):
            value = default
        result[key] = max(MIN_POLL_INTERVAL, min(MAX_POLL_INTERVAL, value))
    return result

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.IMAGE]
