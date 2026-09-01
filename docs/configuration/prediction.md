# Prediction configuration

Prediction-config JSON for `pred_model --config` in exact release **v0.1.0a8**.

This page is the canonical human-readable contract. The documentation schema
snapshot is
[pred-config.schema.json](../schemas/v0.1.0a8/pred-config.schema.json).

## Required top-level keys

| Key | Type | Notes |
| --- | --- | --- |
| `model_type` | string | Must be `EncoderPredictor` |
| `model_config` | object | Composition tree; see [Model composition](../models/composition.md) |
| `test_data` | object | Test / inference split; see [Test data](#test_data) |
| `job_name` | non-empty string | Artifact stem for prediction filenames |
| `random_seed` | integer | Seeds process RNGs |

Unknown top-level keys fail closed.

## Forbidden top-level keys

| Key | Why |
| --- | --- |
| `wandb` | Prediction does not log to Weights & Biases |
| `loss` | Per-head losses live in hparams from training |
| `optimizer` | No optimizer during inference |
| `max_epochs` | Training-only |
| `early_stopping` | Training-only |
| `init_checkpoint` | Training/tune-only; prediction loads `--checkpoint` |
| Keys matching `attribution*` | Attribution is CLI-only (`--attribution`, `--attribution-target`) |

## `test_data`

`test_data` reuses the loader keys of train/val splits, but labels are optional
and profile masks are forbidden. Schema snapshot:
[test-data.schema.json](../schemas/v0.1.0a8/test-data.schema.json).

### Required keys

| Key | Type | Notes |
| --- | --- | --- |
| `encoder` | object | `{ "ohe_npy": <path\|paths>, "label": null }` |
| `shuffle` | boolean | Typical: `false` for deterministic row order |
| `num_workers` | integer ≥ 0 | DataLoader workers |
| `pin_memory` | boolean | DataLoader pin-memory flag |
| `source_fracs` | number array | Positive weights; length equals source count `S` |

### Optional keys

| Key | Type | Notes |
| --- | --- | --- |
| `predictor` | object map | Label payloads when evaluating against labels; omit for unlabeled inference |
| `persistent_workers` | boolean or `null` | Meaningful when `num_workers > 0` |
| `prefetch_factor` | integer ≥ 1 or `null` | Meaningful when `num_workers > 0` |

Unknown keys fail closed. `batch_size` is **not** allowed here; set it in the
hparams file passed to `--hparams`.

### Label optionality

| Situation | Behavior |
| --- | --- |
| Unlabeled inference | Omit `predictor`, or omit individual head entries |
| Labeled evaluation | Supply a payload for each head you want labels for |
| Scalar head payload | `{ "label_npy": <path\|paths> }` when present |
| Profile head payload | Both `profile_npy` and `count_npy` required together when present |
| Profile `mask_npy` | Invalid on test; rejected |

Train/val require labels for every declared head. Prediction does not. Exact
exception strings for invalid label combinations are not stabilized here; see
[Validation and errors](../reference/validation-and-errors.md).

### Encoder payload

| Key | Required | Contract |
| --- | --- | --- |
| `ohe_npy` | yes | Non-empty path string, or non-empty path array of length `S` |
| `label` | yes | Must be JSON `null` |

See [Arrays](../data/arrays.md) and [Splits](../data/splits.md) for geometry and
`source_fracs` invariants (`S = 1` ⇒ `[1]`).

## Complete unlabeled example

Placeholder paths only.

<!-- schema: schemas/v0.1.0a8/pred-config.schema.json -->
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
  "test_data": {
    "encoder": {
      "ohe_npy": "/path/to/test_ohe.npy",
      "label": null
    },
    "shuffle": false,
    "num_workers": 0,
    "pin_memory": true,
    "source_fracs": [1]
  },
  "job_name": "demo_pred",
  "random_seed": 0
}
```

## Labeled `test_data` fragment (illustrative)

```json
{
  "encoder": {
    "ohe_npy": "/path/to/test_ohe.npy",
    "label": null
  },
  "predictor": {
    "cls": { "label_npy": "/path/to/test_cls_labels.npy" },
    "reg": { "label_npy": "/path/to/test_reg_labels.npy" }
  },
  "shuffle": false,
  "num_workers": 0,
  "pin_memory": true,
  "source_fracs": [1]
}
```

Standalone `test_data` documents may also validate against the test-data
schema:

<!-- schema: schemas/v0.1.0a8/test-data.schema.json -->
```json
{
  "encoder": {
    "ohe_npy": "/path/to/test_ohe.npy",
    "label": null
  },
  "shuffle": false,
  "num_workers": 0,
  "pin_memory": true,
  "source_fracs": [1]
}
```

## Multi-source `test_data`

Unlabeled multi-source inference. With `shuffle: false`, prediction rows follow
sources concatenated in list order. Full command example:
[Multi-source data workflow](../workflows/multi-source-data.md).

<!-- schema: schemas/v0.1.0a8/test-data.schema.json -->
```json
{
  "encoder": {
    "ohe_npy": [
      "/path/to/src0_test_ohe.npy",
      "/path/to/src1_test_ohe.npy"
    ],
    "label": null
  },
  "shuffle": false,
  "num_workers": 0,
  "pin_memory": true,
  "source_fracs": [0.5, 0.5]
}
```

Labeled multi-source fragment (illustrative; omit unused heads as needed):

```json
{
  "encoder": {
    "ohe_npy": [
      "/path/to/src0_test_ohe.npy",
      "/path/to/src1_test_ohe.npy"
    ],
    "label": null
  },
  "predictor": {
    "cls": {
      "label_npy": [
        "/path/to/src0_test_cls_labels.npy",
        "/path/to/src1_test_cls_labels.npy"
      ]
    },
    "reg": {
      "label_npy": [
        "/path/to/src0_test_reg_labels.npy",
        "/path/to/src1_test_reg_labels.npy"
      ]
    },
    "prof": {
      "profile_npy": [
        "/path/to/src0_test_profile.npy",
        "/path/to/src1_test_profile.npy"
      ],
      "count_npy": [
        "/path/to/src0_test_count.npy",
        "/path/to/src1_test_count.npy"
      ]
    }
  },
  "shuffle": false,
  "num_workers": 0,
  "pin_memory": true,
  "source_fracs": [0.5, 0.5]
}
```

## Invalid fragments (illustrative)

Forbidden training key on a prediction config:

```json
{
  "wandb": { "project": "should-fail", "mode": "disabled" }
}
```

Forbidden profile mask on test:

```json
{
  "profile_npy": "/path/to/test_profile.npy",
  "count_npy": "/path/to/test_count.npy",
  "mask_npy": "/path/to/test_mask.npy"
}
```

Profile labels missing the paired count array:

```json
{
  "profile_npy": "/path/to/test_profile.npy"
}
```

## Shell form

```bash
pred_model \
  --config /path/to/pred.json \
  --hparams /path/to/out/demo_train.ep_main.hparam.json \
  --checkpoint /path/to/out/demo_train.ep_main.pth \
  --opath /path/to/pred_out \
  --verbosity 1
```

## Related pages

- [`pred_model` CLI](../cli/pred_model.md)
- [Config overview](../config.md)
- [Predictions](../artifacts/predictions.md)
- [Multi-source](../data/multi-source.md)
- [Multi-source data workflow](../workflows/multi-source-data.md)
- [Train to predict](../workflows/train-to-predict.md)
- [Schemas](../reference/schemas.md)
