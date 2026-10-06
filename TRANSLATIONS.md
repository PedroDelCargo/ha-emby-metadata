# Card translations

The card defaults to English and includes French, German and Spanish. It follows the current Home
Assistant interface language (`hass.locale.language`, then `hass.language`).
Regional variants such as `fr-CA` use their base language when no exact dictionary
exists. Unsupported languages and missing translation keys fall back to English.
No browser language or global language setting is used, so cards and editor
instances do not overwrite each other's language.

## What is translated

- Card status messages, synopsis controls, technical headings, subtitle flags,
  cast heading and the default director label.
- Visual editor fields, expandable section heading and validation errors.
- Audio/subtitle language names through `Intl.DisplayNames`.
- Ratings through `Intl.NumberFormat`: for example, `6.4` in English and `6,4`
  in French. A language change refreshes the card; unchanged data in the same
  language does not rebuild it.

Movie/series titles, plots, genres, character names and other Emby metadata stay
as supplied by the server. Codec and format names remain their standard names.
The card picker description is English because its registration is static.

## Adding a card language

Each language has its own UTF-8 JSON source file:

```text
frontend/
  emby-metadata-card.js
  translations/
    en.json
    fr.json
    de.json
    es.json
scripts/
  build_card.py
```

1. Copy `frontend/translations/en.json` to a new language file, for example
   `it.json` or `pt-br.json`. Use lowercase language tags.
2. Translate the values only. Keep keys and placeholders such as `{key}` unchanged.
3. Submit the language JSON in a pull request. Translation contributors do not
   need to edit JavaScript or the generated file.

Missing entries fall back to English. The build rejects duplicate or unknown
keys, empty values, invalid filenames and changed placeholders.

### For maintainers

From the repository/archive root, using Python 3.10 or later, run:

```sh
python scripts/build_card.py
python scripts/build_card.py --check
```

There are no extra Python dependencies. The first command generates
`custom_components/emby_metadata/static/emby-metadata-card.js` from the source
card and all translation JSON files. The second validates translations and checks
that the generated file is current without modifying it; it is suitable for CI.
New language files are discovered automatically, without adding imports.

Distribute the generated JavaScript. Dictionaries are embedded at build time,
so users do not need Python or a build step. The card remains self-contained;
it does not fetch translation JSON at runtime. Changes to source JSON take effect
after a rebuild and release, not immediately on an installed card.

The native `getConfigForm()` editor is retained. Its label and validation methods
read the editor instance's current `hass`. The expandable section uses its
translated label instead of a fixed `title` string.

## Integration translations

The integration setup flow already uses Home Assistant's native translation
files: `strings.json` and `translations/en.json` are English, while
`translations/fr.json` supplies French. These are separate from the custom
card's JavaScript dictionary. Add other setup-flow translations as
`translations/<language>.json`.

Backend attributes use English for generated role labels. The card also handles
the older `Réalisateur` fallback from versions before 1.2.2.

This release adds localization. Repository metadata, release automation and
the remaining HACS publication requirements are outside this change.
