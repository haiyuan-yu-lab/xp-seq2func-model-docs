# ConvEncoder

Convolutional encoder component for **v0.1.0a8**.

Nestable only under `EncoderPredictor.encoder`. Cannot be used as top-level
CLI `model_type`. See [Model composition](composition.md).

## Configuration

Nested `model_config` is identity-only:

| Key | Type | Notes |
| --- | --- | --- |
| `model_name` | non-empty string | Unique across the composition tree |

Architecture lives in hyperparameters, not in `model_config`.

```json
{
  "model_type": "ConvEncoder",
  "model_config": { "model_name": "enc" }
}
```

## Hyperparameters

Under top-level hparams `encoder` (pre-inheritance):

| Key | Type | Notes |
| --- | --- | --- |
| `n_layers` | integer ≥ 1 | Required |
| `kernel_size` | odd integer ≥ 1 | Required |
| `dilation` | array of integers ≥ 1 | Required; length ≥ `n_layers` (prefix used) |
| `batch_size` | integer ≥ 1 | Optional; inherits from parent when omitted |
| `learning_rate` | number ≥ 0 | Optional; `0` freezes this encoder |
| `n_channels` | integer ≥ 1 | Optional; inherits from parent when omitted |

Unknown keys fail closed. Inheritance rules live on
[Hyperparameters](../configuration/hyperparameters.md).

```json
{
  "n_layers": 2,
  "kernel_size": 3,
  "dilation": [1, 2]
}
```

## Inputs and outputs

| Tensor | Shape | Notes |
| --- | --- | --- |
| Input | `(B, 4, L)` | One-hot bases in channel order A, C, G, T |
| Output | `(B, C, L)` | Embedding before top-level trimming |

`EncoderPredictor` then trims `embedding_trimming` bases from each end so heads
see `(B, C, L_embed)` with `L_embed = L - 2T > 0`.

## Nested data payload

Under each data block's `encoder` key:

| Key | Value |
| --- | --- |
| `ohe_npy` | Path string or non-empty path array |
| `label` | Must be `null` |

## Related pages

- [ConvSelfAttEncoder](conv-self-att-encoder.md)
- [RCConvEncoder](rc-conv-encoder.md)
- [Model composition](composition.md)
- [Hyperparameters](../configuration/hyperparameters.md)
- [Arrays](../data/arrays.md)
