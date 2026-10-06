"""Emby API coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging
from time import monotonic
from urllib.parse import quote

from .metadata import normalize_item

from aiohttp import ClientError, ClientTimeout
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_HOST,
    CONF_PORT,
    CONF_PROTOCOL,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class EmbyCoordinator(DataUpdateCoordinator[dict]):
    """Fetch the selected Emby client session."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.base_url = (
            f"{entry.data[CONF_PROTOCOL]}://{entry.data[CONF_HOST]}:{entry.data[CONF_PORT]}"
        ).rstrip("/")
        self.api_key = entry.data[CONF_API_KEY]
        self.device_id = entry.data[CONF_DEVICE_ID]
        self.device_name = entry.data.get(CONF_DEVICE_NAME, "Emby device")
        self.session = async_get_clientsession(hass)
        self._details_cache = {}
        super().__init__(
            hass,
            logger=_LOGGER,
            name=f"Emby {self.device_name}",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            always_update=False,
        )

    async def _async_update_data(self) -> dict:
        """Fetch all sessions and select the configured client."""
        url = f"{self.base_url}/emby/Sessions"
        try:
            async with self.session.get(
                url,
                headers={"X-Emby-Token": self.api_key},
                timeout=ClientTimeout(total=10),
            ) as response:
                if response.status == 401:
                    raise UpdateFailed("Emby API key rejected")
                if response.status != 200:
                    raise UpdateFailed(f"Emby returned HTTP {response.status}")
                sessions = await response.json()
        except UpdateFailed:
            raise
        except (ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Unable to connect to Emby: {err}") from err

        if not isinstance(sessions, list):
            raise UpdateFailed("Unexpected Emby /Sessions response")

        for session in sessions:
            if session.get("DeviceId") == self.device_id:
                item = session.get("NowPlayingItem")
                if item and item.get("Id"):
                    user_id = session.get("UserId")
                    details = await self._item_details(item["Id"], user_id)
                    combined = {**item, **details}
                    series = await self._item_details(combined.get("SeriesId"), user_id)
                    season = await self._item_details(combined.get("SeasonId"), user_id)
                    item = normalize_item(item, details, series, season,
                                          (session.get("PlayState") or {}).get("MediaSourceId"))
                self.update_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL if item else 30)
                # Keep only data that affects the metadata card. In particular,
                # omit playback position/time fields so a 5-second poll does not
                # trigger a state update while the same item is playing.
                playstate = session.get("PlayState") or {}
                return {
                    "DeviceId": session.get("DeviceId"),
                    "DeviceName": session.get("DeviceName", self.device_name),
                    "Client": session.get("Client"),
                    "ApplicationVersion": session.get("ApplicationVersion"),
                    "NowPlayingItem": item,
                    "PlayState": {
                        "AudioStreamIndex": playstate.get("AudioStreamIndex"),
                        "SubtitleStreamIndex": playstate.get("SubtitleStreamIndex"),
                    },
                }

        self.update_interval = timedelta(seconds=30)
        return {
            "DeviceId": self.device_id,
            "DeviceName": self.device_name,
            "Client": None,
            "ApplicationVersion": None,
            "NowPlayingItem": None,
            "PlayState": {
                "AudioStreamIndex": None,
                "SubtitleStreamIndex": None,
            },
        }

    async def _item_details(self, item_id, user_id=None) -> dict:
        """Use documented item endpoints; cache details and retry failed enrichments."""
        if not item_id:
            return {}
        key = (str(user_id or ""), str(item_id))
        now = monotonic()
        previous = self._details_cache.get(key)
        if previous and now < previous[0]:
            return previous[1]
        requests = []
        if user_id:
            requests.append((f"/Users/{quote(str(user_id), safe='')}/Items/{quote(str(item_id), safe='')}", {}))
        requests.append(("/Items", {
            "Ids": str(item_id),
            "Fields": "People,Overview,Genres,MediaStreams,MediaSources,ProviderIds,Taglines",
            "EnableImages": "true",
        }))
        for path, params in requests:
            try:
                async with self.session.get(
                    f"{self.base_url}/emby{path}", params=params,
                    headers={"X-Emby-Token": self.api_key},
                    timeout=ClientTimeout(total=5),
                ) as response:
                    if response.status != 200:
                        _LOGGER.debug("Emby metadata endpoint %s returned HTTP %s", path, response.status)
                        continue
                    data = await response.json()
                    if path == "/Items":
                        data = next((v for v in data.get("Items", []) if str(v.get("Id")) == str(item_id)), {}) if isinstance(data, dict) else {}
                    if isinstance(data, dict) and str(data.get("Id")) == str(item_id):
                        self._cache_details(key, now + 300, data)
                        return data
            except (ClientError, TimeoutError, ValueError):
                _LOGGER.debug("Unable to enrich Emby item %s", item_id)
        # Preserve previous metadata during a transient failure, but never reuse
        # another item's details when playback advances.
        data = previous[1] if previous else {}
        self._cache_details(key, now + 30, data)
        return data

    def _cache_details(self, key, expires, data):
        if key not in self._details_cache and len(self._details_cache) >= 32:
            self._details_cache.pop(next(iter(self._details_cache)))
        self._details_cache[key] = (expires, data)

    async def async_fetch_image(self, item_id: str, image_type: str, tag: str | None = None) -> tuple[bytes, str]:
        """Fetch one Emby image without exposing the API key to the browser."""
        url = f"{self.base_url}/emby/Items/{item_id}/Images/{image_type}"
        params = {"Tag": tag} if tag else {}
        async with self.session.get(
            url,
            params=params,
            headers={"X-Emby-Token": self.api_key},
            timeout=ClientTimeout(total=15),
        ) as response:
            if response.status != 200:
                raise UpdateFailed(f"Emby image request returned HTTP {response.status}")
            content_type = response.headers.get("Content-Type", "image/jpeg").split(";", 1)[0]
            return await response.read(), content_type
