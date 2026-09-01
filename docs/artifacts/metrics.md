# Metrics

Logged metric namespaces for **v0.1.0a8** training.

## Producers and consumers

| Role | Surface |
| --- | --- |
| Producer | `train_model` (and tune trials) emit epoch metrics |
| Destinations | Process console (verbosity ≥ 1) and Weights & Biases when enabled |
| File artifact | **None** — training does not write a metrics file under `--opath` |
| Consumer | Humans / W&B UI; tune sweeps select on validation loss |

## Early stopping and selection

| Rule | Behavior |
| --- | --- |
| Objective | Minimize combined validation loss `val_loss` |
| Patience | `early_stopping.grace_epochs` epochs without a new best |
| Checkpoint | Best `val_loss` epoch is restored before writing artifacts |
| W&B summary | When a run exists, `val_loss` is registered with summary aggregate `min` |

## Logged names

| Name | Where | Notes |
| --- | --- | --- |
| `train_loss` | console + W&B | Combined training loss for the epoch |
| `val_loss` | console + W&B | Combined validation loss; early-stop / summary target |
| `epoch` | W&B | Epoch index |
| Split-qualified diagnostics | console + W&B | Profile heads may emit additional `train|val:<head>:…` diagnostics |

Scalar classification and regression heads contribute to the combined losses;
they do not require separate public metric filenames. Profile diagnostic names
are documented with [Profiles](../profiles.md). Exact console formatting is not
stabilized.

## W&B mode

Train `wandb.mode` may be `online`, `offline`, or `disabled`. When `disabled`,
metrics still print to the console at verbosity ≥ 1, but no W&B run is created.

Tune `wandb.mode` must be `online` or `offline` (sweeps only). See
[Tuning workflow](../workflows/tuning.md).

## Related pages

- [`train_model`](../cli/train_model.md)
- [`tune_model`](../cli/tune_model.md)
- [Train configuration](../configuration/train.md)
- [Tune configuration](../configuration/tune.md)
- [Concepts: Weights & Biases](../concepts.md#weights-biases)
- [Checkpoints](checkpoints.md)
