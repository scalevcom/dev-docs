# Documentation project instructions

## About this project

- This is the English Scalev developer documentation published with ReadMe.
- Pages are Markdown files with YAML frontmatter under `docs/`.
- Navigation order lives in `_order.yaml` files.
- The API definition is `reference/apiscalevid-v2openapi.json`; its filename is historical, but its contents are the current API v3 contract.
- ReadMe manages generated files under `reference/Scalev API/` and `reference/ReadMeConfig/`.
- Run `python3 scripts/validate_docs.py` before committing.

## Style

- Use active voice and second person ("you").
- Keep sentences concise and use sentence case for headings.
- Bold UI labels and use code formatting for commands, paths, fields, and code references.
- Keep guide links in the `/docs/<slug>` form.
- Write new documentation in English only.

## Content boundaries

- Document public developer workflows and public API behavior.
- Do not document internal administration or implementation details.
- Do not manually edit ReadMe-generated API reference pages.
