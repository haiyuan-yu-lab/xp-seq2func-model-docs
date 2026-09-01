# Tune configuration

Tune-config JSON for `tune_model --config` in exact release **v0.1.0a8**.

This page is the canonical human-readable contract. The documentation schema
snapshot is
[tune-config.schema.json](../schemas/v0.1.0a8/tune-config.schema.json).

Shared model, data, early-stopping, checkpoint, and metric contracts are
documented once elsewhere — link to those pages rather than duplicating their
tables here.

## Required top-level keys

| Key | Type | Notes |
| --- | --- | --- |
| `model_type` | string | Must be `EncoderPredictor` |
| `model_config` | object | Composition tree; see [Model composition](../models/composition.md) |
| `train_data` | object | Train split; see [Splits](../data/splits.md) |
| `val_data` | object | Validation split; same shape as `train_data` |
| `random_seed` | integer | Seeds process RNGs |
| `max_epochs` | integer ≥ 1 | Hard epoch cap per trial |
| `early_stopping` | object | `{ "grace_epochs": <int ≥ 1> }` — same object as train |
| `wandb` | object | Requires `project` and `mode` (`online` \| `offline` only) |

Unknown top-level keys fail closed. There is **no** `job_name` on tune configs;
artifact stems use each trial's W&B `run_id`.

## Forbidden top-level keys

| Key | Why |
| --- | --- |
| `optimizer` | Adam is fixed; learning rates live in the tune-space / drawn hparams |
| `loss` | Per-head losses live in predictor wrappers inside the tune-space |
| `job_name` | Tune artifacts use the W&B `run_id` as stem |
| `num_agents` | Pass `--num-agents` on the CLI |
| `max_trials` | Pass `--max-trials` on the CLI |

## Optional top-level keys

| Key | Type | Notes |
| --- | --- | --- |
| `init_checkpoint` | object | `{ "path", "modules" }`; applied at the start of **each** trial; see [Config: init_checkpoint](../config.md#init_checkpoint-train--tune) and [Initialization and freezing](../workflows/initialization-and-freezing.md) |

Do not put `init_checkpoint` in the tune-space file.

## `early_stopping`

Same contract as training. Schema snapshot:
[early-stopping.schema.json](../schemas/v0.1.0a8/early-stopping.schema.json).

| Key | Type | Notes |
| --- | --- | --- |
| `grace_epochs` | integer ≥ 1 | Patience: stop after this many epochs without a new best `val_loss` |

No other keys are allowed.

<!-- schema: schemas/v0.1.0a8/early-stopping.schema.json -->
```json
{
  "grace_epochs": 5
}
```

## `wandb`

| Key | Required | Notes |
| --- | --- | --- |
| `project` | yes | W&B project name (string) |
| `mode` | yes | `online` or `offline` only (`disabled` is invalid for tune) |
| `entity` | no | Optional entity string |
| `tags` | no | Array of strings |
| `notes` | no | Free-text notes |
| `sweep_id` | no | Existing sweep id; empty string means create a new sweep |
| `sweep_name` | conditional | **Required** when `sweep_id` is empty |

Forbidden on tune configs: `name`, `num_agents`, `max_trials`. Trial run names
come from W&B; agent and trial caps are CLI flags.

<!-- schema: schemas/v0.1.0a8/wandb-tune.schema.json -->
```json
{
  "project": "seq2func-tune",
  "mode": "online",
  "sweep_name": "demo-sweep",
  "tags": ["example"],
  "notes": "placeholder tune sweep"
}
```

## Data blocks

`train_data` and `val_data` share the split contract documented in
[Splits](../data/splits.md). Schema snapshot:
[data-source.schema.json](../schemas/v0.1.0a8/data-source.schema.json).

`batch_size` is **not** a data-block field; it belongs in the tune-space
`parameters` tree (see [Tuning spaces](tuning-spaces.md) and
[Hyperparameters](hyperparameters.md)).

## Complete example

Placeholder paths only. Pair with a tune-space document from
[Tuning spaces](tuning-spaces.md).

<!-- schema: schemas/v0.1.0a8/tune-config.schema.json -->
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
  "random_seed": 0,
  "max_epochs": 20,
  "early_stopping": { "grace_epochs": 5 },
  "wandb": {
    "project": "seq2func-tune",
    "mode": "online",
    "sweep_name": "demo-sweep"
  }
}
```

Shell form:

```bash
export CUDA_VISIBLE_DEVICES=0
tune_model \
  --config /path/to/tune.json \
  --tune-space /path/to/tune_space.json \
  --opath /path/to/out \
  --verbosity 1
```

## Multi-source data fragment

Additive multi-source `train_data` nesting for tune configs. Complete
multi-source tune example:
[Multi-source data workflow](../workflows/multi-source-data.md).

<!-- schema: schemas/v0.1.0a8/data-source.schema.json -->
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
  "source_fracs": [0.6, 0.4]
}
```

## Invalid fragments (illustrative)

Forbidden `job_name` and CLI-only controls:

```json
{
  "job_name": "should-fail",
  "num_agents": 2,
  "max_trials": 10
}
```

`disabled` W&B mode is invalid for tune:

```json
{
  "project": "seq2func-tune",
  "mode": "disabled",
  "sweep_name": "demo-sweep"
}
```

Missing `sweep_name` when `sweep_id` is empty:

```json
{
  "project": "seq2func-tune",
  "mode": "offline",
  "sweep_id": ""
}
```

## Related pages

- [`tune_model` CLI](../cli/tune_model.md)
- [Tuning spaces](tuning-spaces.md)
- [Tuning workflow](../workflows/tuning.md)
- [Train configuration](train.md) (shared early stopping and data blocks)
- [Multi-source](../data/multi-source.md)
- [Multi-source data workflow](../workflows/multi-source-data.md)
- [Config overview](../config.md)
- [Schemas](../reference/schemas.md)
