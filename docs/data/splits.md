# Splits

Train, validation, and test split contracts for **v0.1.0a8**.

| Split key | Used by | Labels |
| --- | --- | --- |
| `train_data` | `train_model`, `tune_model` | Required for every declared head |
| `val_data` | `train_model`, `tune_model` | Required for every declared head |
| `test_data` | `pred_model` | Optional (label-free prediction allowed) |

This page focuses on the train/val block used by training. Schema snapshot:
[data-source.schema.json](../schemas/v0.1.0a8/data-source.schema.json).

## Required keys

| Key | Type | Notes |
| --- | --- | --- |
| `encoder` | object | `{ "ohe_npy": <path\|paths>, "label": null }` |
| `predictor` | object map | One payload per head map key in `model_config.predictor` |
| `shuffle` | boolean | Typical: `true` train, `false` val |
| `num_workers` | integer ≥ 0 | DataLoader workers |
| `pin_memory` | boolean | DataLoader pin-memory flag |
| `source_fracs` | number array | Positive weights; length equals source count `S` |

## Optional loader keys

| Key | Type | Notes |
| --- | --- | --- |
| `persistent_workers` | boolean or `null` | Meaningful when `num_workers > 0` |
| `prefetch_factor` | integer ≥ 1 or `null` | Meaningful when `num_workers > 0` |

Unknown keys fail closed. `batch_size` is **not** allowed here; set it in
hparams.

## Encoder payload

| Key | Required | Contract |
| --- | --- | --- |
| `ohe_npy` | yes | Non-empty path string, or non-empty path array of length `S` |
| `label` | yes | Must be JSON `null` |

Empty path arrays fail. See [Arrays](arrays.md) for one-hot geometry.

## Predictor payloads

Map keys must match `model_config.predictor` exactly on train/val (no missing
heads, no extras).

| Head type | Payload |
| --- | --- |
| `ClassPredictor` / `RegressPredictor` | `{ "label_npy": <path\|paths> }` |
| `ProfilePredictor` | `{ "profile_npy": ..., "count_npy": ..., "mask_npy"?: ... }` |

Scalar heads use the released field name **`label_npy`** (not `label`).
Profile details: [Profiles](../profiles.md) and [Labels](labels.md).

## `source_fracs` invariants

| Rule | Behavior |
| --- | --- |
| Required | Always present on the split |
| Length | Exactly `S` entries, where `S` is the OHE source count |
| Values | Every entry must be a number `> 0` |
| Single source | When `S = 1`, the only valid value is `[1]` (or `[1.0]`) |

Path arrays for labels must use the same `S` and the same source order as
`encoder.ohe_npy`. See [Multi-source](multi-source.md).

## Complete single-source example

<!-- schema: schemas/v0.1.0a8/data-source.schema.json -->
```json
{
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
}
```

## Multi-source fragment (illustrative)

```json
{
  "encoder": {
    "ohe_npy": ["/path/to/src0_ohe.npy", "/path/to/src1_ohe.npy"],
    "label": null
  },
  "predictor": {
    "cls": {
      "label_npy": [
        "/path/to/src0_cls_labels.npy",
        "/path/to/src1_cls_labels.npy"
      ]
    }
  },
  "shuffle": true,
  "num_workers": 2,
  "pin_memory": true,
  "source_fracs": [0.7, 0.3],
  "persistent_workers": true,
  "prefetch_factor": 2
}
```

## Related pages

- [Train configuration](../configuration/train.md)
- [Arrays](arrays.md)
- [Labels](labels.md)
- [Multi-source](multi-source.md)
- [Formats overview](../formats.md)
