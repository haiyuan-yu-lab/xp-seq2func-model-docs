# Predictions

Prediction array artifacts written by `pred_model` in **v0.1.0a8**.

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

## Classification (`ClassPredictor`)

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

## Regression (`RegressPredictor`)

| Property | Contract |
| --- | --- |
| Filename | `{job}.{ep}.{head}.pred.npy` |
| Shape | `(N, 1)` |
| dtype | float32 |
| Values | Scalar regression outputs |
| Producer | `pred_model` |
| Consumers | Downstream regression analysis |

## Profile (`ProfilePredictor`) — summary

Profile heads write a paired pair of arrays. Deep profile geometry belongs to
a later documentation slice; the public filenames and shapes are:

| Artifact | Filename | Shape | dtype |
| --- | --- | --- | --- |
| Profile | `{job}.{ep}.{head}.profile.npy` | `(N, T, P)` | float32 |
| Count | `{job}.{ep}.{head}.count.npy` | `(N, T)` | float32 |

`T` is `len(track_names)`; `P` is the bin count for the retained window. See
[Profiles](../profiles.md).

## Always written

Prediction arrays for **all** heads are always written on a successful run,
whether or not `--attribution` is set and whether or not `test_data` includes
labels.

## Related pages

- [`pred_model`](../cli/pred_model.md)
- [Prediction configuration](../configuration/prediction.md)
- [Formats overview](../formats.md)
- [ClassPredictor](../models/class-predictor.md)
- [RegressPredictor](../models/regress-predictor.md)
- [Train to predict](../workflows/train-to-predict.md)
