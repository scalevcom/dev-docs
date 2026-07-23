#!/usr/bin/env python3
"""Generate ReadMe API reference pages from the checked-in OpenAPI source."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "reference" / "apiscalevid-v2openapi.json"
REFERENCE_ROOT = ROOT / "reference"
API_DIRECTORY = REFERENCE_ROOT / "Scalev API"
HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^a-z0-9_-]+", "-", normalized)
    return normalized.strip("-")


def page_frontmatter(operation_id: str) -> str:
    return "\n".join(
        [
            "---",
            "hidden: false",
            "api:",
            f"  file: {SPEC_PATH.name}",
            f"  operationId: {operation_id}",
            "---",
            "",
        ]
    )


def index_frontmatter(title: str) -> str:
    return "\n".join(
        [
            "---",
            f"title: {json.dumps(title, ensure_ascii=False)}",
            "hidden: false",
            "---",
            "",
        ]
    )


def build_files(spec: dict) -> dict[Path, str]:
    declared_tags = [tag["name"] for tag in spec.get("tags", [])]
    operations_by_tag: dict[str, list[tuple[str, str]]] = {tag: [] for tag in declared_tags}
    seen_ids: set[str] = set()
    seen_slugs: set[str] = set()

    for path_item in spec.get("paths", {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            operation_id = operation.get("operationId")
            tags = operation.get("tags", [])
            if not operation_id:
                raise ValueError("Every API operation must define operationId")
            if len(tags) != 1:
                raise ValueError(f"{operation_id} must have exactly one tag")
            if operation_id in seen_ids:
                raise ValueError(f"Duplicate operationId: {operation_id}")
            operation_slug = slugify(operation_id)
            if operation_slug in seen_slugs:
                raise ValueError(f"Operation slugs collide after normalization: {operation_slug}")
            if tags[0] not in operations_by_tag:
                operations_by_tag[tags[0]] = []
                declared_tags.append(tags[0])
            operations_by_tag[tags[0]].append((operation_slug, operation_id))
            seen_ids.add(operation_id)
            seen_slugs.add(operation_slug)

    files: dict[Path, str] = {}
    tag_slugs: set[str] = set()
    ordered_tag_slugs: list[str] = []
    for tag in declared_tags:
        operations = operations_by_tag.get(tag, [])
        if not operations:
            continue
        tag_slug = slugify(tag)
        if tag_slug in tag_slugs:
            raise ValueError(f"Tag slugs collide after normalization: {tag_slug}")
        tag_slugs.add(tag_slug)
        ordered_tag_slugs.append(tag_slug)
        tag_directory = Path(tag_slug)
        files[tag_directory / "index.md"] = index_frontmatter(tag)
        files[tag_directory / "_order.yaml"] = "".join(f"- {slug}\n" for slug, _ in operations)
        for operation_slug, operation_id in operations:
            files[tag_directory / f"{operation_slug}.md"] = page_frontmatter(operation_id)

    files[Path("_order.yaml")] = "".join(f"- {tag_slug}\n" for tag_slug in ordered_tag_slugs)
    return files


def check_files(expected: dict[Path, str]) -> int:
    actual_paths = {
        path.relative_to(API_DIRECTORY)
        for path in API_DIRECTORY.rglob("*")
        if path.is_file()
    }
    expected_paths = set(expected)
    errors: list[str] = []
    for path in sorted(expected_paths - actual_paths):
        errors.append(f"missing reference file: {path}")
    for path in sorted(actual_paths - expected_paths):
        errors.append(f"unexpected reference file: {path}")
    for path in sorted(expected_paths & actual_paths):
        if (API_DIRECTORY / path).read_text(encoding="utf-8") != expected[path]:
            errors.append(f"stale reference file: {path}")
    if errors:
        print("OpenAPI reference generation check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated {len(expected) - 1} generated API reference files.")
    return 0


def write_files(expected: dict[Path, str]) -> None:
    if API_DIRECTORY.exists():
        shutil.rmtree(API_DIRECTORY)
    for relative_path, content in expected.items():
        path = API_DIRECTORY / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    root_order = REFERENCE_ROOT / "_order.yaml"
    root_order.write_text("- ReadMeConfig\n- Scalev API\n", encoding="utf-8")
    print(f"Generated {len(expected) - 1} API reference files from {SPEC_PATH.name}.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Verify generated files without changing them")
    args = parser.parse_args()
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    expected = build_files(spec)
    if args.check:
        return check_files(expected)
    write_files(expected)
    return 0


if __name__ == "__main__":
    sys.exit(main())
