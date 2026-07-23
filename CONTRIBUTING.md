# Contributing

Create documentation changes on a branch based on `v3`. Keep content in English and use active voice, second person, and concise sentences.

## Before submitting changes

1. Run `python3 scripts/validate_docs.py`.
2. Confirm all internal guide links use `/docs/<slug>`.
3. Keep every page listed in its category `_order.yaml` file.
4. Update `reference/apiscalevid-v2openapi.json` when the public API contract changes.

Do not edit generated files under `reference/Scalev API/` or `reference/ReadMeConfig/` by hand. ReadMe owns those files.
