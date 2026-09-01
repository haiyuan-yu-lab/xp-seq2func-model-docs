#!/usr/bin/env python3
"""Generate docs/llms.txt and docs/llms-full.txt for the documentation site.

llms.txt
    Concise curated Markdown map (llmstxt.org style) with absolute links and
    one-line descriptions. Never writes a singular ``llm.txt`` alias.

llms-full.txt
    Concatenates canonical source Markdown in ``mkdocs.yml`` navigation order
    (depth-first). Exclusion rules:

    - Include only Markdown pages listed in ``nav`` (canonical prose).
    - Exclude generated LLM outputs themselves (``llms.txt``, ``llms-full.txt``).
    - Exclude JSON Schema snapshot bodies under ``schemas/`` (discoverable from
      prose and the schema index; not duplicated here).
    - Exclude built ``site/`` HTML, MkDocs theme boilerplate, and repository
      files outside the MkDocs ``docs/`` directory (for example ``README.md``).
    - Exclude any singular ``llm.txt`` alias (never produced).

Regenerate with ``--write``. Verify committed artifacts with ``--check``.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml

SITE_ORIGIN = "https://haiyuan-yu-lab.github.io/xp-seq2func-model-docs"
VERSION = "v0.1.0a8"

# Curated map entries: (section, title, docs-relative path, one-line description).
# Keep this list intentional and short; do not auto-dump the full nav.
CURATED: list[tuple[str, str, str, str]] = [
    (
        "Getting Started",
        "Home",
        "index.md",
        "Release scope and supported public interface for the CLIs",
    ),
    (
        "Getting Started",
        "Installation",
        "install.md",
        "Authenticated source install for the exact release tag",
    ),
    (
        "Getting Started",
        "Quickstart",
        "getting-started/quickstart.md",
        "Text-only train-to-predict command shapes with placeholder paths",
    ),
    (
        "Getting Started",
        "Core concepts",
        "concepts.md",
        "EncoderPredictor composition, freezing, init, and W&B roles",
    ),
    (
        "CLI Reference",
        "CLI overview",
        "cli/index.md",
        "The three console commands and shared flags",
    ),
    (
        "CLI Reference",
        "train_model",
        "cli/train_model.md",
        "Fixed-hparam training flags, inputs, outputs, and failures",
    ),
    (
        "CLI Reference",
        "tune_model",
        "cli/tune_model.md",
        "W&B sweep tuning flags, agents, trials, and failures",
    ),
    (
        "CLI Reference",
        "pred_model",
        "cli/pred_model.md",
        "Prediction and optional Captum attribution flags and outputs",
    ),
    (
        "Workflows",
        "Train to predict",
        "workflows/train-to-predict.md",
        "Connect train artifacts to prediction",
    ),
    (
        "Workflows",
        "Tuning",
        "workflows/tuning.md",
        "Sweep creation, GPU pinning, and W&B requirements",
    ),
    (
        "Workflows",
        "Initialization and freezing",
        "workflows/initialization-and-freezing.md",
        "Selective checkpoint init and nested learning-rate freezing",
    ),
    (
        "Workflows",
        "Multi-source data",
        "workflows/multi-source-data.md",
        "Parallel sources, source_fracs, and alignment invariants",
    ),
    (
        "Workflows",
        "Profile masks",
        "workflows/profile-masks.md",
        "Positional validity masks for profile loss and Pearson",
    ),
    (
        "Workflows",
        "Attribution",
        "workflows/attribution.md",
        "Attribution methods, target grammar, and legacy mode",
    ),
    (
        "Models",
        "Model composition",
        "models/composition.md",
        "Top-level EncoderPredictor and nestable encoders/heads",
    ),
    (
        "Models",
        "Profile reconstruction",
        "profiles.md",
        "ProfilePredictor tracks, bins, counts, masks, and artifacts",
    ),
    (
        "Data Contracts",
        "Arrays",
        "data/arrays.md",
        "One-hot sequence array shapes, dtypes, and alignment",
    ),
    (
        "Data Contracts",
        "Labels",
        "data/labels.md",
        "Classification, regression, and profile label payloads",
    ),
    (
        "Data Contracts",
        "Formats overview",
        "formats.md",
        "Short cross-cutting array and artifact format summary",
    ),
    (
        "Configuration",
        "Configuration overview",
        "config.md",
        "Shared keys and pointers to command-specific configs",
    ),
    (
        "Configuration",
        "Train config",
        "configuration/train.md",
        "Complete train_model --config contract",
    ),
    (
        "Configuration",
        "Tune config",
        "configuration/tune.md",
        "Complete tune_model --config contract",
    ),
    (
        "Configuration",
        "Prediction config",
        "configuration/prediction.md",
        "Complete pred_model --config contract",
    ),
    (
        "Configuration",
        "Hyperparameters",
        "configuration/hyperparameters.md",
        "Fixed hparams, inheritance, and head wrappers",
    ),
    (
        "Configuration",
        "Tuning spaces",
        "configuration/tuning-spaces.md",
        "tune-space method and leaf parameter forms",
    ),
    (
        "Artifacts",
        "Checkpoints",
        "artifacts/checkpoints.md",
        "Parent and module .pth contracts",
    ),
    (
        "Artifacts",
        "Predictions",
        "artifacts/predictions.md",
        "Per-head prediction array filenames and shapes",
    ),
    (
        "Artifacts",
        "Attributions",
        "artifacts/attributions.md",
        "Legacy and target-qualified attribution filenames",
    ),
    (
        "Reference",
        "Validation and errors",
        "reference/validation-and-errors.md",
        "Fail-closed validation behavior without stable error strings",
    ),
    (
        "Reference",
        "Schemas",
        "reference/schemas.md",
        "Index of release-specific JSON Schema snapshots",
    ),
    (
        "Reference",
        "Compatibility",
        "reference/compatibility.md",
        "Exact-release accuracy promise and non-goals",
    ),
    (
        "Reference",
        "FAQ",
        "faq.md",
        "Short answers for common CLI and contract questions",
    ),
    (
        "Optional",
        "Full documentation corpus",
        "llms-full.txt",
        "Navigation-ordered concatenation of canonical Markdown sources",
    ),
]


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[1]


def load_nav(mkdocs_yml: Path) -> list[Any]:
    data = yaml.safe_load(mkdocs_yml.read_text(encoding="utf-8"))
    nav = data.get("nav")
    if not isinstance(nav, list):
        raise ValueError(f"{mkdocs_yml}: missing nav list")
    return nav


def iter_nav_markdown(nav: list[Any]) -> list[str]:
    """Depth-first list of docs-relative Markdown paths from mkdocs nav."""
    paths: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, str):
            if node.endswith(".md"):
                paths.append(node)
            return
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
            return
        if isinstance(node, list):
            for item in node:
                walk(item)
            return

    walk(nav)
    return paths


def site_url_for(docs_rel: str) -> str:
    """Map a docs-relative path to its published site URL."""
    if docs_rel.endswith(".txt"):
        return f"{SITE_ORIGIN}/{docs_rel}"
    if docs_rel.endswith(".md"):
        stem = docs_rel[: -len(".md")]
        if stem == "index" or stem.endswith("/index"):
            page = stem[: -len("index")] if stem.endswith("index") else ""
            return f"{SITE_ORIGIN}/{page}"
        return f"{SITE_ORIGIN}/{stem}/"
    return f"{SITE_ORIGIN}/{docs_rel}"


def render_llms_txt() -> str:
    lines = [
        f"# xp-seq2func-model",
        "",
        f"> Exact-release **{VERSION}** documentation for the `train_model`, "
        f"`tune_model`, and `pred_model` CLIs and their configuration, data, "
        f"and artifact contracts. Python imports are not a supported API.",
        "",
        f"Site: {SITE_ORIGIN}/",
        "",
    ]
    current_section: str | None = None
    for section, title, rel, description in CURATED:
        if section != current_section:
            if current_section is not None:
                lines.append("")
            lines.append(f"## {section}")
            lines.append("")
            current_section = section
        url = site_url_for(rel)
        lines.append(f"- [{title}]({url}): {description}")
    lines.append("")
    return "\n".join(lines)


def page_banner(docs_rel: str) -> str:
    return (
        f"\n\n{'=' * 72}\n"
        f"# SOURCE: {docs_rel}\n"
        f"# URL: {site_url_for(docs_rel)}\n"
        f"{'=' * 72}\n\n"
    )


def render_llms_full(docs_dir: Path, nav_paths: list[str]) -> str:
    parts = [
        f"# xp-seq2func-model documentation corpus ({VERSION})",
        "",
        "Concatenated canonical Markdown in MkDocs navigation order.",
        "Schema JSON snapshots and site HTML boilerplate are omitted; see",
        f"{SITE_ORIGIN}/reference/schemas/ for schema URLs.",
        "",
    ]
    for rel in nav_paths:
        path = docs_dir / rel
        if not path.is_file():
            raise FileNotFoundError(f"nav page missing: {rel}")
        # Skip if a nav entry ever pointed at generated LLM outputs.
        if path.name in {"llms.txt", "llms-full.txt", "llm.txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        parts.append(page_banner(rel))
        parts.append(text.rstrip())
        parts.append("")
    parts.append("")
    return "\n".join(parts)


def write_artifacts(docs_dir: Path, llms_txt: str, llms_full: str) -> None:
    (docs_dir / "llms.txt").write_text(llms_txt, encoding="utf-8")
    (docs_dir / "llms-full.txt").write_text(llms_full, encoding="utf-8")
    alias = docs_dir / "llm.txt"
    if alias.exists():
        alias.unlink()


def check_artifacts(docs_dir: Path, llms_txt: str, llms_full: str) -> list[str]:
    errors: list[str] = []
    expected = {
        "llms.txt": llms_txt,
        "llms-full.txt": llms_full,
    }
    for name, content in expected.items():
        path = docs_dir / name
        if not path.is_file():
            errors.append(f"missing generated artifact: docs/{name}")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != content:
            errors.append(
                f"docs/{name} is out of date; run "
                "`python scripts/generate_llms.py --write`"
            )
    alias = docs_dir / "llm.txt"
    if alias.exists():
        errors.append("docs/llm.txt must not exist (no singular alias)")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--write",
        action="store_true",
        help="Regenerate docs/llms.txt and docs/llms-full.txt",
    )
    mode.add_argument(
        "--check",
        action="store_true",
        help="Verify committed LLM artifacts match regenerated content",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=None,
        help="Documentation repository root (default: parent of scripts/)",
    )
    args = parser.parse_args(argv)
    root = (args.repo_root or repo_root_from_script()).resolve()
    docs_dir = root / "docs"
    mkdocs_yml = root / "mkdocs.yml"
    if not docs_dir.is_dir():
        print(f"ERROR: docs directory not found: {docs_dir}", file=sys.stderr)
        return 1
    if not mkdocs_yml.is_file():
        print(f"ERROR: mkdocs.yml not found: {mkdocs_yml}", file=sys.stderr)
        return 1

    nav_paths = iter_nav_markdown(load_nav(mkdocs_yml))
    if not nav_paths:
        print("ERROR: no Markdown pages found in mkdocs.yml nav", file=sys.stderr)
        return 1

    # Curated map paths (except the llms-full self-link) must exist.
    for _section, _title, rel, _desc in CURATED:
        if rel.endswith(".txt"):
            continue
        if not (docs_dir / rel).is_file():
            print(f"ERROR: curated page missing: {rel}", file=sys.stderr)
            return 1

    llms_txt = render_llms_txt()
    llms_full = render_llms_full(docs_dir, nav_paths)

    if args.write:
        write_artifacts(docs_dir, llms_txt, llms_full)
        print(
            f"Wrote docs/llms.txt and docs/llms-full.txt "
            f"({len(nav_paths)} nav pages in corpus)."
        )
        return 0

    errors = check_artifacts(docs_dir, llms_txt, llms_full)
    if errors:
        print(f"LLM corpus check failed ({len(errors)} issue(s)):", file=sys.stderr)
        for err in errors:
            print(f"  {err}", file=sys.stderr)
        return 1
    print(
        f"LLM corpus check passed "
        f"(llms.txt + llms-full.txt; {len(nav_paths)} nav pages)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
