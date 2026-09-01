# Losses

Loss objects paired with prediction heads in **v0.1.0a8**. This page is the
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

<!-- schema: schemas/v0.1.0a8/loss.schema.json -->
```json
{
  "type": "categorical_cross_entropy",
  "params": {}
}
```

## Supported types

| `type` | Typical head / component | `params` |
| --- | --- | --- |
| `categorical_cross_entropy` | `ClassPredictor` | `{}` |
| `mse` | `RegressPredictor` | `{}` |
| `profile_cross_entropy` | `ProfilePredictor` profile component | `{}` |
| `log1p_mse` | `ProfilePredictor` count component | `{}` |

Recommendations for scalar heads: use `categorical_cross_entropy` with
`ClassPredictor` and `mse` with `RegressPredictor`. Profile component losses
are mandatory for their respective profile / count branches; see
[Profile reconstruction](../profiles.md).

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

[`loss.schema.json`](../schemas/v0.1.0a8/loss.schema.json).

## Related pages

- [Hyperparameters](hyperparameters.md)
- [ClassPredictor](../models/class-predictor.md)
- [RegressPredictor](../models/regress-predictor.md)
- [Schemas](../reference/schemas.md)
