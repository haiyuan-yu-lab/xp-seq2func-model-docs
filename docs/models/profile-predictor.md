# ProfilePredictor

Profile prediction head for **v0.1.0a8**.

A **profile prediction head** contains one or more **profile tracks** and a
paired **profile count** per track. Public outputs are a **profile
distribution** over **profile bins** plus nonnegative counts.

Nestable only under `EncoderPredictor.predictor`. Composition rules and the
nested ref shape are on [Model composition](composition.md). Geometry, data
payloads (`profile_npy` / `count_npy` / optional `mask_npy`), component
hparams, artifacts, and attribution targets are on
[Profile reconstruction](../profiles.md).

For non-profile heads in this release, see [ClassPredictor](class-predictor.md)
and [RegressPredictor](regress-predictor.md).
