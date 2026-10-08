# Emby Metadata v1.2.11

Preserves the v1.2.9 card appearance with the Home Assistant theme corner radius and 1 px main card padding. Tested by the maintainer on Home Assistant, including the theme radius. The broader styling from the unpublished v1.2.10 test build is not included.

This release includes the mobile/tablet screenshot gallery, visual editor screenshot, active-player setup instructions and confirmation of a successful fresh installation. The README uses standard Markdown and absolute image URLs for HACS.

## Updating

Update through HACS, restart Home Assistant and fully refresh the dashboard. UI-managed card resources update automatically. For YAML-managed resources use `/api/emby_metadata/emby-metadata-card.js?v=1.2.11` as a JavaScript module.

For first setup or an additional player, open Emby on the device, sign in and leave it connected so the server can detect it. Start playback briefly if the player is missing.

[Installation and configuration](https://github.com/PedroDelCargo/ha-emby-metadata/blob/v1.2.11/README.md)

Available as a HACS custom repository. Default catalog submission has not yet been made.
