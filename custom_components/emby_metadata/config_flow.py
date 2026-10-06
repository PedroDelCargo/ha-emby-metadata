"""Config flow for Emby Metadata."""

from __future__ import annotations

import voluptuous as vol
from aiohttp import ClientError, ClientTimeout
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_API_KEY,
    CONF_DEVICE_ID,
    CONF_DEVICE_NAME,
    CONF_HOST,
    CONF_PORT,
    CONF_PROTOCOL,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_PROTOCOL,
    DOMAIN,
)


class CannotConnect(HomeAssistantError):
    """Unable to connect to Emby."""


class InvalidAuth(HomeAssistantError):
    """Invalid Emby API key."""


async def _get_sessions(hass, base_url: str, api_key: str) -> list[dict]:
    session = async_get_clientsession(hass)
    try:
        async with session.get(
            f"{base_url.rstrip('/')}/emby/Sessions",
            headers={"X-Emby-Token": api_key},
            timeout=ClientTimeout(total=10),
        ) as response:
            if response.status == 401:
                raise InvalidAuth
            if response.status != 200:
                raise CannotConnect
            data = await response.json()
    except (ClientError, TimeoutError) as err:
        raise CannotConnect from err
    if not isinstance(data, list):
        raise CannotConnect
    return data


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Emby Metadata config flow."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Collect server connection details and discover Emby clients."""
        errors = {}
        if user_input is not None:
            base_url = (
                f"{user_input[CONF_PROTOCOL]}://{user_input[CONF_HOST]}:{user_input[CONF_PORT]}"
            ).rstrip("/")
            try:
                sessions = await _get_sessions(self.hass, base_url, user_input[CONF_API_KEY])
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except (CannotConnect, TimeoutError):
                errors["base"] = "cannot_connect"
            else:
                devices: dict[str, str] = {}
                for session in sessions:
                    device_id = session.get("DeviceId")
                    device_name = session.get("DeviceName") or session.get("Client")
                    if device_id and device_name:
                        devices.setdefault(device_id, device_name)
                if not devices:
                    errors["base"] = "no_devices"
                else:
                    self._server = {
                        CONF_PROTOCOL: user_input[CONF_PROTOCOL],
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PORT: user_input[CONF_PORT],
                        CONF_API_KEY: user_input[CONF_API_KEY],
                    }
                    self._devices = devices
                    return await self.async_step_device()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PROTOCOL, default=DEFAULT_PROTOCOL): vol.In({"http": "HTTP", "https": "HTTPS"}),
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    async def async_step_device(self, user_input=None):
        """Select the Emby client to monitor."""
        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            device_name = self._devices[device_id]
            await self.async_set_unique_id(f"emby_{device_id}")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=device_name,
                data={
                    **self._server,
                    CONF_DEVICE_ID: device_id,
                    CONF_DEVICE_NAME: device_name,
                },
            )

        return self.async_show_form(
            step_id="device",
            data_schema=vol.Schema({vol.Required(CONF_DEVICE_ID): vol.In(self._devices)}),
        )
