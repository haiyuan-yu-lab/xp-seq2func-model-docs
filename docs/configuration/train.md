# Train configuration

Train-config JSON for `train_model --config` in exact release **v0.1.0a9**.

This page is the canonical human-readable contract. The documentation schema
snapshot is
[train-config.schema.json](../schemas/v0.1.0a9/train-config.schema.json).

## Required top-level keys

| Key | Type | Notes |
| --- | --- | --- |
| `model_type` | string | Must be `EncoderPredictor` |
| `model_config` | object | Composition tree; see [Model composition](../models/composition.md) |
| `train_data` | object | Train split; see [Splits](../data/splits.md) |
| `val_data` | object | Validation split; same shape as `train_data` |
| `job_name` | non-empty string | Artifact stem and W&B run name |
| `random_seed` | integer | Seeds process RNGs |
| `max_epochs` | integer ≥ 1 | Hard epoch cap |
| `early_stopping` | object | `{ "grace_epochs": <int ≥ 1> }` |
| `wandb` | object | Requires `project` and `mode` |

Unknown top-level keys fail closed.

## Forbidden top-level keys

| Key | Why |
| --- | --- |
| `optimizer` | Adam is fixed; learning rates live in hparams |
| `loss` | Per-head losses live in hparams wrappers |

## Optional top-level keys

| Key | Type | Notes |
| --- | --- | --- |
| `init_checkpoint` | object | `{ "path", "modules" }`; see [Config: init_checkpoint](../config.md#init_checkpoint-train--tune) and [Initialization and freezing](../workflows/initialization-and-freezing.md) |

## `early_stopping`

| Key | Type | Notes |
| --- | --- | --- |
| `grace_epochs` | integer ≥ 1 | Patience: stop after this many epochs without a new best `val_loss` |

No other keys are allowed.

<!-- schema: schemas/v0.1.0a9/early-stopping.schema.json -->
```json
{
  "grace_epochs": 5
}
```

## `wandb`

| Key | Required | Notes |
| --- | --- | --- |
| `project` | yes | W&B project name (string) |
| `mode` | yes | `online`, `offline`, or `disabled` |
| `entity` | no | Optional entity string |
| `tags` | no | Array of strings |
| `notes` | no | Free-text notes |

Forbidden on train configs: `name`, `sweep_id`, `sweep_name`. The run name is
always taken from `job_name`. When `mode` is `disabled`, no W&B run is created.

<!-- schema: schemas/v0.1.0a9/wandb-train.schema.json -->
```json
{
  "project": "seq2func-train",
  "mode": "disabled",
  "tags": ["example"],
  "notes": "placeholder train run"
}
```

## Data blocks

`train_data` and `val_data` share the split contract documented in
[Splits](../data/splits.md). Schema snapshot:
[data-source.schema.json](../schemas/v0.1.0a9/data-source.schema.json).

Loader keys live on the split (`shuffle`, `num_workers`, `pin_memory`,
`source_fracs`, optional `persistent_workers` / `prefetch_factor`).
`batch_size` is **not** a data-block field; it belongs in hparams.

### Profile-specific validation

When `model_config.predictor` includes a `ProfilePredictor` or
`RCProfilePredictor`:

| Check | Behavior |
| --- | --- |
| Labels | Train/val require `profile_npy` and `count_npy` for every profile head |
| Optional mask | `mask_npy` may appear on train and/or val; boolean `(N, L_embed)` |
| Geometry | `P = L_embed / bin_size` must be exact; profile labels rank-3 `(N, T, P)` |
| Wrapper | Hparams use `profile_alpha` / `count_alpha` / `profile_loss` / `count_loss` |
| Losses | `profile_loss.type` must be `profile_cross_entropy`; `count_loss.type` must be `log1p_mse` |

See [Profiles](../profiles.md), [Labels](../data/labels.md), and
[Masks](../data/masks.md).

## Complete example

Placeholder paths only.

<!-- schema: schemas/v0.1.0a9/train-config.schema.json -->
```json
{
  "model_type": "EncoderPredictor",
  "model_config": {
    "model_name": "ep_main",
    "embedding_trimming": 0,
    "encoder": {
      "model_type": "ConvEncoder",
      "model_config": { "model_name": "enc" }
    },
    "predictor": {
      "cls": {
        "model_type": "ClassPredictor",
        "model_config": { "model_name": "cls_head", "n_class": 2 }
      },
      "reg": {
        "model_type": "RegressPredictor",
        "model_config": { "model_name": "reg_head" }
      }
    }
  },
  "train_data": {
    "encoder": {
      "ohe_npy": "/path/to/train_ohe.npy",
      "label": null
    },
    "predictor": {
      "cls": { "label_npy": "/path/to/train_cls_labels.npy" },
      "reg": { "label_npy": "/path/to/train_reg_labels.npy" }
    },
    "shuffle": true,
    "num_workers": 0,
    "pin_memory": true,
    "source_fracs": [1]
  },
  "val_data": {
    "encoder": {
      "ohe_npy": "/path/to/val_ohe.npy",
      "label": null
    },
    "predictor": {
      "cls": { "label_npy": "/path/to/val_cls_labels.npy" },
      "reg": { "label_npy": "/path/to/val_reg_labels.npy" }
    },
    "shuffle": false,
    "num_workers": 0,
    "pin_memory": true,
    "source_fracs": [1]
  },
  "job_name": "demo_train",
  "random_seed": 0,
  "max_epochs": 20,
  "early_stopping": { "grace_epochs": 5 },
  "wandb": {
    "project": "seq2func-train",
    "mode": "disabled"
  }
}
```

Pair with a complete hparams document from
[Hyperparameters](hyperparameters.md). Shell form:

```bash
train_model \
  --config /path/to/train.json \
  --hparams /path/to/hparams.json \
  --opath /path/to/out \
  --verbosity 1
```

## Multi-source data fragment

Additive multi-source `train_data` / `val_data` nesting. Full train/tune/pred
command examples: [Multi-source data workflow](../workflows/multi-source-data.md).
Invariants: [Multi-source](../data/multi-source.md).

<!-- schema: schemas/v0.1.0a9/data-source.schema.json -->
```json
{
  "encoder": {
    "ohe_npy": [
      "/path/to/src0_train_ohe.npy",
      "/path/to/src1_train_ohe.npy"
    ],
    "label": null
  },
  "predictor": {
    "cls": {
      "label_npy": [
        "/path/to/src0_train_cls_labels.npy",
        "/path/to/src1_train_cls_labels.npy"
      ]
    },
    "reg": {
      "label_npy": [
        "/path/to/src0_train_reg_labels.npy",
        "/path/to/src1_train_reg_labels.npy"
      ]
    }
  },
  "shuffle": true,
  "num_workers": 0,
  "pin_memory": true,
  "source_fracs": [0.7, 0.3]
}
```

## Invalid fragments (illustrative)

Forbidden optimizer key:

```json
{
  "optimizer": "adam"
}
```

Forbidden W&B run name override:

```json
{
  "project": "seq2func-train",
  "mode": "online",
  "name": "should-fail"
}
```

## Related pages

- [`train_model` CLI](../cli/train_model.md)
- [Config overview](../config.md)
- [Hyperparameters](hyperparameters.md)
- [Profiles](../profiles.md)
- [Multi-source](../data/multi-source.md)
- [Multi-source data workflow](../workflows/multi-source-data.md)
- [Schemas](../reference/schemas.md)
