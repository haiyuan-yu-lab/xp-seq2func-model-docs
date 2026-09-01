#!/usr/bin/env python3
"""Validate complete fenced JSON examples associated with docs schemas.

Convention: place an HTML comment immediately before a ```json fence:

    <!-- schema: schemas/v0.1.0a9/example-name.schema.json -->
    ```json
    { ... }
    ```

The path is relative to the MkDocs docs_dir. Incomplete or illustrative
fragments should omit the comment so they are skipped.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

SITE_ORIGIN = "https://haiyuan-yu-lab.github.io/xp-seq2func-model-docs"

SCHEMA_COMMENT = re.compile(
    r"<!--\s*schema:\s*(?P<path>[^\s]+?)\s*-->\s*\n```json\n(?P<body>.*?)```",
    re.DOTALL,
)


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def published_path_for(schema_path: Path, docs_dir: Path) -> str:
    rel = schema_path.relative_to(docs_dir).as_posix()
    return f"{SITE_ORIGIN}/{rel}"


def build_registry(docs_dir: Path) -> Registry:
    registry = Registry()
    for path in sorted((docs_dir / "schemas").rglob("*.schema.json")):
        contents = load_json(path)
        resource = Resource.from_contents(contents, default_specification=DRAFT202012)
        uri = contents.get("$id") or published_path_for(path, docs_dir)
        registry = registry.with_resource(uri, resource)
        published = published_path_for(path, docs_dir)
        if published != uri:
            registry = registry.with_resource(published, resource)
    return registry


def resolve_schema_path(raw: str, docs_dir: Path) -> Path:
    parsed = urlparse(raw)
    if parsed.scheme in ("http", "https"):
        if not raw.startswith(SITE_ORIGIN + "/"):
            raise ValueError(f"schema URL is not under the docs site: {raw}")
        return docs_dir / raw[len(SITE_ORIGIN) + 1 :]
    return docs_dir / raw


def find_examples(markdown_files: list[Path]) -> list[tuple[Path, str, str]]:
    found: list[tuple[Path, str, str]] = []
    for path in markdown_files:
        text = path.read_text(encoding="utf-8")
        for match in SCHEMA_COMMENT.finditer(text):
            found.append((path, match.group("path"), match.group("body")))
    return found


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
    if not docs_dir.is_dir():
        print(f"ERROR: docs directory not found: {docs_dir}", file=sys.stderr)
        return 1

    markdown_files = sorted(docs_dir.rglob("*.md"))
    examples = find_examples(markdown_files)
    if not examples:
        print(
            "ERROR: no schema-associated JSON examples found "
            "(expected <!-- schema: ... --> before ```json fences)",
            file=sys.stderr,
        )
        return 1

    registry = build_registry(docs_dir)
    errors: list[str] = []

    for md_path, schema_ref, body in examples:
        rel_md = md_path.relative_to(docs_dir)
        try:
            schema_path = resolve_schema_path(schema_ref, docs_dir)
        except ValueError as exc:
            errors.append(f"{rel_md}: {exc}")
            continue
        if not schema_path.is_file():
            errors.append(f"{rel_md}: schema not found: {schema_ref}")
            continue
        try:
            instance = json.loads(body)
        except json.JSONDecodeError as exc:
            errors.append(f"{rel_md}: example is not valid JSON ({exc})")
            continue
        schema = load_json(schema_path)
        validator = Draft202012Validator(schema, registry=registry)
        try:
            validator.validate(instance)
        except ValidationError as exc:
            errors.append(
                f"{rel_md}: example failed schema {schema_ref}: {exc.message}"
            )

    if errors:
        print(f"Inline JSON check failed ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    print(f"Inline JSON check passed ({len(examples)} example(s)).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
