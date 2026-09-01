# Install

Install instructions for exact release **v0.1.0a9**.

## Requirements

- Python **≥ 3.10**
- A working **CUDA** PyTorch install (the CLIs require a CUDA device at runtime)
- Runtime dependencies install with the package: `numpy`, `torch`, `wandb`,
  `captum`
- **Repository access and authentication** for the code repository (this alpha
  is not anonymously installable)

## Access prerequisite

**v0.1.0a9** is not published to PyPI and is not available for anonymous
download. Source installation requires access to the
[code repository](https://github.com/haiyuan-yu-lab/xp-seq2func-model) and a
working GitHub authentication method (for example SSH keys or a personal access
token) that can read that repository.

If you cannot clone or fetch the repository, request access from the
maintainers before attempting installation.

## Install from the v0.1.0a9 tag

Clone the authenticated repository, check out the release tag, then install:

```bash
# SSH (typical for accounts with repository access)
git clone git@github.com:haiyuan-yu-lab/xp-seq2func-model.git
cd xp-seq2func-model
git checkout v0.1.0a9
pip install -e .
```

HTTPS clone with credentials also works when your Git client is configured for
GitHub authentication:

```bash
git clone https://github.com/haiyuan-yu-lab/xp-seq2func-model.git
cd xp-seq2func-model
git checkout v0.1.0a9
pip install -e .
```

Use a non-editable `pip install .` from the same checked-out tree if you prefer
a non-editable install.

## Verify

```bash
train_model --help
tune_model --help
pred_model --help
```

## CUDA note

All three CLIs call into CUDA and fail if no CUDA device is available. For
`tune_model`, set `CUDA_VISIBLE_DEVICES` to the device tokens you want agents
to use (comma-separated, non-empty, no duplicates).

## Next steps

- [Quickstart](getting-started/quickstart.md)
- [Core concepts](concepts.md)
- [Compatibility](reference/compatibility.md)
