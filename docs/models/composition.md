# Model composition

Top-level composition rules for **v0.1.0a8**.

- Only `EncoderPredictor` may appear as CLI `model_type`
- Nest one encoder (`ConvEncoder` or `ConvSelfAttEncoder`)
- Nest one or more prediction heads (`ClassPredictor`, `RegressPredictor`,
  `ProfilePredictor`) under `predictor`
- Every `model_name` in the tree must be unique

See [Concepts](../concepts.md) and [Config](../config.md).

Coming in a later documentation slice: complete nesting tables and invalid
trees.
