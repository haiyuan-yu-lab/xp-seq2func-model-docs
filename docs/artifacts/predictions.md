# Predictions

Prediction array artifacts written by `pred_model` in **v0.1.0a9**.

## Producers and consumers

| Role | Surface |
| --- | --- |
| Producer | `pred_model` writes under `--opath` for every head in `model_config.predictor` |
| Consumer | Downstream analysis, notebooks, and evaluation scripts that load `.npy` arrays |

Attribution arrays are separate artifacts; see
[Attributions](attributions.md) and [Attribution](../workflows/attribution.md).

## Filename pattern

```text
{job}.{ep}.{head}.<suffix>.npy
```

| Token | Source |
| --- | --- |
| `{job}` | Prediction-config `job_name` |
| `{ep}` | Top-level `EncoderPredictor` `model_name` |
| `{head}` | That head's `model_name` |

## Classification (`ClassPredictor` / `RCClassPredictor`)

| Property | Contract |
| --- | --- |
| Filename | `{job}.{ep}.{head}.pred_class.npy` |
| Shape | `(N, n_class)` |
| dtype | float32 |
| Values | Class probabilities |
| Producer | `pred_model` |
| Consumers | Downstream class-score analysis |

`n_class` matches that head's `model_config.n_class`. `N` is the number of
test rows after deterministic multi-source ordering.

## Regression (`RegressPredictor` / `RCRegressPredictor`)

| Property | Contract |
| --- | --- |
| Filename | `{job}.{ep}.{head}.pred.npy` |
| Shape | `(N, 1)` |
| dtype | float32 |
| Values | Scalar regression outputs |
| Producer | `pred_model` |
| Consumers | Downstream regression analysis |

## Profile (`ProfilePredictor` / `RCProfilePredictor`)

Each profile prediction head writes **both** a profile-distribution array and a
profile-count array. Masks used during training do not change these artifacts.

### Profile distribution

| Property | Contract |
| --- | --- |
| Filename | `{job}.{ep}.{head}.profile.npy` |
| Shape | `(N, T, P)` |
| dtype | float32 |
| Values | Profile-distribution probabilities; each row/track sums to 1 over `P` within numerical tolerance |
| Channel order | `track_names` order (`T = len(track_names)`) |
| Bin geometry | `P = L_embed / bin_size` with exact divisibility; bin `j` covers retained positions `[j * bin_size, (j + 1) * bin_size)` |
| Producer | `pred_model` |
| Consumers | Downstream profile-shape analysis |

### Profile count

| Property | Contract |
| --- | --- |
| Filename | `{job}.{ep}.{head}.count.npy` |
| Shape | `(N, T)` |
| dtype | float32 |
| Values | Nonnegative reconstructed profile counts (paired one-to-one with tracks) |
| Channel order | Same `track_names` order as the distribution array |
| Producer | `pred_model` |
| Consumers | Downstream magnitude analysis |

`N` is the number of test rows after deterministic multi-source ordering.
Deep geometry and count pairing: [Profiles](../profiles.md) and
[ProfilePredictor](../models/profile-predictor.md).

## Always written

Prediction arrays for **all** heads are always written on a successful run,
whether or not `--attribution` is set and whether or not `test_data` includes
labels.

## Related pages

- [`pred_model`](../cli/pred_model.md)
- [Prediction configuration](../configuration/prediction.md)
- [Formats overview](../formats.md)
- [ClassPredictor](../models/class-predictor.md)
- [RCClassPredictor](../models/rc-class-predictor.md)
- [RegressPredictor](../models/regress-predictor.md)
- [RCRegressPredictor](../models/rc-regress-predictor.md)
- [ProfilePredictor](../models/profile-predictor.md)
- [RCProfilePredictor](../models/rc-profile-predictor.md)
- [Profiles](../profiles.md)
- [Train to predict](../workflows/train-to-predict.md)
