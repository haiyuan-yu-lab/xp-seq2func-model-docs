# Quickstart

Text-only orientation for **v0.1.0a8**. This page uses placeholder paths only;
the documentation does not ship datasets or checkpoints.

## Prerequisites

1. Complete [Install](../install.md) (requires repository access and
   authentication).
2. Confirm a CUDA device is visible to the process.
3. Prepare your own one-hot sequence arrays, labels, and JSON configs. See
   [Formats](../formats.md) and [Configuration](../config.md).

## Typical command shapes

Train with fixed hyperparameters:

```bash
train_model \
  --config /path/to/train_config.json \
  --hparams /path/to/hparams.json \
  --opath /path/to/train_outdir \
  --verbosity 1
```

Tune with a search space (requires `CUDA_VISIBLE_DEVICES`):

```bash
export CUDA_VISIBLE_DEVICES=0
tune_model \
  --config /path/to/tune_config.json \
  --tune-space /path/to/tune_space.json \
  --opath /path/to/tune_outdir \
  --verbosity 1
```

Predict from a parent checkpoint:

```bash
pred_model \
  --config /path/to/pred_config.json \
  --hparams /path/to/hparams.json \
  --checkpoint /path/to/parent_checkpoint.pth \
  --opath /path/to/pred_outdir \
  --verbosity 1
```

Exact flags and defaults for the installed build are authoritative via
`--help`. See the [CLI overview](../cli/index.md).

## Next reading

- [Train to predict](../workflows/train-to-predict.md) — full train →
  checkpoint → `pred_model` → output arrays path
- [Tuning workflow](../workflows/tuning.md)
- [`pred_model`](../cli/pred_model.md)
- [Prediction configuration](../configuration/prediction.md)
- [Core concepts](../concepts.md)
- [Compatibility](../reference/compatibility.md)
