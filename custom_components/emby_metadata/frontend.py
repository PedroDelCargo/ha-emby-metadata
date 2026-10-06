"""Register the bundled card with Lovelace's resource collection."""

from __future__ import annotations

import logging
from urllib.parse import urlsplit

from homeassistant.components.lovelace.const import LOVELACE_DATA, MODE_STORAGE
from homeassistant.core import HomeAssistant
from homeassistant.loader import async_get_integration

from .const import DOMAIN

CARD_URL = "/api/emby_metadata/emby-metadata-card.js"
_LOGGER = logging.getLogger(__name__)


def _is_card_resource(url: str) -> bool:
    """Match only our relative endpoint, regardless of version query."""
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    return not parsed.scheme and not parsed.netloc and parsed.path == CARD_URL


async def async_register_card(hass: HomeAssistant) -> None:
    """Register once at integration setup, independently of client entries.

    Lovelace is a dependency, so its resource collection already exists.
    Keep the resource when a client is unloaded: other clients/dashboards may
    still use the same card. Never write to YAML or storage files directly.
    """
    try:
        integration = await async_get_integration(hass, DOMAIN)
        url = f"{CARD_URL}?v={integration.version}"
        lovelace = hass.data[LOVELACE_DATA]
        if lovelace.resource_mode != MODE_STORAGE:
            _LOGGER.info(
                "Lovelace resources are managed in YAML. Add or update the "
                "Emby Metadata resource manually: url: %s, type: module", url
            )
            return

        resources = lovelace.resources
        # Public method ensures the lazy storage collection has been loaded.
        await resources.async_get_info()
        matches = [
            item for item in resources.async_items()
            if _is_card_resource(item.get("url", ""))
        ]
        values = {"url": url, "res_type": "module"}
        if not matches:
            await resources.async_create_item(values)
            return

        primary = matches[0]
        if primary.get("url") != url or primary.get("type") != "module":
            await resources.async_update_item(primary["id"], values)
        # Only duplicate entries for our own exact endpoint are removed.
        for duplicate in matches[1:]:
            await resources.async_delete_item(duplicate["id"])
    except Exception:  # The optional card must not prevent sensor setup.
        _LOGGER.exception(
            "Could not register the Emby Metadata card automatically. "
            "Add %s as a JavaScript module in dashboard resources, "
            "or restart Home Assistant to retry", CARD_URL
        )
