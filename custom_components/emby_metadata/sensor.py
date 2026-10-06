"""Emby metadata sensor."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_DEVICE_NAME, DOMAIN
from .coordinator import EmbyCoordinator
from .metadata import people, hdr_value


def ticks_to_minutes(ticks) -> int | None:
    try:
        value = int(ticks or 0)
    except (TypeError, ValueError):
        return None
    return round(value / 10_000_000 / 60) if value else None


def selected_stream(item: dict, kind: str, index=None) -> dict:
    """Return the selected Emby stream, respecting an explicit disabled index."""
    streams = [s for s in (item.get("MediaStreams") or []) if s.get("Type") == kind]
    if index is not None:
        try:
            index = int(index)
        except (TypeError, ValueError):
            return {}
        if index < 0:
            return {}
        for stream in streams:
            if stream.get("Index") == index:
                return stream
        return {}
    return next((s for s in streams if s.get("IsDefault")), {}) if kind == "Subtitle" else next((s for s in streams if s.get("IsDefault")), streams[0] if streams else {})


def people_metadata(item: dict) -> tuple[dict | None, list[dict]]:
    """Extract director and five principal actors, including image metadata."""
    director = None
    actors: list[dict] = []

    for person in people(item):
        name = person.get("Name")
        if not name:
            continue

        person_type = str(person.get("Type") or "").lower()
        data = {
            "id": person.get("Id"),
            "name": name,
            "role": person.get("Role"),
            "image_tag": person.get("PrimaryImageTag"),
        }

        if person_type == "director" and director is None:
            director = data
        elif person_type == "actor" and len(actors) < 5:
            actors.append(data)

    return director, actors


def device_info(entry: ConfigEntry, coordinator: EmbyCoordinator) -> DeviceInfo:
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name=f"Emby - {entry.data.get(CONF_DEVICE_NAME, 'Device')}",
        manufacturer="Emby",
        model=coordinator.data.get("Client", "Emby client"),
    )


class EmbyNowPlayingSensor(CoordinatorEntity[EmbyCoordinator], SensorEntity):
    """Current item and its metadata/technical information."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:movie-open"
    _unrecorded_attributes = frozenset(
        {
            "overview",
            "external_urls",
            "media_streams",
            "director",
            "actors",
        }
    )

    def __init__(self, coordinator: EmbyCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_now_playing"
        self._attr_name = "Now Playing"
        self._attr_device_info = device_info(entry, coordinator)

    @property
    def native_value(self) -> str:
        item = self.coordinator.data.get("NowPlayingItem")
        return item.get("Name", "Idle") if item else "Idle"

    @property
    def extra_state_attributes(self) -> dict:
        session = self.coordinator.data
        item = session.get("NowPlayingItem")
        registry = async_get_entity_registry(self.hass)

        def entity_id(suffix: str) -> str | None:
            return registry.async_get_entity_id(
                "image", DOMAIN, f"{self.entry.entry_id}_{suffix}"
            )

        attrs = {
            "device_name": session.get("DeviceName"),
            "device_id": session.get("DeviceId"),
            "client": session.get("Client"),
            "application_version": session.get("ApplicationVersion"),
            "poster_entity": entity_id("poster"),
            "backdrop_entity": entity_id("backdrop"),
            "logo_entity": entity_id("logo"),
        }

        if not item:
            attrs["playing"] = False
            return {k: v for k, v in attrs.items() if v is not None}

        playstate = session.get("PlayState", {})
        video = selected_stream(item, "Video")
        audio = selected_stream(item, "Audio", playstate.get("AudioStreamIndex"))
        subtitle = selected_stream(item, "Subtitle", playstate.get("SubtitleStreamIndex"))
        providers = (item.get("ProviderIds") or {})
        image_tags = item.get("ImageTags") or {}
        backdrop_tags = item.get("BackdropImageTags") or []
        director, actors = people_metadata(item)

        director_out = None
        if director:
            director_out = {
                "name": director["name"],
                "role": director.get("role") or "Director",
                "image_entity": entity_id("director"),
            }

        actors_out = []
        for index, actor in enumerate(actors, start=1):
            actors_out.append(
                {
                    "name": actor["name"],
                    "role": actor.get("role"),
                    "image_entity": entity_id(f"actor_{index}"),
                }
            )

        attrs.update(
            {
                "playing": True,
                "media_type": item.get("Type"),
                "title": item.get("Name"),
                "series_title": item.get("SeriesName"),
                "season_number": item.get("ParentIndexNumber"),
                "episode_number": item.get("IndexNumber"),
                "episode_number_end": item.get("IndexNumberEnd"),
                "season_title": item.get("SeasonName"),
                "original_title": item.get("OriginalTitle"),
                "tagline": item.get("Tagline"),
                "production_year": item.get("ProductionYear"),
                "premiere_date": item.get("PremiereDate"),
                "overview": item.get("Overview"),
                "genres": item.get("Genres"),
                "official_rating": item.get("OfficialRating"),
                "community_rating": item.get("CommunityRating"),
                "critic_rating": item.get("CriticRating"),
                "runtime_minutes": ticks_to_minutes(item.get("RunTimeTicks")),
                "container": item.get("Container"),
                "bitrate": item.get("Bitrate"),
                "video_codec": video.get("Codec"),
                "video_profile": video.get("Profile"),
                "video_width": video.get("Width"),
                "video_height": video.get("Height"),
                "video_bit_depth": video.get("BitDepth"),
                "video_frame_rate": video.get("AverageFrameRate"),
                "video_hdr": hdr_value(video),
                "audio_codec": audio.get("Codec"),
                "audio_language": audio.get("Language"),
                "audio_title": audio.get("Title"),
                "audio_channels": audio.get("Channels"),
                "audio_channel_layout": audio.get("ChannelLayout"),
                "subtitle_language": subtitle.get("Language"),
                "subtitle_title": subtitle.get("Title"),
                "subtitle_forced": subtitle.get("IsForced"),
                "subtitle_hearing_impaired": subtitle.get("IsHearingImpaired"),
                "director": director_out,
                "actors": actors_out,
                "imdb_id": providers.get("Imdb"),
                "tmdb_id": providers.get("Tmdb"),
                "tvdb_id": providers.get("Tvdb"),
                "emby_item_id": item.get("Id"),
                "primary_image_tag": image_tags.get("Primary"),
                "backdrop_image_tag": backdrop_tags[0] if backdrop_tags else None,
                "logo_image_tag": image_tags.get("Logo"),
                "parent_logo_item_id": item.get("ParentLogoItemId"),
                "parent_logo_image_tag": item.get("ParentLogoImageTag"),
            }
        )
        return {key: value for key, value in attrs.items() if value is not None}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Emby metadata sensor."""
    coordinator: EmbyCoordinator = entry.runtime_data
    async_add_entities([EmbyNowPlayingSensor(coordinator, entry)])
