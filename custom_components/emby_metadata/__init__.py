"""Emby Metadata integration for Home Assistant."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN, PLATFORMS
from .coordinator import EmbyCoordinator, EmbySessionsCoordinator
from .frontend import CARD_URL, async_register_card

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the integration and expose the companion Lovelace card."""
    static_dir = Path(__file__).parent / "static"
    await hass.http.async_register_static_paths(
        [StaticPathConfig(CARD_URL, str(static_dir / "emby-metadata-card.js"), True)]
    )
    await async_register_card(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Emby Metadata from a config entry."""
    servers = hass.data.setdefault(DOMAIN, {})
    key = _server_key(entry)
    if key not in servers:
        servers[key] = EmbySessionsCoordinator(hass, entry)
        await servers[key].async_register_shutdown()
    sessions = servers[key]
    sessions.clients[entry.entry_id] = entry
    coordinator = EmbyCoordinator(hass, entry, sessions)
    try:
        await sessions.async_ensure_data()
        sessions.select_interval(sessions.data)
        await coordinator.async_config_entry_first_refresh()
        entry.runtime_data = coordinator
        coordinator.async_start()
        sessions.async_set_updated_data(sessions.data)
        await hass.config_entries.async_forward_entry_setups(entry, ["image"])
        await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    except BaseException:
        await coordinator.async_stop()
        await _release_server(hass, entry)
        raise
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Emby Metadata config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        await entry.runtime_data.async_stop()
        await _release_server(hass, entry)
    return unloaded


def _server_key(entry):
    """Never share sessions across different credentials."""
    data = entry.data
    return (data["protocol"].lower(), data["host"].lower(), data["port"], data["api_key"])


async def _release_server(hass, entry):
    servers = hass.data[DOMAIN]
    key = _server_key(entry)
    sessions = servers[key]
    sessions.clients.pop(entry.entry_id, None)
    if not sessions.clients:
        servers.pop(key)
        await sessions.async_shutdown()
    elif sessions.data is not None:
        sessions.select_interval(sessions.data)
        # Reset the schedule without another HTTP request.
        if sessions.last_update_success:
            sessions.async_set_updated_data(sessions.data)


async def _async_options_updated(hass, entry):
    sessions = entry.runtime_data.sessions
    sessions.clients[entry.entry_id] = entry
    if sessions.last_update_success:
        sessions.select_interval(sessions.data or [])
        sessions.async_set_updated_data(sessions.data or [])
    else:
        await sessions.async_request_refresh()
