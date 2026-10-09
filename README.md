# Emby Metadata

[English](README.md) · [Français](INSTALLATION.md)

A Home Assistant integration for media playing on an Emby client, with an optional companion dashboard card.

**Use the included card or build your own dashboard.** Each configured Emby client has its own metadata sensor and image entities, which you can use in other Home Assistant cards and custom layouts.

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/custom_components/emby_metadata/brand/icon.png"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/custom_components/emby_metadata/brand/icon.png" alt="Emby Metadata" width="128"></a>

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-synopsis.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-synopsis.jpg" alt="Movie on tablet with poster and synopsis" width="640"></a>

[Screenshots](#screenshots) · [Installation](#installation) · [Card configuration](#configuration)

## Features

- Movies, TV episodes and personal videos, using metadata available in Emby.
- Responsive layout at 768 px, optional poster, proportional backdrop and title logo with text fallback.
- Synopsis, rating, runtime, video, audio and subtitle information.
- Director and up to five actors with photos and fallback portraits.
- Animated sections: opening one collapses the others.
- English, French, German and Spanish, following the Home Assistant language.
- Images served by Home Assistant; the Emby API key stays on the server.
- Unchanged metadata does not rebuild the card.

## Screenshots

Real screenshots from Home Assistant on mobile and tablet. The examples use the French interface; the card also supports English, German and Spanish. Click an image to view it at full size.

### Mobile

  <a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-synopsis-small.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-synopsis-small.jpg" alt="Mobile card with a collapsed synopsis" width="280"></a>

  <a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-actors.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-actors.jpg" alt="Mobile card with director and cast expanded" width="280"></a>

Compact synopsis and expandable cast, with names and roles overlaid on portraits.

**More mobile views: full synopsis and technical information**

  <a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-synopsis-full.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-synopsis-full.jpg" alt="Mobile card with the full synopsis expanded" width="280"></a>

  <a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-technical-data.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/mobile-technical-data.jpg" alt="Mobile card showing video, audio and subtitle information" width="280"></a>

### TV episodes

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-tv-show.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-tv-show.jpg" alt="TV episode with series logo, season and episode number, episode title and synopsis" width="640"></a>

Series artwork with episode-specific information. The poster is hidden in this example.

**More tablet views: technical information and cast**

**Video, audio and subtitles, with the poster enabled**

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-technical-data.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-technical-data.jpg" alt="Tablet card with technical information expanded" width="640"></a>

**Director and cast, with the poster hidden**

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-actors.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/tablet-actors.jpg" alt="Tablet card with director and cast expanded" width="280"></a>

## Installation

### Before configuring a player

**The target Emby player must be active and connected to your Emby server to be detected.** Open the Emby application on that device, sign in and leave it open during setup. Powering on the device alone is not enough. Detection uses the server's active client sessions, not a list of all previously used devices.

If the player is missing, start playback briefly, then go back to the server connection step and submit it again to refresh the player list. Repeat this preparation when adding another player.

### Install and configure

1. Copy `custom_components/emby_metadata` into your Home Assistant `custom_components` directory.
2. Restart Home Assistant.
3. Open **Settings → Devices & services → Add integration → Emby Metadata**.
4. Enter your Emby protocol, host, port and API key, then select the client to monitor. Start the client if it is not listed.
5. The card resource is registered automatically when resources are managed through the UI. Reload the browser after restarting. For YAML-managed resources, add this URL as a **JavaScript module**:

```text
/api/emby_metadata/emby-metadata-card.js?v=1.2.13
```

In storage mode, the integration creates or updates its resource and removes duplicate entries for its exact endpoint. Existing manual entries at that endpoint are reused. Other URLs are left untouched. YAML resources still require manual updates, using the same URL and `type: module`. Removing or reloading an Emby client keeps the shared card resource.

`https://github.com/PedroDelCargo/ha-emby-metadata` can be installed as a HACS custom repository of type **Integration**. Restart Home Assistant and follow steps 3–5. The project is not yet in the default HACS catalog.

## Configuration

Choose the player's sensor and toggle the poster, video, audio, subtitles and cast directly in Home Assistant's visual card editor.

<a href="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/configuration.jpg"><img src="https://raw.githubusercontent.com/PedroDelCargo/ha-emby-metadata/main/docs/screenshots/configuration.jpg" alt="Home Assistant visual editor for the Emby Metadata card" width="280"></a>

You can also configure the card in YAML:

```yaml
type: custom:emby-metadata-card
entity: sensor.emby_metadata_shield_tv
show_poster: true
show_video: true
show_audio: true
show_subtitles: true
show_cast: true
```

Replace the example entity with your sensor. These options are also available in the visual editor. Poster display applies to horizontal layout. Empty sections are hidden. Media titles, plots, genres and roles remain in the language provided by Emby.

## Build your own dashboard

The included Emby Metadata card is optional. The integration provides entities for each configured Emby client, so you can create your own presentation using Home Assistant cards that support those entities and attributes.

- **Now Playing sensor:** the current title and attributes such as synopsis, genres, year, runtime, ratings, series/season/episode details, video/audio/subtitle information, director and actors.
- **Image entities:** poster, backdrop, title logo, director portrait and five actor portraits, depending on the images available in Emby.

Find these entities under **Settings → Devices & services → Emby Metadata**, then open the relevant client device. Inspect the sensor attributes in **Developer tools → States**. Entity IDs depend on your installation; use the IDs shown in your own Home Assistant.

The sensor also exposes `poster_entity`, `backdrop_entity` and `logo_entity`. When people are available, `director` and the entries in `actors` contain their names, roles and `image_entity` references. Metadata depends on what Emby supplies, and image entities may be unavailable when no matching image exists.

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

## Publication status

Available as a HACS custom repository. [Default catalog submission](https://github.com/hacs/default/pull/11725) is awaiting review.

## License

MIT — see [LICENSE](LICENSE).

