## Playback controls in your Emby card

Enable **Show player controls and progress** in the visual card editor to add Previous, Stop, Play/Pause and Next, elapsed/remaining time and progress.

The matching `media_player` from Home Assistant’s built-in **Emby** integration is detected automatically. Without a matching player, the controls stay hidden and metadata continues to work.

- Same player layout on mobile and tablet, with progress in the theme accent color.
- Smooth local time updates without additional Emby polling.
- More compact card editor and refreshed mobile/tablet screenshots.

**Upgrade:** update through HACS, restart Home Assistant and reload your dashboard. Existing cards remain compatible. Playback controls are off by default; enable them in each card where you want them.
