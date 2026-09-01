# Profile masks workflow

How **positional validity masks** interact with profile training and prediction
in **v0.1.0a9**.

A positional validity mask is a boolean annotation aligned to retained sequence
positions. `true` marks positions eligible for position-wise profile losses and
metrics. Masks are data annotations only: they add no model-config field,
hparams, checkpoint metadata, learned state, or prediction artifact.

Array contracts: [Masks](../data/masks.md). Head contracts:
[ProfilePredictor](../models/profile-predictor.md) and
[Profiles](../profiles.md).

## When masks apply

| Split | `mask_npy` |
| --- | --- |
| Train | Optional per profile head |
| Validation | Optional per profile head (independent of train) |
| Test / prediction | Forbidden |

Multiple profile heads may omit, provide, or share mask files. Scalar heads
never accept masks.

## What masks change

| Surface | Effect |
| --- | --- |
| Profile distribution loss | Invalid bins excluded from label normalization and the logits softmax domain |
| Empty eligible sets | Batch/split reductions stay finite and differentiable (empty ⇒ zero mean for that component) |
| Profile Pearson diagnostics | Computed over valid bins only; ineligible pairs yield `NaN` keys rather than zeros |
| Epoch `train_loss` / `val_loss` | Uses masked profile-component means with component weights |

## What masks do **not** change

| Surface | Behavior |
| --- | --- |
| Public profile distributions | Softmax over **all** `P` bins; written `.profile.npy` unchanged by masks |
| Profile counts | `log1p_mse` and `.count.npy` ignore masks |
| Count labels | Remain authoritative magnitudes |
| Attribution | Target selection and `(N, 4, L)` arrays ignore masks |
| Deterministic row order | Mask processing must not reorder samples |

## Training path

1. Optionally reference `mask_npy` on train and/or val profile payloads
2. Validate shape `(N, L_embed)`, boolean dtype, and source alignment
3. Reduce each mask to profile-bin validity (AND within each bin)
4. Apply that validity inside `profile_cross_entropy` and Pearson diagnostics
5. Leave count loss, predictions, and attributions unmasked

Configs without `mask_npy` keep all-valid profile-loss behavior.

## Prediction path

`pred_model` does not compute label-dependent losses or metrics. Supplying
`mask_npy` on `test_data` fails closed. Omit masks on prediction configs even
when training used them.

## Related pages

- [Masks](../data/masks.md)
- [Profiles](../profiles.md)
- [Metrics](../artifacts/metrics.md)
- [Predictions](../artifacts/predictions.md)
- [Prediction configuration](../configuration/prediction.md)
