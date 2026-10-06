# Contributing

Edit `frontend/emby-metadata-card.js`, then rebuild the bundled file. Card dictionaries live in `frontend/translations/`; integration configuration dictionaries are in `custom_components/emby_metadata/translations/`.

Run from the repository root with Python 3.10+:

```sh
python scripts/build_card.py
python scripts/build_card.py --check
python tests/test_backend.py
python tests/test_resources.py
python tests/test_translation_build.py
```

Browser tests use Node.js and Playwright:

```sh
npm install --no-save playwright
npx playwright install chromium
node tests/test_frontend.cjs
node tests/test_i18n.cjs
```

Set `BROWSER_EXECUTABLE` to use an existing Chromium or Edge installation. Artifacts are written to `test-results/`. Backend tests use dependency doubles; test on real Home Assistant and Emby before release. Commit generated JavaScript with source changes. Remove API keys and tokens from issue reports.
