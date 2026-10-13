## Faster playback detection

- Connected idle clients are now checked every **5 seconds**, instead of 30 seconds.
- Configure three polling intervals in each client's integration options: **connected and idle (5 seconds)**, **playing or paused (5 seconds)** and **absent (30 seconds)** by default.
- Each interval accepts whole seconds from **5 to 300**. Changes apply without restarting Home Assistant.
- Clients using the same server address and API key share session requests at the shortest interval required by their current states. Metadata and image caches remain enabled.
- The English and French guides explain the settings, shared polling and how the absent-client interval affects detection. Options are translated into English, French, German and Spanish.

## Updating

Update through HACS and restart Home Assistant once. Existing clients receive the default intervals automatically. Open **Settings → Devices & services → Emby Metadata** and the relevant client's options to adjust them.

[English guide](https://github.com/PedroDelCargo/ha-emby-metadata/blob/v1.2.14/README.md) · [Guide français](https://github.com/PedroDelCargo/ha-emby-metadata/blob/v1.2.14/INSTALLATION.md)
