# Scalev developer documentation

This repository is the Git source for [docs.scalev.dev](https://docs.scalev.dev), published through ReadMe Bi-Directional Sync.

## Structure

- `docs/` contains English guide pages and navigation order files.
- `changelog/` contains the source for ReadMe's unversioned native Changelog posts.
- `reference/apiscalevid-v2openapi.json` contains the Scalev API v3 OpenAPI source. The historical filename is retained so ReadMe updates the connected API definition in place.
- `reference/Scalev API/` contains generated ReadMe endpoint pages.
- `reference/ReadMeConfig/` contains ReadMe's hidden API reference configuration pages.

## Validate changes

```sh
python3 scripts/sync_openapi_reference.py --check
python3 scripts/validate_docs.py
```

After updating the OpenAPI file, run `python3 scripts/sync_openapi_reference.py` to regenerate the endpoint pages. Push documentation changes to the ReadMe-connected `v3` branch to publish them.

Guide and API reference content publish through ReadMe Bi-Directional Sync. Changelog posts publish through `.github/workflows/publish-changelog.yml` using the `README_API_KEY` repository secret because ReadMe changelogs are shared across versions and are not part of the versioned Git sync tree.

## ReadMe project settings

The following site-wide settings are managed in the ReadMe dashboard and are not part of Bi-Directional Sync:

- In **Appearance → Navigation**, leave page icons off, show Discussions, and add Status after Changelog as a **Link URL** to `https://status.scalev.com`.
- In **Appearance → Changelog**, use the **Continuous** layout so each repo-managed post displays its opening summary.
