## Documentation improvements

- English and French guides now cover the same features, installation instructions, screenshots and configuration examples, with links between languages.
- Clarifies that the bundled card is optional and explains how to build a custom dashboard using each Emby client's metadata sensor and image entities.
- Removes development details from the presentation and keeps compatibility information concise.

Integration and card behavior are unchanged.

## Updating

Update through HACS and restart Home Assistant. UI-managed card resources update automatically. For YAML-managed resources, use `/api/emby_metadata/emby-metadata-card.js?v=1.2.13` as a JavaScript module.

[English guide](https://github.com/PedroDelCargo/ha-emby-metadata/blob/v1.2.13/README.md) · [Guide français](https://github.com/PedroDelCargo/ha-emby-metadata/blob/v1.2.13/INSTALLATION.md)

Available as a HACS custom repository. [Default catalog submission](https://github.com/hacs/default/pull/11725) is awaiting review.
