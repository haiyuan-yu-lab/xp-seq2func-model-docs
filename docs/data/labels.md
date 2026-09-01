# Labels

Label array contracts for prediction heads in **v0.1.0a9**.

Train and validation require a label payload for **every** head declared in
`model_config.predictor`, including zero-weight heads. Prediction may omit
labels.

## Field names

| Head type | Released field(s) |
| --- | --- |
| `ClassPredictor` | `label_npy` |
| `RCClassPredictor` | `label_npy` |
| `RegressPredictor` | `label_npy` |
| `RCRegressPredictor` | `label_npy` |
| `ProfilePredictor` | `profile_npy`, `count_npy`, optional `mask_npy` (train/val only) |
| `RCProfilePredictor` | `profile_npy`, `count_npy`, optional `mask_npy` (train/val only) |

Scalar heads consistently use **`label_npy`**. Do not use a bare `label` key
on a predictor payload (`encoder.label` is a separate field that must be
`null`).

## Classification labels (`ClassPredictor` / `RCClassPredictor`)

| Property | Contract |
| --- | --- |
| Path form | Non-empty string or non-empty path array aligned to OHE sources |
| Requiredness | Required on train/val for every classification head |
| Shape | `(N, n_class)` per source |
| Trailing width | Must equal that head's `model_config.n_class` (`≥ 2`) |
| Values | Real integer or floating dtype; floating values must be finite. Typical targets are one-hot or soft class indicators |
| Alignment | Same `S` and per-source `N_s` as `encoder.ohe_npy` |
| Cross-source | Trailing shape `(n_class,)` must match across sources |

## Regression labels (`RegressPredictor` / `RCRegressPredictor`)

| Property | Contract |
| --- | --- |
| Path form | Non-empty string or non-empty path array aligned to OHE sources |
| Requiredness | Required on train/val for every regression head |
| Shape | `(N, 1)` per source |
| Rank | Must be rank-2; rank-1 `(N,)` arrays fail |
| Values | Continuous real targets; real integer or floating dtype; floating values must be finite. Negatives are allowed (nonnegativity is a profile/count rule, not a regression rule) |
| Alignment | Same `S` and per-source `N_s` as `encoder.ohe_npy` |
| Cross-source | Trailing shape `(1,)` must match across sources |

## Profile labels (`ProfilePredictor` / `RCProfilePredictor`)

| Field | Train/val | Test | Shape | dtype / values |
| --- | --- | --- | --- | --- |
| `profile_npy` | required | optional with `count_npy` | `(N, T, P)` | Real integer or floating; finite nonnegative |
| `count_npy` | required | optional with `profile_npy` | `(N, T)` | Real integer or floating; finite nonnegative |
| `mask_npy` | optional | forbidden | `(N, L_embed)` | NumPy boolean only |

| Invariant | Rule |
| --- | --- |
| Pairing | `profile_npy` and `count_npy` are always required together when a profile payload is present |
| Rank | Profile arrays must be rank-3 even when `T = 1` (rank-2 shortcuts fail) |
| Geometry | `T = len(track_names)`; `P = L_embed / bin_size` with exact divisibility |
| Alignment | Same `S` and per-source `N_s` as `encoder.ohe_npy` |
| Cross-source | Trailing shapes `(T, P)` / `(T,)` and `L_embed` must match across sources |
| Count pairing | Count labels are authoritative; equality to profile-bin sums is not required |
| Forbidden keys | Do not put `label_npy` on a profile payload |

Full mask tables: [Masks](masks.md). Reconstruction overview: [Profiles](../profiles.md).

<!-- schema: schemas/v0.1.0a9/profile-label-payload.schema.json -->
```json
{
  "profile_npy": "/path/to/train_profile.npy",
  "count_npy": "/path/to/train_count.npy",
  "mask_npy": "/path/to/train_mask.npy"
}
```

<!-- schema: schemas/v0.1.0a9/profile-test-label-payload.schema.json -->
```json
{
  "profile_npy": "/path/to/test_profile.npy",
  "count_npy": "/path/to/test_count.npy"
}
```

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

## Representative invalid cases

Describe conditions only; exact exception strings are not stabilized.

| Case | Why it fails |
| --- | --- |
| Scalar payload uses `"label"` instead of `"label_npy"` | Released field name is `label_npy` |
| Regression array shaped `(N,)` | Trailing width `1` is required |
| Classification width ≠ `n_class` | Trailing shape must match the head config |
| Profile payload with only `profile_npy` | `count_npy` must be paired |
| Profile `mask_npy` under `test_data` | Masks are train/val only |
| Empty `label_npy` path array | Empty path lists fail closed |

## Related pages

- [Splits](splits.md)
- [Arrays](arrays.md)
- [ClassPredictor](../models/class-predictor.md)
- [RCClassPredictor](../models/rc-class-predictor.md)
- [RCRegressPredictor](../models/rc-regress-predictor.md)
- [RegressPredictor](../models/regress-predictor.md)
- [Profiles](../profiles.md)
- [Masks](masks.md)
- [ProfilePredictor](../models/profile-predictor.md)
