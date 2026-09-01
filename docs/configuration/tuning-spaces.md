# Tuning spaces

Tune-space JSON for `tune_model --tune-space` in exact release **v0.1.0a8**.

This page is the canonical human-readable contract for the search-space
envelope and leaf descriptors. The documentation schema snapshot is
[tune-space.schema.json](../schemas/v0.1.0a8/tune-space.schema.json).

Drawn hyperparameter **values** follow the same field meanings as fixed
hparams: reuse [Hyperparameters](hyperparameters.md) for key tables, inheritance,
freezing, and Adam learning-rate rules. Do not put `init_checkpoint`,
`track_names`, or `bin_size` in a tune-space file.

## Envelope

| Key | Type | Notes |
| --- | --- | --- |
| `method` | string | `grid`, `random`, or `bayes` |
| `parameters` | object | Nested tree of leaf descriptors mirroring the hparams layout |

Only these two top-level keys are allowed. Unknown envelope keys fail closed.
A bad tune-space file fails at load time before agents start.

## Required `parameters` keys

| Key | Notes |
| --- | --- |
| `batch_size` | Leaf or nested fragment |
| `learning_rate` | Leaf; top-level rates must stay **> 0** for every allowed draw |
| `n_channels` | Leaf or nested fragment |
| `encoder` | Nested fragment matching the configured encoder type |
| `predictor` | Map of head key → wrapper fragment for each declared head |

Unknown `parameters` keys fail closed. Nesting must align with the tune
config's `model_config` (same predictor map keys and encoder/head types).

## Leaf descriptors

Every searchable scalar (or fixed object) ends in exactly one leaf form:

| Form | Keys | Meaning |
| --- | --- | --- |
| Fixed | `{"value": ...}` | Constant value (scalar or nested object when fixing a whole subtree) |
| Discrete | `{"values": [...]}` | Non-empty list of choices |
| Continuous | `{"distribution": "uniform"\|"log_uniform", "min": ..., "max": ...}` | Continuous range; require `min < max`; `log_uniform` requires `min > 0` |

Unknown leaf keys fail closed. Do not mix forms (for example `value` plus
`values`) in one leaf.

### Learning-rate leaves

Same public rules as fixed hparams:

| Path | Allowed draws |
| --- | --- |
| Top-level `learning_rate` | Every `value` / `values` entry / continuous `min` must be **> 0** |
| Nested `.learning_rate` | Every draw must be **≥ 0** (including fixed `{"value": 0}` to freeze) |

### Profile component weights

When a profile head is present, `profile_alpha` / `count_alpha` leaves must
draw finite numbers ≥ 0. Profile geometry fields `track_names` and `bin_size`
stay on `model_config` only — never in the tune-space tree. See
[Profiles](../profiles.md).

## Complete example

Placeholder paths are not used inside the tune-space file itself; values are
numeric / structural. This example matches the composition used on
[Tune configuration](tune.md).

<!-- schema: schemas/v0.1.0a8/tune-space.schema.json -->
```json
{
  "method": "random",
  "parameters": {
    "batch_size": { "values": [16, 32] },
    "learning_rate": {
      "distribution": "log_uniform",
      "min": 0.0001,
      "max": 0.01
    },
    "n_channels": { "value": 16 },
    "encoder": {
      "n_layers": { "values": [2, 3] },
      "kernel_size": { "value": 5 },
      "dilation": { "value": [1, 2, 4] },
      "learning_rate": { "values": [0, 0.001] }
    },
    "predictor": {
      "cls": {
        "alpha": { "value": 1 },
        "loss": {
          "value": { "type": "categorical_cross_entropy", "params": {} }
        },
        "predictor_config": {
          "n_fc_layers": { "value": 2 },
          "fc_hidden_dims": { "value": [64] },
          "dropout": {
            "distribution": "uniform",
            "min": 0.0,
            "max": 0.5
          },
          "activation": { "values": ["relu", "gelu"] },
          "pooling_methods": { "value": "GAP" }
        }
      },
      "reg": {
        "alpha": { "value": 1 },
        "loss": { "value": { "type": "mse", "params": {} } },
        "predictor_config": {
          "n_fc_layers": { "value": 1 },
          "fc_hidden_dims": { "value": [] },
          "dropout": { "value": 0.0 },
          "activation": { "value": "relu" },
          "pooling_methods": { "value": "GAP" }
        }
      }
    }
  }
}
```

## Invalid fragments (illustrative)

Forbidden reserved keys inside `parameters`:

```json
{
  "init_checkpoint": { "value": { "path": "/path/to/x.pth", "modules": ["enc"] } }
}
```

```json
{
  "predictor": {
    "prof": {
      "track_names": { "value": ["plus"] },
      "bin_size": { "value": 1 }
    }
  }
}
```

Unknown leaf keys:

```json
{
  "learning_rate": { "value": 0.001, "distribution": "uniform" }
}
```

Top-level learning rate may not be zero:

```json
{
  "learning_rate": { "value": 0 }
}
```

## Related pages

- [`tune_model` CLI](../cli/tune_model.md)
- [Tune configuration](tune.md)
- [Hyperparameters](hyperparameters.md)
- [Tuning workflow](../workflows/tuning.md)
- [Formats overview](../formats.md)
- [Schemas](../reference/schemas.md)
