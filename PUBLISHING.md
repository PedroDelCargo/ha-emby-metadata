# Publication checklist

Prepared on 2026-10-05. This folder is the repository root.

## Project details

- Repository: `PedroDelCargo/ha-emby-metadata`. Manifest URLs and codeowner are configured accordingly. If the name changes, update both URLs.
- MIT license, copyright PedroDelCargo.
- Tested: Home Assistant Core 2026.9.4, frontend 20260826.7. Earlier releases have not been tested; no minimum is asserted in hacs.json.
- Create the public repository, enable issues, and add a description and topics (`home-assistant`, `hacs`, `emby`, `lovelace`).

## Validation and release

1. Run local checks in CONTRIBUTING.md.
2. Pass GitHub jobs: tests, Hassfest and HACS. Official remote validators have not yet run; the repository must first exist at the configured URL.
3. Test a clean install and upgrade through a HACS custom repository. Automatic registration is implemented for storage resources and covered by dependency-double tests. Validate first installation, existing manual resources, upgrade and two clients on real HA. YAML resources remain manual.
4. Publish a GitHub Release for 1.2.9. HACS downloads the integration directory; `zip_release` is not enabled.
5. Request default catalog inclusion after validation. Acceptance belongs to HACS maintainers.

## References

- [Integration requirements](https://www.hacs.xyz/docs/publish/integration/)
- [HACS action](https://www.hacs.xyz/docs/publish/action/)
- [Default catalog inclusion](https://www.hacs.xyz/docs/publish/include/)
