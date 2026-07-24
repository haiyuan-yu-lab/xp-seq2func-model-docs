# Install

## Requirements

- Python **≥ 3.10**
- A working **CUDA** PyTorch install (the CLIs require a CUDA device at runtime)
- Runtime dependencies install with the package: `numpy`, `torch`, `wandb`,
  `captum`

## Install from the v0.1.0a5 tag

There is no PyPI publish for this alpha. Install from the tagged code repository:

```bash
pip install "git+https://github.com/haiyuan-yu-lab/xp-seq2func-model.git@v0.1.0a5"
```

Editable install from a local clone:

```bash
git clone https://github.com/haiyuan-yu-lab/xp-seq2func-model.git
cd xp-seq2func-model
git checkout v0.1.0a5
pip install -e .
```

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
