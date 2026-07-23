# Contributing

Create documentation changes on a branch based on `v3`. Keep content in English and use active voice, second person, and concise sentences.

## Before submitting changes

1. If the API contract changed, run `python3 scripts/sync_openapi_reference.py`.
2. Run `python3 scripts/sync_openapi_reference.py --check`.
3. Run `python3 scripts/validate_docs.py`.
4. Confirm all internal guide links use `/docs/<slug>`.
5. Keep every page listed in its category `_order.yaml` file.
6. Update `reference/apiscalevid-v2openapi.json` when the public API contract changes.

Do not edit files under `reference/Scalev API/` by hand. Regenerate them from OpenAPI. Do not edit `reference/ReadMeConfig/` unless you intend to change ReadMe's API reference settings.
