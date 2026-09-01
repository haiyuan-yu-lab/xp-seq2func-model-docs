# Masks

**Positional validity mask** contracts for **v0.1.0a8**.

Optional boolean `mask_npy` on train/val **profile prediction head** payloads
marks retained positions eligible for position-wise profile losses and Pearson
diagnostics. Forbidden on test payloads and on scalar-head payloads.

Workflow effects (what masks change vs leave alone):
[Profile masks](../workflows/profile-masks.md). Glossary:
[Positional validity mask](../reference/glossary.md#positional-validity-mask).

## Placement

| Surface | Rule |
| --- | --- |
| Train / val profile payload | Optional `mask_npy` alongside required `profile_npy` / `count_npy` |
| Test / prediction profile payload | `mask_npy` invalid (rejected) |
| `ClassPredictor` / `RegressPredictor` | `mask_npy` invalid |
| Path form | Non-empty string, or non-empty path array parallel to `encoder.ohe_npy` |
| Coverage | When present for a head, must cover every source for that head |
| Independence | Train and val choose independently; multiple profile heads may share files |

<!-- schema: schemas/v0.1.0a8/profile-label-payload.schema.json -->
```json
{
  "profile_npy": "/path/to/train_profile.npy",
  "count_npy": "/path/to/train_count.npy",
  "mask_npy": "/path/to/train_mask.npy"
}
```

Missing `mask_npy` is equivalent to an all-`true` mask (existing configs without
masks keep all-valid profile-loss behavior).

## Array contract

For every source, the loaded mask must satisfy:

| Property | Contract |
| --- | --- |
| Shape | Exact `(N_s, L_embed)` |
| Rank | Rank-2 only |
| dtype | NumPy boolean |
| Values | `true` = eligible retained base; `false` = excluded |
| Alignment | Same `N_s` as that source's OHE, profile, and count arrays |
| Cross-source | Same retained length `L_embed` as other sources used by the model |

Invalid forms (fail closed):

- Integer, floating, string, object, or complex dtypes (even if values are 0/1)
- Rank-1 masks
- Singleton-track forms such as `(N, 1, L_embed)`
- Profile-bin masks shaped `(N, P)`
- Track-specific masks shaped `(N, T, L_embed)`

All-false rows are valid data. Validation does not require at least one `true`
position.

## Profile-bin reduction

Stored masks are at retained **base** resolution. For bin size `K = bin_size`
and `P = L_embed / K`, derive bin validity `M` shaped `(B, P)`:

```text
M[i,p] = AND over r in [p*K, (p+1)*K) of m[i,r]
```

| Rule | Behavior |
| --- | --- |
| Validity | A **profile bin** is valid iff every retained base in that bin is `true` |
| Sharing | `M` is shared across all `T` tracks in that head |
| Alignment | Same left-edge, non-overlapping bins as profile average-pooling |
| Partial bins | No padding, truncation, threshold, or fractional validity weight |
| `bin_size = 1` | `M` equals the stored base-resolution mask |

## Effects (summary)

| Surface | Affected by mask? |
| --- | --- |
| Profile distribution loss (`profile_cross_entropy`) | Yes — invalid bins excluded |
| Profile Pearson diagnostics | Yes — valid bins only |
| Profile count loss (`log1p_mse`) | No |
| Public `.profile.npy` / `.count.npy` predictions | No |
| Attribution arrays | No |

## Related pages

- [Profile masks workflow](../workflows/profile-masks.md)
- [Profiles](../profiles.md)
- [Labels](labels.md)
- [ProfilePredictor](../models/profile-predictor.md)
- [Geometry](geometry.md)
