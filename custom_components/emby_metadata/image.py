"""Emby poster, backdrop, title-logo and cast image entities."""

from __future__ import annotations

from datetime import datetime, timezone
import logging

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EmbyCoordinator
from .metadata import image_source

_LOGGER = logging.getLogger(__name__)


class EmbyImageEntity(CoordinatorEntity[EmbyCoordinator], ImageEntity):
    """Serve an Emby image through Home Assistant's authenticated image proxy."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: EmbyCoordinator,
        entry: ConfigEntry,
        image_kind: str,
        name: str,
    ) -> None:
        CoordinatorEntity.__init__(self, coordinator)
        ImageEntity.__init__(self, hass)
        self.entry = entry
        self.image_kind = image_kind
        self._attr_unique_id = f"{entry.entry_id}_{image_kind}"
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": f"Emby - {entry.data.get('device_name', 'Device')}",
            "manufacturer": "Emby",
        }
        self._cached_key: tuple[str, str, str] | None = None
        self._cached_bytes: bytes | None = None
        self._cached_key = self._source()
        if self._cached_key:
            self._attr_image_last_updated = datetime.now(timezone.utc)

    def _source(self) -> tuple[str, str, str | None] | None:
        return image_source(self.coordinator.data.get("NowPlayingItem"), self.image_kind)

    @property
    def available(self) -> bool:
        return super().available and self._source() is not None

    def _handle_coordinator_update(self) -> None:
        """Invalidate the image cache only when its source changes."""
        key = self._source()
        if key != self._cached_key:
            self._cached_key = key
            self._cached_bytes = None
            self._attr_image_last_updated = datetime.now(timezone.utc)
        super()._handle_coordinator_update()

    async def async_image(self) -> bytes | None:
        """Fetch and cache the current Emby image."""
        source = self._source()
        if source is None:
            return None
        if self._cached_bytes is not None and source == self._cached_key:
            return self._cached_bytes
        try:
            content, content_type = await self.coordinator.async_fetch_image(*source)
        except Exception as err:
            _LOGGER.debug("Unable to fetch Emby %s image: %s", self.image_kind, err)
            return None
        if source != self._source():
            return None
        self._cached_key = source
        self._cached_bytes = content
        self._attr_content_type = content_type
        return content


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Emby metadata image entities."""
    coordinator: EmbyCoordinator = entry.runtime_data

    entities = [
        EmbyImageEntity(hass, coordinator, entry, "poster", "Poster"),
        EmbyImageEntity(hass, coordinator, entry, "backdrop", "Backdrop"),
        EmbyImageEntity(hass, coordinator, entry, "logo", "Title Logo"),
        EmbyImageEntity(hass, coordinator, entry, "director", "Director"),
    ]
    for index in range(1, 6):
        entities.append(
            EmbyImageEntity(hass, coordinator, entry, f"actor_{index}", f"Actor {index}")
        )

    async_add_entities(entities)
