# RegressPredictor

Scalar regression prediction head for **v0.1.0a8**.

Nestable only under `EncoderPredictor.predictor`. Consumes the shared trimmed
encoder embedding and emits a single scalar per row. See
[Model composition](composition.md).

## Configuration

| Key | Type | Notes |
| --- | --- | --- |
| `model_name` | non-empty string | Unique across the composition tree; used in artifact filenames |

Identity-only `model_config` (no `n_class`):

```json
{
  "model_type": "RegressPredictor",
  "model_config": { "model_name": "reg_head" }
}
```

## Hyperparameters

Each `hparams.predictor.<head_key>` entry for this head uses the same scalar
wrapper as `ClassPredictor` (`alpha`, `loss`, `predictor_config`):

| Key | Type | Notes |
| --- | --- | --- |
| `alpha` | integer ≥ 0 | Head weight in the combined loss |
| `loss` | `{ "type", "params" }` | Recommend `mse` with `params: {}` |
| `predictor_config` | object | Same FC stack fields as `ClassPredictor` |

`predictor_config` fields:

| Key | Type | Notes |
| --- | --- | --- |
| `n_fc_layers` | integer ≥ 1 | Required |
| `fc_hidden_dims` | array of integers ≥ 1 | Length ≥ `n_fc_layers - 1` (prefix used) |
| `dropout` | number in `[0, 1)` | Required |
| `activation` | `relu` \| `gelu` \| `silu` | Required |
| `pooling_methods` | `GAP` \| `GMP` | Required |
| `batch_size` | integer ≥ 1 | Optional; inherits from parent when omitted |
| `learning_rate` | number ≥ 0 | Optional; `0` freezes this head |
| `n_channels` | integer ≥ 1 | Optional; inherits from parent when omitted |

Canonical wrapper, inheritance, and freeze rules:
[Hyperparameters](../configuration/hyperparameters.md). Loss object contract:
[Losses](../configuration/losses.md).

<!-- schema: schemas/v0.1.0a8/scalar-head-hparams-wrapper.schema.json -->
```json
{
  "alpha": 1,
  "loss": { "type": "mse", "params": {} },
  "predictor_config": {
    "n_fc_layers": 1,
    "fc_hidden_dims": [],
    "dropout": 0.0,
    "activation": "relu",
    "pooling_methods": "GMP"
  }
}
```

## Inputs and outputs

| Tensor | Shape | Notes |
| --- | --- | --- |
| Input | `(B, C, L_embed)` | Shared trimmed encoder embedding |
| Predictions | `(N, 1)` | Scalar regression outputs |

## Labels and artifacts

| Surface | Contract |
| --- | --- |
| Data key | `label_npy` (path or path array aligned to OHE sources) |
| Label geometry | Trailing width 1 — shape `(N, 1)` per source array; rank-1 labels fail |
| Prediction artifact | `{job}.{encoder_predictor}.{head_model_name}.pred.npy` |

Train/val require `label_npy` for every declared regression head. Prediction
may omit labels.

## Related pages

- [ClassPredictor](class-predictor.md)
- [Model composition](composition.md)
- [Labels](../data/labels.md)
- [Prediction artifacts](../artifacts/predictions.md)
- [Losses](../configuration/losses.md)
