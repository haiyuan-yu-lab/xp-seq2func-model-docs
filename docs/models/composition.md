# Model composition

Top-level composition rules for **v0.1.0a8**.

Only `EncoderPredictor` may appear as the CLI `model_type`. Encoders and
prediction heads nest under that tree; they are never valid top-level CLI
`model_type` values.

## Roles

| Role | Allowed `model_type` | Where it appears |
| --- | --- | --- |
| Top-level model | `EncoderPredictor` | CLI `model_type` / `model_config` |
| Encoder (nestable) | `ConvEncoder`, `ConvSelfAttEncoder` | `model_config.encoder` only |
| Prediction head (nestable) | `ClassPredictor`, `RegressPredictor`, `ProfilePredictor` | `model_config.predictor` map only |

Nested components always use the exact reference shape
`{ "model_type", "model_config" }` — no other keys.

## Top-level `model_config`

| Key | Type | Notes |
| --- | --- | --- |
| `model_name` | non-empty string | Unique across the whole composition tree |
| `encoder` | nested ref | One encoder (`ConvEncoder` or `ConvSelfAttEncoder`) |
| `predictor` | object map | One or more prediction heads |
| `embedding_trimming` | integer ≥ 0 | Required; bases trimmed from each end of the encoder embedding |

Every `model_config` in the tree (top-level, encoder, and each head) needs its
own unique non-empty `model_name`.

### Predictor map

- Map keys are the caller-defined **prediction head** identities used across
  data, hparams, metrics, and attribution
- Keys must be non-empty and must not contain `:`
- Artifact filenames use each head's nested `model_name`, not the map key

## Forward geometry

```text
one-hot (B, 4, L)
  → encoder embedding (B, C, L)
  → trim T bases from each end
  → heads share trimmed embedding (B, C, L_embed)
```

| Quantity | Meaning |
| --- | --- |
| `L` | Input sequence length |
| `T` | `embedding_trimming` |
| `L_embed` | `L - 2T` (must be `> 0`) |
| `C` | Channel width (`n_channels` after inheritance) |

All prediction heads under one `EncoderPredictor` consume the same trimmed
embedding.

## Valid example

<!-- schema: schemas/v0.1.0a8/encoder-predictor-model-config.schema.json -->
```json
{
  "model_name": "ep_main",
  "embedding_trimming": 4,
  "encoder": {
    "model_type": "ConvEncoder",
    "model_config": { "model_name": "enc" }
  },
  "predictor": {
    "cls": {
      "model_type": "ClassPredictor",
      "model_config": { "model_name": "cls_head", "n_class": 3 }
    },
    "reg": {
      "model_type": "RegressPredictor",
      "model_config": { "model_name": "reg_head" }
    }
  }
}
```

## Invalid trees (illustrative)

Extra keys on a nested ref fail closed:

```json
{
  "model_type": "ConvEncoder",
  "model_config": { "model_name": "enc" },
  "extra": true
}
```

A nestable type as the CLI top-level `model_type` is rejected:

```json
{
  "model_type": "ConvEncoder",
  "model_config": { "model_name": "enc_only" }
}
```

Predictor map keys must not contain `:`:

```json
{
  "cls:main": {
    "model_type": "ClassPredictor",
    "model_config": { "model_name": "cls_head", "n_class": 2 }
  }
}
```

## Related pages

- [ConvEncoder](conv-encoder.md)
- [ConvSelfAttEncoder](conv-self-att-encoder.md)
- [ClassPredictor](class-predictor.md)
- [RegressPredictor](regress-predictor.md)
- [ProfilePredictor](profile-predictor.md) / [Profile reconstruction](../profiles.md)
- [Model configuration](../configuration/model.md)
- [Hyperparameters](../configuration/hyperparameters.md)
- [Schemas](../reference/schemas.md)
