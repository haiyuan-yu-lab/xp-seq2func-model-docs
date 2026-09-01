# Hyperparameters

Fixed hyperparameter JSON for `train_model` and `pred_model` in **v0.1.0a8**.
This page is the canonical reference for top-level required keys, scalar and
profile head wrappers, inheritance, freezing, and the Adam optimizer contract.

Tune searches use a related tune-space envelope; see
[Tuning spaces](tuning-spaces.md).

## Top-level required keys

| Key | Type | Notes |
| --- | --- | --- |
| `batch_size` | integer ≥ 1 | Shared training/prediction batch size |
| `learning_rate` | number **> 0** | Top-level rate; must stay strictly positive |
| `n_channels` | integer ≥ 1 | Shared channel width `C` |
| `encoder` | object | Architecture (+ optional overrides) for the nested encoder |
| `predictor` | object map | One wrapper object per prediction-head map key |

Unknown top-level keys fail closed. Optimizer and loss are **not** configured
at the top level of this file: Adam is fixed, and per-head losses live inside
each predictor wrapper.

## Encoder subtree

Shape depends on the nested encoder type. See
[ConvEncoder](../models/conv-encoder.md) and
[ConvSelfAttEncoder](../models/conv-self-att-encoder.md).

Missing inheritable keys (`batch_size`, `learning_rate`, `n_channels`) are
filled from the parent. Nested `learning_rate: 0` freezes the encoder.

## Scalar prediction-head wrapper

`ClassPredictor` and `RegressPredictor` entries under `predictor` use exactly
these keys:

| Key | Type | Notes |
| --- | --- | --- |
| `alpha` | integer ≥ 0 | Head weight in the combined objective |
| `loss` | `{ "type", "params" }` | See [Losses](losses.md) |
| `predictor_config` | object | FC stack (+ optional inheritable overrides) |

No other wrapper keys are allowed. Recommended losses: `categorical_cross_entropy`
for classification, `mse` for regression.

## Profile prediction-head wrapper

`ProfilePredictor` entries use component weights and losses instead of scalar
`alpha` / `loss`:

| Key | Type | Notes |
| --- | --- | --- |
| `profile_alpha` | finite number ≥ 0 | Weight on the profile-distribution component |
| `count_alpha` | finite number ≥ 0 | Weight on the profile-count component |
| `profile_loss` | `{ "type", "params" }` | Must be `profile_cross_entropy` with `params: {}` |
| `count_loss` | `{ "type", "params" }` | Must be `log1p_mse` with `params: {}` |
| `predictor_config` | object | Count-branch FC settings (same FC fields as scalar heads) |

Mixing scalar wrapper keys with profile wrapper keys fails closed.
`track_names` and `bin_size` stay in model config and must not appear in a tune
space. Full geometry and count pairing:
[ProfilePredictor](../models/profile-predictor.md) and
[Profile reconstruction](../profiles.md).

<!-- schema: schemas/v0.1.0a8/profile-head-hparams-wrapper.schema.json -->
```json
{
  "profile_alpha": 1.0,
  "profile_loss": { "type": "profile_cross_entropy", "params": {} },
  "count_alpha": 1.0,
  "count_loss": { "type": "log1p_mse", "params": {} },
  "predictor_config": {
    "n_fc_layers": 1,
    "fc_hidden_dims": [],
    "dropout": 0.0,
    "activation": "relu",
    "pooling_methods": "GAP"
  }
}
```

## Combined weights

Across the whole model, at least one scalar `alpha` or profile component
weight must be strictly greater than zero. Zero-weight heads still require
labels when present in the composition and still emit diagnostics.

## Inheritance

Pre-inheritance JSON may omit child keys that the child schema allows and the
parent already defines.

| Rule | Behavior |
| --- | --- |
| Fill | Missing child keys are copied from the parent when they appear in the child schema |
| Merge | No deep merge — present child objects replace, they do not recursively merge |
| Unknown keys | Fail closed |
| Sidecars | Written top-level `.hparam.json` artifacts keep the pre-inheritance tree |

Typical inherited keys: `batch_size`, `learning_rate`, `n_channels`.

## Freezing and Adam

| Location | Allowed values | Effect of `0` |
| --- | --- | --- |
| Top-level `learning_rate` | number **> 0** | Not allowed |
| Nested encoder `learning_rate` | number ≥ 0 | Freezes the encoder (`requires_grad=False`); omitted from Adam |
| Nested head `predictor_config.learning_rate` | number ≥ 0 | Freezes that prediction head; omitted from Adam |

Distinct positive rates become separate Adam parameter groups. Freezing every
trainable module fails when the optimizer is built. Adam itself is not
configurable beyond these learning rates (no top-level `optimizer` key).

Pair freezing with optional `init_checkpoint` to warm-start then hold modules.
Freezing a `ProfilePredictor` freezes both of its branches. See
[Initialization and freezing](../workflows/initialization-and-freezing.md)
and [Config: init_checkpoint](../config.md#init_checkpoint-train--tune).

## Complete example

<!-- schema: schemas/v0.1.0a8/encoder-predictor-hparams.schema.json -->
```json
{
  "batch_size": 32,
  "learning_rate": 0.001,
  "n_channels": 16,
  "encoder": {
    "n_layers": 2,
    "kernel_size": 5,
    "dilation": [1, 2],
    "learning_rate": 0
  },
  "predictor": {
    "cls": {
      "alpha": 1,
      "loss": { "type": "categorical_cross_entropy", "params": {} },
      "predictor_config": {
        "n_fc_layers": 2,
        "fc_hidden_dims": [64],
        "dropout": 0.1,
        "activation": "gelu",
        "pooling_methods": "GAP"
      }
    },
    "reg": {
      "alpha": 1,
      "loss": { "type": "mse", "params": {} },
      "predictor_config": {
        "n_fc_layers": 1,
        "fc_hidden_dims": [],
        "dropout": 0.0,
        "activation": "relu",
        "pooling_methods": "GMP",
        "learning_rate": 0.0005
      }
    }
  }
}
```

In that example the encoder inherits `batch_size` / `n_channels` from the
parent, is frozen via `learning_rate: 0`, the classification head inherits the
top-level learning rate, and the regression head overrides to `0.0005`.

## Invalid fragments (illustrative)

Top-level learning rate must be positive:

```json
{
  "batch_size": 8,
  "learning_rate": 0,
  "n_channels": 8,
  "encoder": { "n_layers": 1, "kernel_size": 3, "dilation": [1] },
  "predictor": {}
}
```

Scalar wrappers reject unknown keys:

```json
{
  "alpha": 1,
  "loss": { "type": "mse", "params": {} },
  "predictor_config": {
    "n_fc_layers": 1,
    "fc_hidden_dims": [],
    "dropout": 0.0,
    "activation": "relu",
    "pooling_methods": "GAP"
  },
  "extra": true
}
```

## Schema snapshot

[`encoder-predictor-hparams.schema.json`](../schemas/v0.1.0a8/encoder-predictor-hparams.schema.json),
[`scalar-head-hparams-wrapper.schema.json`](../schemas/v0.1.0a8/scalar-head-hparams-wrapper.schema.json),
and
[`profile-head-hparams-wrapper.schema.json`](../schemas/v0.1.0a8/profile-head-hparams-wrapper.schema.json).

## Related pages

- [Losses](losses.md)
- [Model composition](../models/composition.md)
- [ProfilePredictor](../models/profile-predictor.md)
- [Concepts: learning rates and freezing](../concepts.md#learning-rates-and-freezing)
- [Schemas](../reference/schemas.md)
