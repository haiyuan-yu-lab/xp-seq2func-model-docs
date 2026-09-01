#!/usr/bin/env python3
"""Content checks for the v0.1.0a8 documentation foundation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

VERSION = "v0.1.0a8"
BINARY_SUFFIXES = {
    ".npy",
    ".npz",
    ".h5",
    ".hdf5",
    ".pth",
    ".pt",
    ".ckpt",
    ".bin",
    ".pkl",
    ".pickle",
    ".joblib",
    ".parquet",
    ".feather",
    ".arrow",
    ".zip",
    ".tar",
    ".gz",
    ".bz2",
    ".xz",
    ".7z",
    ".sqlite",
    ".db",
    ".onnx",
    ".safetensors",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_contains(path: Path, needle: str, errors: list[str]) -> None:
    text = read(path)
    if needle not in text:
        errors.append(f"{path.as_posix()}: missing required text {needle!r}")


def check_version_markers(docs_dir: Path, errors: list[str]) -> None:
    for rel in (
        "index.md",
        "install.md",
        "reference/compatibility.md",
        "reference/glossary.md",
    ):
        path = docs_dir / rel
        if not path.is_file():
            errors.append(f"missing required page: {rel}")
            continue
        require_contains(path, VERSION, errors)


def check_install_wording(docs_dir: Path, errors: list[str]) -> None:
    path = docs_dir / "install.md"
    if not path.is_file():
        errors.append("missing required page: install.md")
        return
    text = read(path)
    lowered = text.lower()

    if "repository access" not in lowered and "authenticated" not in lowered:
        errors.append(
            "install.md: must state that source installation requires "
            "repository access and authentication"
        )
    if "authentication" not in lowered and "authenticated" not in lowered:
        errors.append(
            "install.md: must mention authentication for repository access"
        )

    # Reject positive availability claims; negative wording is fine.
    for match in re.finditer(
        r"\banonymously\s+(available|installable|downloadable)\b"
        r"|\bavailable\s+anonymously\b"
        r"|\banonymous\s+public\s+(access|availability|install|download)\b",
        text,
        flags=re.IGNORECASE,
    ):
        window_start = max(0, match.start() - 24)
        prefix = text[window_start:match.start()].lower()
        if re.search(r"\bnot\b", prefix):
            continue
        errors.append("install.md: must not claim anonymous availability")
        break

    forbidden_patterns = [
        (
            r"pip install\s+[\"']?git\+https://github\.com/haiyuan-yu-lab/xp-seq2func-model",
            "install.md: must not present anonymous git+https pip install as the path",
        ),
        (
            r"available on pypi",
            "install.md: must not claim PyPI availability",
        ),
        (
            r"install from pypi",
            "install.md: must not claim PyPI availability",
        ),
        (
            r"\bwithout\s+authentication\b",
            "install.md: must not claim installation works without authentication",
        ),
        (
            r"\bno\s+authentication\s+(required|needed)\b",
            "install.md: must not claim installation works without authentication",
        ),
    ]
    for pattern, message in forbidden_patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            errors.append(message)

    if "no pypi" not in lowered and "not published to pypi" not in lowered:
        # Soft requirement: explicitly deny PyPI for this alpha.
        if "pypi" not in lowered:
            errors.append("install.md: should state there is no PyPI publish")


def check_public_interface(docs_dir: Path, errors: list[str]) -> None:
    index = docs_dir / "index.md"
    if not index.is_file():
        return
    text = read(index).lower()
    if "public interface" not in text and "supported public interface" not in text:
        errors.append(
            "index.md: must state the supported public interface boundary"
        )
    if "python import" not in text and "python imports" not in text:
        errors.append(
            "index.md: must clarify that Python imports are not the supported API"
        )


def check_no_binaries(docs_dir: Path, errors: list[str]) -> None:
    for path in docs_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            errors.append(
                f"binary fixture not allowed under docs/: {path.relative_to(docs_dir)}"
            )


def check_preserved_urls(docs_dir: Path, errors: list[str]) -> None:
    required = [
        "index.md",
        "install.md",
        "concepts.md",
        "profiles.md",
        "formats.md",
        "config.md",
        "faq.md",
        "cli/index.md",
        "cli/train_model.md",
        "cli/tune_model.md",
        "cli/pred_model.md",
    ]
    for rel in required:
        if not (docs_dir / rel).is_file():
            errors.append(f"preserved URL page missing: {rel}")


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

    errors: list[str] = []
    check_preserved_urls(docs_dir, errors)
    check_version_markers(docs_dir, errors)
    check_install_wording(docs_dir, errors)
    check_public_interface(docs_dir, errors)
    check_no_binaries(docs_dir, errors)

    if errors:
        print(f"Content check failed ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1

    print("Content check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
