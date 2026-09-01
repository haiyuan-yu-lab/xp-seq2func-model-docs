# xp-seq2func-model docs

Public user documentation for **xp-seq2func-model** exact release **v0.1.0a8**.

Covers the `train_model`, `tune_model`, and `pred_model` CLIs and their
configuration, data, and artifact contracts from the
[code repository](https://github.com/haiyuan-yu-lab/xp-seq2func-model) tag
`v0.1.0a8`. Source installation requires repository access and authentication.

## Local preview

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/mkdocs serve
```

## Checks

Docs-only validation (strict MkDocs build, internal links, Draft 2020-12
schemas, inline JSON examples, and content markers):

```bash
make check
# or
./scripts/check_docs.sh
```

## Build

```bash
.venv/bin/mkdocs build --strict
```

Pushing `main` deploys the site via GitHub Pages (see `.github/workflows/pages.yml`).
