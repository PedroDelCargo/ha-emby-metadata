# Changelog

## 2.0.0 — 2026-10-23

- Add optional Previous, Stop, Play/Pause and Next controls, automatically linked to the matching native Home Assistant Emby player.
- Show elapsed and remaining time with locally smoothed progress and no additional Emby polling.
- Keep the same player layout on mobile and tablet, with progress in the theme accent color.
- Move the rating to the top right, retain runtime on the left and limit title artwork to half the card width.
- Compact the visual card editor and place the player option immediately after the entity.
- Add new mobile and tablet screenshots and player instructions in English and French.
- Existing card configurations remain compatible; playback controls are disabled by default.

## 1.2.15 — 2026-10-21

- Make installation from the default HACS catalog the recommended method.
- Retain manual installation as an alternative and remove outdated custom-repository and pending-review instructions.
- Integration and card behavior are unchanged.

## 1.2.14 — 2026-10-13

- Check connected idle clients every 5 seconds by default instead of 30.
- Add live per-client options for idle, playing/paused and absent intervals (5–300 seconds).
- Share session polling for clients with the same server address and API key, using the shortest required interval.
- Retain metadata/image caching and unchanged-data suppression; limit concurrent metadata requests per server.
- Translate options into English, French, German and Spanish.

## 1.2.13 — 2026-10-09

- Align the English and French guides, including screenshots and configuration examples.
- Explain that the bundled card is optional and document custom dashboards using each client’s sensor and image entities.
- Simplify presentation and compatibility information; add language navigation links.
- No changes to integration or card behavior.

## 1.2.12 — 2026-10-09

- Compact screenshot previews with links to full-size originals in the README.
- Smaller introductory logo.
- Card appearance and integration behavior unchanged from v1.2.11.

## 1.2.11 â€” 2026-10-08
- Restore the exact v1.2.9 card appearance, except for the theme corner radius and 1 px main card padding.
- Revert the broader theme colors, typography and section surfaces introduced in the unpublished 1.2.10 test build.

## 1.2.10 â€” 2026-10-08
- Follow Home Assistant theme colors, typography, borders, radius, shadows and focus styles.
- Add 3 px main container padding and preserve readable image overlays.
- Include the screenshot gallery and setup prerequisites in the next release documentation.
- Use portable Markdown and absolute screenshot URLs in the README for HACS.

## 1.2.9 â€” 2026-10-05
- Automatically register and update the shared Lovelace resource in storage mode.
- Reuse manual entries and remove duplicates for the integration endpoint.
- Keep YAML resources manual and isolate registration failures from sensor setup.

## 1.2.8 â€” 2026-10-05
- Apply 16 px padding above and below the synopsis.
- Prepare repository documentation and validation workflows.

## 1.2.7
- Adjust separators and add German and Spanish translations.

## 1.2.6
- Opening a section collapses the other sections.

## 1.2.5
- Display the synopsis below the visible poster across the full width.

## 1.2.4
- Add animated sections, portrait captions and fallback silhouettes.

## 1.2.3
- Separate translation JSON sources and build script.
