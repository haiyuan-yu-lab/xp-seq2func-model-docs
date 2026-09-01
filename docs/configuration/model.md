# Model configuration

Nested `model_config` trees for **v0.1.0a8**.

- Top-level CLI `model_type` must be `EncoderPredictor`
- Encoder and prediction-head components nest with their own `model_type` and
  `model_config`
- All `model_name` values must be unique

See [Config](../config.md) and [Model composition](../models/composition.md).

Coming in a later documentation slice: recursive field tables per component.
