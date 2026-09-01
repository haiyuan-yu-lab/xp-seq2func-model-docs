#!/usr/bin/env python3
"""Validate docs/schemas as Draft 2020-12 and resolve local $ref targets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012

SITE_ORIGIN = "https://haiyuan-yu-lab.github.io/xp-seq2func-model-docs"


def collect_schema_files(schemas_root: Path) -> list[Path]:
    return sorted(schemas_root.rglob("*.schema.json"))


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def published_path_for(schema_path: Path, docs_dir: Path) -> str:
    rel = schema_path.relative_to(docs_dir).as_posix()
    return f"{SITE_ORIGIN}/{rel}"


def local_path_for_ref(ref: str, base_dir: Path, docs_dir: Path) -> Path | None:
    """Return the on-disk schema file for a local $ref (fragment ignored)."""
    parsed = urlparse(ref)
    if parsed.scheme in ("http", "https"):
        if not ref.startswith(SITE_ORIGIN + "/"):
            return None
        return docs_dir / parsed.path.lstrip("/")
    if ref.startswith("#") or not parsed.path:
        return None
    # Relative local refs resolve from the referencing schema's directory.
    return (base_dir / parsed.path).resolve()


def iter_refs(node: Any) -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(iter_refs(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(iter_refs(item))
    return found


def build_registry(schema_files: list[Path], docs_dir: Path) -> Registry:
    registry = Registry()
    for path in schema_files:
        contents = load_json(path)
        resource = Resource.from_contents(contents, default_specification=DRAFT202012)
        uri = contents.get("$id") or published_path_for(path, docs_dir)
        registry = registry.with_resource(uri, resource)
        # Also register under the published path so absolute site URLs resolve.
        published = published_path_for(path, docs_dir)
        if published != uri:
            registry = registry.with_resource(published, resource)
    return registry


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=Path("docs"),
        help="MkDocs docs_dir (default: docs)",
    )
    args = parser.parse_args(argv)
    docs_dir = args.docs_dir.resolve()
    schemas_root = docs_dir / "schemas"
    if not schemas_root.is_dir():
        print(f"ERROR: schemas directory not found: {schemas_root}", file=sys.stderr)
        return 1

    schema_files = collect_schema_files(schemas_root)
    if not schema_files:
        print(f"ERROR: no *.schema.json files under {schemas_root}", file=sys.stderr)
        return 1

    errors: list[str] = []
    registry = build_registry(schema_files, docs_dir)

    for path in schema_files:
        rel = path.relative_to(docs_dir)
        try:
            schema = load_json(path)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel}: invalid JSON ({exc})")
            continue

        schema_id = schema.get("$id")
        expected_id = published_path_for(path, docs_dir)
        if schema_id != expected_id:
            errors.append(
                f"{rel}: $id must be {expected_id!r}, found {schema_id!r}"
            )

        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as exc:
            errors.append(f"{rel}: not a valid Draft 2020-12 schema ({exc.message})")
            continue

        for ref in iter_refs(schema):
            if ref.startswith("#"):
                continue
            local = local_path_for_ref(ref, path.parent, docs_dir)
            if local is None:
                # External non-site refs are out of scope for local resolution.
                if ref.startswith(("http://", "https://")):
                    errors.append(f"{rel}: unresolved non-local $ref {ref!r}")
                continue
            if not local.exists():
                errors.append(f"{rel}: $ref target missing on disk: {ref}")
                continue
            # Confirm registry can resolve absolute site IDs and same-dir relatives.
            try:
                base = schema.get("$id") or published_path_for(path, docs_dir)
                registry.resolver(base_uri=base).lookup(ref)
            except (Unresolvable, KeyError, AttributeError) as exc:
                errors.append(f"{rel}: registry could not resolve $ref {ref!r} ({exc})")

        # Instantiate a validator to ensure the schema is usable with the registry.
        try:
            Draft202012Validator(schema, registry=registry)
        except Exception as exc:  # noqa: BLE001 - surface any construction failure
            errors.append(f"{rel}: Draft202012Validator failed ({exc})")

    if errors:
        print(f"Schema check failed ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    print(f"Schema check passed ({len(schema_files)} schema file(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
