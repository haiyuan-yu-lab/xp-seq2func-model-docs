# Concepts

## EncoderPredictor

The only top-level model type in **0.1.0a2** is `EncoderPredictor`.

It composes:

1. An **encoder** (`ConvEncoder`) that maps one-hot sequence tensors to an
   embedding
2. Optional **embedding trimming** (integer ≥ 0) applied to that embedding
3. One or more **predictor heads** (`ClassPredictor`), each with its own loss
   weight (`alpha`) and loss object

Nested components (`ConvEncoder`, `ClassPredictor`) are nestable-only: they
cannot be set as the top-level `model_type` on a CLI config.

## Workflows

| Workflow | CLI | Typical inputs |
| --- | --- | --- |
| Fixed-hparam train | `train_model` | train config JSON + hparams JSON |
| Sweep / search | `tune_model` | tune config JSON + tune-space JSON |
| Inference | `pred_model` | test config JSON + checkpoint + hparams JSON |

Train and tune both write checkpoints under `--opath`. Prediction loads a
parent `.pth` checkpoint and writes per-head `.pred_class.npy` arrays.

## Weights & Biases

- **Train**: optional W&B logging (`wandb.mode` may be `online`, `offline`, or
  `disabled`)
- **Tune**: W&B sweeps only (`wandb.mode` is `online` or `offline`); agents run
  concurrent workers constrained by `CUDA_VISIBLE_DEVICES`

Tune optimizes on validation loss. Epoch metrics expose `val_loss` with a W&B
`min` summary for sweep selection.
