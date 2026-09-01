# RCClassPredictor

Reverse-complement-aware classification head for **v0.1.0a8**.

Nestable only under `EncoderPredictor.predictor`. It preserves the same
external role as `ClassPredictor` — class probabilities, one-hot labels,
`*.pred_class.npy` artifacts, scalar-head loss wrapper, and classification
attribution targets — while making class identities invariant under the
embedding reverse-complement transform in evaluation mode.

See [Model composition](composition.md) and
[ClassPredictor](class-predictor.md) for the ordinary counterpart.

## Configuration

| Key | Type | Notes |
| --- | --- | --- |
| `model_name` | non-empty string | Unique across the composition tree; used in artifact filenames |
| `n_class` | integer ≥ 2 | Number of classes |

```json
{
  "model_type": "RCClassPredictor",
  "model_config": { "model_name": "rc_cls_head", "n_class": 3 }
}
```

## Hyperparameters

Each `hparams.predictor.<head_key>` entry uses the same scalar wrapper as
`ClassPredictor` (`alpha`, `loss`, `predictor_config`):

| Key | Type | Notes |
| --- | --- | --- |
| `alpha` | integer ≥ 0 | Head weight in the combined loss |
| `loss` | `{ "type", "params" }` | Recommend `categorical_cross_entropy` with `params: {}` |
| `predictor_config` | object | FC stack settings (below) |

`predictor_config` fields match `ClassPredictor`, with one extra constraint:

| Key | Type | Notes |
| --- | --- | --- |
| `n_fc_layers` | integer ≥ 1 | Required |
| `fc_hidden_dims` | array of integers ≥ 1 | Length ≥ `n_fc_layers - 1` (prefix used) |
| `dropout` | number in `[0, 1)` | Required |
| `activation` | `relu` \| `gelu` \| `silu` | Required |
| `pooling_methods` | `GAP` \| `GMP` | Required |
| `batch_size` | integer ≥ 1 | Optional; inherits from parent when omitted |
| `learning_rate` | number ≥ 0 | Optional; `0` freezes this head |
| `n_channels` | **even** integer ≥ 2 | Optional; inherits from parent when omitted |

Canonical wrapper, inheritance, and freeze rules:
[Hyperparameters](../configuration/hyperparameters.md). Loss object contract:
[Losses](../configuration/losses.md).

<!-- schema: schemas/v0.1.0a8/scalar-head-hparams-wrapper.schema.json -->
```json
{
  "alpha": 1,
  "loss": { "type": "categorical_cross_entropy", "params": {} },
  "predictor_config": {
    "n_fc_layers": 2,
    "fc_hidden_dims": [128],
    "dropout": 0.1,
    "activation": "relu",
    "pooling_methods": "GAP"
  }
}
```

## Forward behavior

The head applies one shared global-pool + FC stack to the trimmed embedding
and to its embedding reverse-complement (channel and length axes reversed on
`(B, C, L)` tensors). Pre-softmax logits are the average of the two branch
logits; `forward` returns the softmax of that average.

| Mode | Behavior |
| --- | --- |
| Eval (`dropout` off) | Logits and probabilities agree under embedding RC within floating-point tolerance; class order is unchanged |
| Train (`dropout` > 0) | Dropout is applied independently on each branch; separate forward calls need not match pathwise |

There is no required encoder family pairing. This head may sit behind ordinary
or RC encoders.

## Inputs and outputs

| Tensor | Shape | Notes |
| --- | --- | --- |
| Input | `(B, C, L_embed)` | Shared trimmed encoder embedding; `C` must be even |
| Predictions | `(N, n_class)` | Class probabilities |

## Labels and artifacts

| Surface | Contract |
| --- | --- |
| Data key | `label_npy` (path or path array aligned to OHE sources) |
| Prediction artifact | `{job}.{encoder_predictor}.{head_model_name}.pred_class.npy` |

Train/val require `label_npy` for every declared classification head.
Prediction may omit labels.

## Checkpoints

New training runs write typed `seq2func_ckpt_v2` checkpoints with
`model_type: RCClassPredictor` in `contracts`. Legacy `seq2func_ckpt_v1`
checkpoints cannot load into a composition tree that contains this head type.

## Related pages

- [ClassPredictor](class-predictor.md)
- [RCConvEncoder](rc-conv-encoder.md) / [RCConvSelfAttEncoder](rc-conv-self-att-encoder.md)
- [Model composition](composition.md)
- [Labels](../data/labels.md)
- [Prediction artifacts](../artifacts/predictions.md)
- [Checkpoints](../artifacts/checkpoints.md)
