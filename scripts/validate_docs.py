#!/usr/bin/env python3
"""Validate the Git-backed ReadMe documentation source."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OPENAPI = ROOT / "reference" / "apiscalevid-v2openapi.json"
API_REFERENCE = ROOT / "reference" / "Scalev API"
MINTLIFY_TAGS = re.compile(r"</?(?:Columns|Card|Warning|Update)\b")
INTERNAL_LINK = re.compile(r"\]\(/docs/([^#?)\s]+)")


def ordered_values(path: Path) -> list[str]:
    values = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- "):
            values.append(line[2:].strip().strip('"').strip("'"))
    return values


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    operation_ids: list[str] = []
    pages = sorted(DOCS.glob("*/*.md"))
    slugs = [path.stem for path in pages]
    known_slugs = set(slugs)

    if len(slugs) != len(known_slugs):
        duplicates = sorted({slug for slug in slugs if slugs.count(slug) > 1})
        fail(errors, f"Duplicate global page slugs: {', '.join(duplicates)}")

    for path in pages:
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        if not match:
            fail(errors, f"{relative}: missing YAML frontmatter")
            continue
        frontmatter = match.group(1)
        if not re.search(r"^title:\s*.+$", frontmatter, re.MULTILINE):
            fail(errors, f"{relative}: missing title")
        if not re.search(r"^excerpt:\s*.+$", frontmatter, re.MULTILINE):
            fail(errors, f"{relative}: missing excerpt")
        if MINTLIFY_TAGS.search(text):
            fail(errors, f"{relative}: contains a Mintlify-only component")
        if re.search(r"(?<![A-Za-z0-9_-])/en(?:/|\b)", text):
            fail(errors, f"{relative}: contains a legacy /en path")
        for slug in INTERNAL_LINK.findall(text):
            if slug not in known_slugs:
                fail(errors, f"{relative}: unresolved internal link /docs/{slug}")

    root_order = ordered_values(DOCS / "_order.yaml")
    categories = sorted(path.name for path in DOCS.iterdir() if path.is_dir())
    if sorted(root_order) != categories:
        fail(errors, "docs/_order.yaml does not list every category exactly once")

    for category in categories:
        directory = DOCS / category
        order = ordered_values(directory / "_order.yaml")
        category_slugs = sorted(path.stem for path in directory.glob("*.md"))
        if sorted(order) != category_slugs:
            fail(errors, f"docs/{category}/_order.yaml does not list every page exactly once")

    try:
        spec = json.loads(OPENAPI.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"OpenAPI file is unreadable: {exc}")
        spec = {}

    if spec:
        if not str(spec.get("openapi", "")).startswith("3."):
            fail(errors, "OpenAPI source is not an OpenAPI 3.x document")
        paths = spec.get("paths", {})
        if not paths:
            fail(errors, "OpenAPI source has no paths")
        for path_item in paths.values():
            if not isinstance(path_item, dict):
                continue
            for operation in path_item.values():
                if isinstance(operation, dict) and operation.get("operationId"):
                    operation_ids.append(operation["operationId"])
        duplicate_ids = sorted({item for item in operation_ids if operation_ids.count(item) > 1})
        if duplicate_ids:
            fail(errors, f"Duplicate OpenAPI operationIds: {', '.join(duplicate_ids)}")

    reference_pages = sorted(
        path for path in API_REFERENCE.glob("*/*.md") if path.name != "index.md"
    )
    generated_ids: list[str] = []
    for path in reference_pages:
        match = re.search(r"^  operationId:\s*(\S+)\s*$", path.read_text(encoding="utf-8"), re.MULTILINE)
        if not match:
            fail(errors, f"{path.relative_to(ROOT)}: missing API operationId")
            continue
        generated_ids.append(match.group(1))
    missing_ids = sorted(set(operation_ids) - set(generated_ids))
    stale_ids = sorted(set(generated_ids) - set(operation_ids))
    if missing_ids:
        fail(errors, f"API reference is missing {len(missing_ids)} OpenAPI operations")
    if stale_ids:
        fail(errors, f"API reference contains {len(stale_ids)} stale operations")
    if len(generated_ids) != len(set(generated_ids)):
        fail(errors, "API reference contains duplicate operationId pages")

    if errors:
        print("Documentation validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        f"Validated {len(pages)} guide pages, {len(categories)} categories, "
        f"{len(spec.get('paths', {}))} OpenAPI paths, and {len(generated_ids)} reference operations."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
