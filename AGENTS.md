# Documentation project instructions

## About this project

- This is the English Scalev developer documentation published with ReadMe.
- Pages are Markdown files with YAML frontmatter under `docs/`.
- Navigation order lives in `_order.yaml` files.
- Native Changelog posts live under `changelog/` and publish with `rdme changelog upload` in GitHub Actions.
- Top-level external links live under `custom_pages/` so redirect and new-tab behavior remain Git-backed.
- The API definition is `reference/openapi.json`; its contents are the current API v3 contract.
- Generate endpoint pages with `python3 scripts/sync_openapi_reference.py` after changing OpenAPI.
- Run `python3 scripts/sync_openapi_reference.py --check` and `python3 scripts/validate_docs.py` before committing.

## Style

- Use active voice and second person ("you").
- Keep sentences concise and use sentence case for headings.
- Bold UI labels and use code formatting for commands, paths, fields, and code references.
- Keep guide links in the `/docs/<slug>` form.
- Write new documentation in English only.

## Content boundaries

- Document public developer workflows and public API behavior.
- Do not document internal administration or implementation details.
- Do not manually edit generated API reference pages under `reference/Scalev API/`.
- Give each changelog post a stable `slug`, its original `created_at` timestamp, and public privacy frontmatter.
