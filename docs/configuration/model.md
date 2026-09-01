# Model configuration

Nested `model_config` trees for **v0.1.0a8**.

The canonical composition contract — top-level vs nestable roles, nested ref
shape, `model_name` uniqueness, predictor map keys, trimming geometry, and
validated examples — lives on
[Model composition](../models/composition.md).

## Quick rules

- Top-level CLI `model_type` must be `EncoderPredictor`
- Nested refs are exactly `{ "model_type", "model_config" }`
- Encoder slot: `ConvEncoder`, `RCConvEncoder`, `ConvSelfAttEncoder`, or
  `RCConvSelfAttEncoder`
- Predictor map: `ClassPredictor`, `RCClassPredictor`, `RegressPredictor`,
  `RCRegressPredictor`, `ProfilePredictor`, and/or `RCProfilePredictor`
- Every `model_config` needs a unique non-empty `model_name`
- `embedding_trimming` is required on the top-level config (integer ≥ 0)

## Schema snapshot

Documentation schema for the top-level tree:
[`encoder-predictor-model-config.schema.json`](../schemas/v0.1.0a8/encoder-predictor-model-config.schema.json).

<!-- schema: schemas/v0.1.0a8/encoder-predictor-model-config.schema.json -->
```json
{
  "model_name": "ep_main",
  "embedding_trimming": 0,
  "encoder": {
    "model_type": "ConvSelfAttEncoder",
    "model_config": { "model_name": "enc" }
  },
  "predictor": {
    "cls": {
      "model_type": "ClassPredictor",
      "model_config": { "model_name": "cls_head", "n_class": 2 }
    }
  }
}
```

## Related pages

- [Config overview](../config.md)
- [Hyperparameters](hyperparameters.md)
- [Schemas](../reference/schemas.md)
