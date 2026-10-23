# Emby Metadata

[English](README.md) · [Français](INSTALLATION.md)

A Home Assistant integration for media playing on an Emby client, with an optional companion dashboard card.

**Use the included card or build your own dashboard.** Each configured Emby client has its own metadata sensor and image entities, which you can use in other Home Assistant cards and custom layouts.

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/custom_components/emby_metadata/brand/icon.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/custom_components/emby_metadata/brand/icon.png" alt="Emby Metadata" width="128"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet.png" alt="Movie on tablet with poster and synopsis" width="640"></a>

[Screenshots](#screenshots) · [Installation](#installation) · [Lovelace card configuration](#lovelace-card-configuration)

## Features

- Movies, TV episodes and personal videos, using metadata available in Emby.
- Responsive layout at 768 px, optional poster, proportional backdrop and title logo with text fallback.
- Optional playback controls, elapsed/remaining time and progress, linked automatically to the matching Home Assistant Emby player.
- Synopsis, rating, runtime, video, audio and subtitle information.
- Director and up to five actors with photos and fallback portraits.
- Animated sections: opening one collapses the others.
- English, French, German and Spanish, following the Home Assistant language.
- Images served by Home Assistant; the Emby API key stays on the server.
- Unchanged metadata does not rebuild the card.

## Screenshots

Real screenshots from Home Assistant on mobile and tablet. The examples use the French interface; the card also supports English, German and Spanish. Click an image to view it at full size.

### Mobile

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-synopsis.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-synopsis.jpg" alt="Synopsis and player" width="280"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-technical.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-technical.jpg" alt="Technical information and player" width="280"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-cast.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-mobile-cast.jpg" alt="Cast and player" width="280"></a>

### Tablet

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-technical.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-technical.png" alt="Technical information" width="640"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-cast.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-cast.png" alt="Cast" width="640"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-no-poster.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/player-tablet-no-poster.png" alt="Player without poster" width="640"></a>

### TV episodes

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-tv-show.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-tv-show.jpg" alt="TV episode" width="640"></a>

## Installation

### Install through HACS (recommended)

1. Open **HACS** in Home Assistant and search for **Emby Metadata**.
2. Open the integration and download it.
3. Restart Home Assistant, then configure your player as described below.

### Before configuring a player

**The target Emby player must be active and connected to your Emby server to be detected.** Open the Emby application on that device, sign in and leave it open during setup. Powering on the device alone is not enough. Detection uses the server's active client sessions, not a list of all previously used devices.

If the player is missing, start playback briefly, then go back to the server connection step and submit it again to refresh the player list. Repeat this preparation when adding another player.

### Configure the player

1. Open **Settings → Devices & services → Add integration → Emby Metadata**.
2. Enter your Emby protocol, host, port and API key, then select the client to monitor. Start the client if it is not listed.
3. The card resource is registered automatically when resources are managed through the UI. Reload the browser after restarting. For YAML-managed resources, add this URL as a **JavaScript module**:

```text
/api/emby_metadata/emby-metadata-card.js?v=2.0.0
```

In storage mode, the integration creates or updates its resource and removes duplicate entries for its exact endpoint. Existing manual entries at that endpoint are reused. Other URLs are left untouched. YAML resources still require manual updates, using the same URL and `type: module`. Removing or reloading an Emby client keeps the shared card resource.

### Manual installation (alternative)

1. Download the **Source code (zip)** archive from the [latest release](https://github.com/PedroDelCargo/ha-emby-metadata/releases/latest) and extract it.
2. Copy the archive’s `custom_components/emby_metadata` folder into your Home Assistant `custom_components` directory.
3. Restart Home Assistant, then follow **Configure the player** above.

## Lovelace card configuration

Choose the player's sensor and toggle the player, poster, video, audio, subtitles and cast directly in Home Assistant's visual card editor.

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/configuration-player.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/configuration-player.png" alt="Home Assistant visual editor for the Emby Metadata card" width="640"></a>

You can also configure the card in YAML:

```yaml
type: custom:emby-metadata-card
entity: sensor.emby_metadata_shield_tv
show_poster: true
show_video: true
show_audio: true
show_subtitles: true
show_cast: true
show_player: false
```

Replace the example entity with your sensor. These options are also available in the visual editor. Poster display applies to horizontal layout. Empty sections are hidden. Media titles, plots, genres and roles remain in the language provided by Emby.

### Optional player

Enable **Show player controls and progress** in the visual card editor (`show_player: true` in YAML). This option is off by default, including after an upgrade. Existing card configurations continue to work.

The built-in **Emby** integration must provide a matching `media_player` entity in Home Assistant. Emby Metadata links it automatically using the Emby client identifier, including when the entity has been renamed. No extra player selection is needed. If no matching entity exists, the player block is hidden; metadata and images still work independently.

## Build your own dashboard

The included Emby Metadata card is optional. The integration provides entities for each configured Emby client, so you can create your own presentation using Home Assistant cards that support those entities and attributes.

- **Now Playing sensor:** the current title and attributes such as synopsis, genres, year, runtime, ratings, series/season/episode details, video/audio/subtitle information, director and actors.
- **Image entities:** poster, backdrop, title logo, director portrait and five actor portraits, depending on the images available in Emby.

Find these entities under **Settings → Devices & services → Emby Metadata**, then open the relevant client device. Inspect the sensor attributes in **Developer tools → States**. Entity IDs depend on your installation; use the IDs shown in your own Home Assistant.

The sensor also exposes `poster_entity`, `backdrop_entity` and `logo_entity`. When people are available, `director` and the entries in `actors` contain their names, roles and `image_entity` references. Metadata depends on what Emby supplies, and image entities may be unavailable when no matching image exists.

## Refresh intervals

Open **Settings → Devices & services → Emby Metadata**, then open the configuration/options for the relevant client. Intervals can be changed from **5 to 300 seconds**, in whole seconds:

| Client state | Default |
| --- | --- |
| Connected, not playing | 5 seconds |
| Playing or paused | 5 seconds |
| Absent from Emby sessions | 30 seconds |

Changes apply immediately, without restarting Home Assistant. Existing clients receive these defaults automatically. Clients using the same server address and API key share one session request at the shortest interval needed by their current states. Different server addresses or API keys are handled separately. Shorter intervals increase requests; metadata and image caches remain enabled.

These are checking intervals, not a guarantee of total display time: Emby must first report playback, and metadata and images must then load. If you open the Emby application and start a movie together, the absent-client interval can still affect detection. Try reducing it to 10 seconds if needed. After a server connection failure, session checks retry after 30 seconds.

## Multiple Emby players

Add one integration entry for each Emby player:

1. Open Emby on the additional player so the server lists it as an active client.
2. In **Settings → Devices & services → Add integration**, choose **Emby Metadata** again.
3. Enter the same server details and API key if the player uses the same Emby server.
4. Select the additional player. A player already configured cannot be added twice.
5. Add a new dashboard card, or duplicate an existing one, and select the new player's sensor in the visual editor.

Each player has its own sensor and image entities. Find the correct sensor in the entities associated with that integration entry; entity IDs depend on your installation. Each card displays the media playing on its selected player, so several cards can show different media simultaneously.

All players share a single JavaScript resource. Do not add another resource or install a second copy of the integration files. This also applies to YAML-managed resources: declare the resource only once.

## Troubleshooting

- **Custom element does not exist:** check the resource URL, restart Home Assistant and refresh the browser cache.
- **Client missing:** start the Emby client and retry configuration.
- **Missing people or images:** check the item's metadata in Emby; fallbacks depend on available metadata.
- **Nothing playing:** check that the configured client is playing the media.

## Compatibility

Tested on Home Assistant Core **2026.9.4**, frontend **20260826.7**. Earlier versions have not been verified.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and [TRANSLATIONS.md](TRANSLATIONS.md). Users do not need to build the bundled JavaScript. The French version of this guide is available in [INSTALLATION.md](INSTALLATION.md).

## License

MIT — see [LICENSE](LICENSE).

