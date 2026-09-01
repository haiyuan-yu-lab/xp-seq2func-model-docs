# Losses

Loss objects paired with prediction heads in **v0.1.0a9**. This page is the
canonical reference for the `{ "type", "params" }` contract.

Head wrappers that embed these objects are documented on
[Hyperparameters](hyperparameters.md).

## Object shape

| Key | Type | Notes |
| --- | --- | --- |
| `type` | string | One of the supported loss type names below |
| `params` | object | Must be `{}` for every supported type in this release |

Unknown keys on the loss object fail closed. Omitting `params` or supplying
non-empty `params` is rejected.

<!-- schema: schemas/v0.1.0a9/loss.schema.json -->
```json
{
  "type": "categorical_cross_entropy",
  "params": {}
}
```

## Supported types

| `type` | Typical head / component | `params` |
| --- | --- | --- |
| `categorical_cross_entropy` | `ClassPredictor` / `RCClassPredictor` | `{}` |
| `mse` | `RegressPredictor` / `RCRegressPredictor` | `{}` |
| `profile_cross_entropy` | `ProfilePredictor` / `RCProfilePredictor` profile component | `{}` |
| `log1p_mse` | `ProfilePredictor` / `RCProfilePredictor` count component | `{}` |

Recommendations for scalar heads: use `categorical_cross_entropy` with
`ClassPredictor` / `RCClassPredictor` and `mse` with `RegressPredictor` /
`RCRegressPredictor`. Profile component losses are mandatory for their
respective branches: `profile_cross_entropy` for the profile distribution and
`log1p_mse` for the profile count. See
[ProfilePredictor](../models/profile-predictor.md),
[RCProfilePredictor](../models/rc-profile-predictor.md), and
[Profile reconstruction](../profiles.md). Masked profile-loss behavior:
[Profile masks](../workflows/profile-masks.md).

## Invalid examples (illustrative)

```json
{
  "type": "mse",
  "params": { "reduction": "mean" }
}
```

```json
{
  "type": "categorical_cross_entropy"
}
```

```json
{
  "type": "mse",
  "params": {},
  "weight": 1.0
}
```

## Schema snapshot

[`loss.schema.json`](../schemas/v0.1.0a9/loss.schema.json).

## Related pages

- [Hyperparameters](hyperparameters.md)
- [ClassPredictor](../models/class-predictor.md) /
  [RCClassPredictor](../models/rc-class-predictor.md)
- [RegressPredictor](../models/regress-predictor.md) /
  [RCRegressPredictor](../models/rc-regress-predictor.md)
- [ProfilePredictor](../models/profile-predictor.md) /
  [RCProfilePredictor](../models/rc-profile-predictor.md)
- [Schemas](../reference/schemas.md)
