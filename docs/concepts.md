# Concepts

## EncoderPredictor

The only top-level model type in **0.1.0a6** is `EncoderPredictor`.

It composes:

1. An **encoder** — either `ConvEncoder` or `ConvSelfAttEncoder` — that maps
   one-hot sequence tensors to an embedding
2. Optional **embedding trimming** (integer ≥ 0) applied to that embedding
3. One or more **predictor heads** — each head is either `ClassPredictor`
   (classification) or `RegressPredictor` (scalar regression), with its own
   loss weight (`alpha`) and loss object

Nested components (`ConvEncoder`, `ConvSelfAttEncoder`, `ClassPredictor`,
`RegressPredictor`) are nestable-only: they cannot be set as the top-level
`model_type` on a CLI config.

## Learning rates and freezing

Hyperparameters include a top-level `learning_rate` and nested rates on the
encoder and each predictor head.

| Location | Allowed values | Effect of `0` |
| --- | --- | --- |
| Top-level `learning_rate` | number **> 0** | Not allowed |
| Nested module `learning_rate` (encoder or head) | number **≥ 0** | Freezes that module (`requires_grad=False`); it is omitted from Adam |

Distinct positive rates become separate Adam param groups. Freezing every
trainable module fails closed when building the optimizer.

## Init from a checkpoint (transfer learning)

Train and tune configs may include optional `init_checkpoint` to load selected
catalogued modules from an existing `.pth` before training (for example, reuse
an encoder while randomly initializing a new head). Pair with nested
`learning_rate: 0` to freeze those modules. See
[Config](config.md#init_checkpoint-train--tune).

## Workflows

| Workflow | CLI | Typical inputs |
| --- | --- | --- |
| Fixed-hparam train | `train_model` | train config JSON + hparams JSON |
| Sweep / search | `tune_model` | tune config JSON + tune-space JSON |
| Inference | `pred_model` | test config JSON + checkpoint + hparams JSON |

Train and tune both write checkpoints under `--opath` (parent and per-module
artifacts). Prediction loads a parent `.pth` checkpoint and writes per-head
arrays (`.pred_class.npy` for `ClassPredictor`, `.pred.npy` for
`RegressPredictor`). With `--attribution`, it also writes per-head attribution
arrays.

## Weights & Biases

- **Train**: optional W&B logging (`wandb.mode` may be `online`, `offline`, or
  `disabled`)
- **Tune**: W&B sweeps only (`wandb.mode` is `online` or `offline`); agents run
  concurrent workers constrained by `CUDA_VISIBLE_DEVICES`

Tune optimizes on validation loss. Epoch metrics expose `val_loss` with a W&B
`min` summary for sweep selection.
