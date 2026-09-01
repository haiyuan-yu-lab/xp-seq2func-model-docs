#!/usr/bin/env bash
# Run the full docs-only validation suite (no model package import).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -x "$ROOT/.venv/bin/python" ]]; then
  PYTHON="$ROOT/.venv/bin/python"
elif [[ -x "$ROOT/../.venv/bin/python" ]]; then
  PYTHON="$ROOT/../.venv/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

echo "==> Using Python: $PYTHON"
echo "==> Content checks"
"$PYTHON" scripts/check_content.py --docs-dir docs

echo "==> Schema checks"
"$PYTHON" scripts/check_schemas.py --docs-dir docs

echo "==> Inline JSON example checks"
"$PYTHON" scripts/check_inline_json.py --docs-dir docs

echo "==> LLM corpus drift check"
"$PYTHON" scripts/generate_llms.py --check

echo "==> Strict MkDocs build"
"$PYTHON" -m mkdocs build --strict

echo "==> Internal link checks"
"$PYTHON" scripts/check_links.py --site-dir site

echo "All docs checks passed."
