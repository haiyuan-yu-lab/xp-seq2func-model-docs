# Labels

Label array contracts for prediction heads in **v0.1.0a8**.

Train and validation require a label payload for **every** head declared in
`model_config.predictor`, including zero-weight heads. Prediction may omit
labels.

## Field names

| Head type | Released field(s) |
| --- | --- |
| `ClassPredictor` | `label_npy` |
| `RegressPredictor` | `label_npy` |
| `ProfilePredictor` | `profile_npy`, `count_npy`, optional `mask_npy` (train/val only) |

Scalar heads consistently use **`label_npy`**. Do not use a bare `label` key
on a predictor payload (`encoder.label` is a separate field that must be
`null`).

## Classification labels (`ClassPredictor`)

| Property | Contract |
| --- | --- |
| Path form | Non-empty string or non-empty path array aligned to OHE sources |
| Requiredness | Required on train/val for every classification head |
| Shape | `(N, n_class)` per source |
| Trailing width | Must equal that head's `model_config.n_class` (`≥ 2`) |
| Values | Real integer or floating dtype; nonnegative; floating values must be finite |
| Alignment | Same `S` and per-source `N_s` as `encoder.ohe_npy` |
| Cross-source | Trailing shape `(n_class,)` must match across sources |

Typical targets are one-hot (or soft) class indicators with width `n_class`.

## Regression labels (`RegressPredictor`)

| Property | Contract |
| --- | --- |
| Path form | Non-empty string or non-empty path array aligned to OHE sources |
| Requiredness | Required on train/val for every regression head |
| Shape | `(N, 1)` per source |
| Rank | Must be rank-2; rank-1 `(N,)` arrays fail |
| Values | Real integer or floating dtype; nonnegative; floating values must be finite |
| Alignment | Same `S` and per-source `N_s` as `encoder.ohe_npy` |
| Cross-source | Trailing shape `(1,)` must match across sources |

## Profile labels (summary)

| Field | Train/val | Shape |
| --- | --- | --- |
| `profile_npy` | required | `(N, T, P)` |
| `count_npy` | required | `(N, T)` |
| `mask_npy` | optional | boolean `(N, L_embed)` |

Full profile geometry and mask rules: [Profiles](../profiles.md) and
[Masks](masks.md). Do not put `label_npy` on a profile payload.

## Cross-field invariants

| Invariant | Rule |
| --- | --- |
| Head coverage | Train/val predictor map keys ↔ `model_config.predictor` keys |
| Source count | Every path field uses the same `S` as `encoder.ohe_npy` |
| Row alignment | For each source `s`, all arrays share `N_s` |
| Shared length | All OHE sources share `L`; scalar trailing widths are fixed per head |
| Path emptiness | Empty path arrays fail |

## Illustrative payloads

Classification:

```json
{
  "label_npy": "/path/to/train_cls_labels.npy"
}
```

Regression:

```json
{
  "label_npy": "/path/to/train_reg_labels.npy"
}
```

Multi-source classification:

```json
{
  "label_npy": [
    "/path/to/src0_cls_labels.npy",
    "/path/to/src1_cls_labels.npy"
  ]
}
```

## Related pages

- [Splits](splits.md)
- [Arrays](arrays.md)
- [ClassPredictor](../models/class-predictor.md)
- [RegressPredictor](../models/regress-predictor.md)
- [Profiles](../profiles.md)
