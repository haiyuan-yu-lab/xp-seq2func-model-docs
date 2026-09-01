# ClassPredictor

Classification prediction head for **v0.1.0a8**.

Nestable only under `EncoderPredictor.predictor`. Consumes the shared trimmed
encoder embedding and emits class probabilities. See
[Model composition](composition.md).

## Configuration

| Key | Type | Notes |
| --- | --- | --- |
| `model_name` | non-empty string | Unique across the composition tree; used in artifact filenames |
| `n_class` | integer ≥ 2 | Number of classes |

```json
{
  "model_type": "ClassPredictor",
  "model_config": { "model_name": "cls_head", "n_class": 3 }
}
```

## Hyperparameters

Each `hparams.predictor.<head_key>` entry for this head uses the scalar
wrapper with exact keys `alpha`, `loss`, and `predictor_config`:

| Key | Type | Notes |
| --- | --- | --- |
| `alpha` | integer ≥ 0 | Head weight in the combined loss |
| `loss` | `{ "type", "params" }` | Recommend `categorical_cross_entropy` with `params: {}` |
| `predictor_config` | object | FC stack settings (below) |

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
  "loss": { "type": "categorical_cross_entropy", "params": {} },
  "predictor_config": {
    "n_fc_layers": 1,
    "fc_hidden_dims": [],
    "dropout": 0.0,
    "activation": "relu",
    "pooling_methods": "GAP"
  }
}
```

## Inputs and outputs

| Tensor | Shape | Notes |
| --- | --- | --- |
| Input | `(B, C, L_embed)` | Shared trimmed encoder embedding |
| Predictions | `(N, n_class)` | Class probabilities |

## Labels and artifacts

| Surface | Contract |
| --- | --- |
| Data key | `label_npy` (path or path array aligned to OHE sources) |
| Prediction artifact | `{job}.{encoder_predictor}.{head_model_name}.pred_class.npy` |

Train/val require `label_npy` for every declared classification head.
Prediction may omit labels.

## Related pages

- [RegressPredictor](regress-predictor.md)
- [Model composition](composition.md)
- [Labels](../data/labels.md)
- [Prediction artifacts](../artifacts/predictions.md)
- [Losses](../configuration/losses.md)
