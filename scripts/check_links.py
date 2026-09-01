#!/usr/bin/env python3
"""Check internal links in the built MkDocs site."""

from __future__ import annotations

import argparse
import re
import sys
import urllib.parse
from pathlib import Path

from bs4 import BeautifulSoup

SKIP_SCHEMES = ("http:", "https:", "mailto:", "tel:", "javascript:", "data:")
SKIP_PAGES = {"404.html"}


def iter_html_files(site_dir: Path) -> list[Path]:
    return sorted(
        p
        for p in site_dir.rglob("*.html")
        if p.is_file() and p.name not in SKIP_PAGES
    )


def site_prefix_from_mkdocs(mkdocs_yml: Path) -> str:
    if not mkdocs_yml.is_file():
        return ""
    text = mkdocs_yml.read_text(encoding="utf-8")
    match = re.search(r"^site_url:\s*(\S+)", text, flags=re.MULTILINE)
    if not match:
        return ""
    parsed = urllib.parse.urlparse(match.group(1).strip().strip("\"'"))
    return parsed.path.rstrip("/")


def normalize_absolute_path(path: str, site_prefix: str) -> str:
    if site_prefix and (path == site_prefix or path.startswith(site_prefix + "/")):
        path = path[len(site_prefix) :] or "/"
    return path


def resolve_href(
    page: Path, href: str, site_dir: Path, site_prefix: str
) -> Path | None:
    parsed = urllib.parse.urlparse(href)
    if parsed.scheme or href.startswith("//"):
        return None
    path = parsed.path
    if not path:
        return page  # fragment-only link on same page
    if path.startswith("/"):
        path = normalize_absolute_path(path, site_prefix)
        if path in ("", "/"):
            target = site_dir / "index.html"
        else:
            target = site_dir / path.lstrip("/")
    else:
        target = (page.parent / path).resolve()
    site_root = site_dir.resolve()
    try:
        target.relative_to(site_root)
    except ValueError:
        return target
    if target.is_dir():
        index = target / "index.html"
        return index if index.exists() else target
    if not target.exists() and target.suffix == "":
        as_dir = target / "index.html"
        if as_dir.exists():
            return as_dir
        as_html = target.with_suffix(".html")
        if as_html.exists():
            return as_html
    return target


def fragment_exists(page: Path, fragment: str) -> bool:
    if not fragment:
        return True
    soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
    if soup.find(id=fragment):
        return True
    # Named anchors still appear in some themes.
    return soup.find("a", attrs={"name": fragment}) is not None


def check_page(page: Path, site_dir: Path, site_prefix: str) -> list[str]:
    errors: list[str] = []
    soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
    for tag in soup.find_all(["a", "link", "img", "script", "source"]):
        attr = "href" if tag.name in ("a", "link") else "src"
        value = tag.get(attr)
        if not value:
            continue
        lower = value.lower()
        if lower.startswith(SKIP_SCHEMES) or lower.startswith("//"):
            continue
        parsed = urllib.parse.urlparse(value)
        if value.startswith("#"):
            if not fragment_exists(page, parsed.fragment):
                rel_page = page.relative_to(site_dir)
                errors.append(f"{rel_page}: broken fragment -> {value}")
            continue
        target = resolve_href(page, value, site_dir, site_prefix)
        if target is None:
            continue
        if not target.exists():
            rel_page = page.relative_to(site_dir)
            errors.append(f"{rel_page}: broken {attr} -> {value}")
            continue
        if parsed.fragment and target.suffix == ".html":
            if not fragment_exists(target, parsed.fragment):
                rel_page = page.relative_to(site_dir)
                errors.append(
                    f"{rel_page}: broken fragment in {attr} -> {value}"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site-dir",
        type=Path,
        default=Path("site"),
        help="Built site directory (default: site)",
    )
    parser.add_argument(
        "--mkdocs-yml",
        type=Path,
        default=Path("mkdocs.yml"),
        help="MkDocs config used to discover site_url path prefix",
    )
    parser.add_argument(
        "--site-prefix",
        default=None,
        help="Optional absolute URL path prefix (overrides mkdocs.yml site_url)",
    )
    args = parser.parse_args(argv)
    site_dir = args.site_dir.resolve()
    if not site_dir.is_dir():
        print(f"ERROR: site directory not found: {site_dir}", file=sys.stderr)
        return 1

    site_prefix = (
        args.site_prefix
        if args.site_prefix is not None
        else site_prefix_from_mkdocs(args.mkdocs_yml)
    )

    errors: list[str] = []
    pages = iter_html_files(site_dir)
    for page in pages:
        errors.extend(check_page(page, site_dir, site_prefix))

    if errors:
        print(f"Internal link check failed ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    print(f"Internal link check passed ({len(pages)} HTML pages).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
