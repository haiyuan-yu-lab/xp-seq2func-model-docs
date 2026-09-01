# Attributions

Attribution array artifacts from `pred_model` in exact release **v0.1.0a8**.

Target grammar, modes, and method notes:
[Attribution workflow](../workflows/attribution.md). Flag summary:
[`pred_model`](../cli/pred_model.md).

## Producers and consumers

| Role | Surface |
| --- | --- |
| Producer | `pred_model` with `--attribution {ig,saliency,deepshap}` writes under `--opath` |
| Consumers | Downstream interpretation notebooks and analysis scripts that load `.npy` arrays |

Attribution is optional. Successful runs always write prediction arrays for
every head; attribution files appear only when a method is selected. Prediction
config JSON forbids `attribution*` keys.

## Shared array contract

Every attribution artifact uses the same geometry:

| Property | Contract |
| --- | --- |
| Shape | `(N, 4, L)` |
| dtype | float32 |
| Channel axis | Bases `A`, `C`, `G`, `T` in that order |
| `N` | Test rows after deterministic multi-source ordering |
| `L` | Input sequence length from the one-hot encoder arrays |

Values are signed input attributions for the selected scalar target. Masks
used in training do not change these arrays.

## Filename tokens

```text
{job}.{ep}.{head}.attr_{method}[.qualifier].npy
```

| Token | Source |
| --- | --- |
| `{job}` | Prediction-config `job_name` |
| `{ep}` | Top-level `EncoderPredictor` `model_name` |
| `{head}` | That head's `model_name` (not the predictor map key) |
| `{method}` | `ig`, `saliency`, or `deepshap` |
| `.qualifier` | Present only for explicit `--attribution-target` |

## Modes and target meaning

| Mode | CLI | Files | Target meaning |
| --- | --- | --- | --- |
| Off | omit `--attribution` | None | — |
| Legacy | `--attribution METHOD` only | One file per `ClassPredictor` / `RCClassPredictor` / `RegressPredictor` / `RCRegressPredictor` head | Classification: **predicted-class attribution** (row-dependent argmax). Regression: channel `0`. Rejected if any `ProfilePredictor` / `RCProfilePredictor` is present. |
| Explicit | `--attribution METHOD --attribution-target TARGET` | Exactly one target-qualified file | Scalar named by `TARGET`; fixed class / profile / count targets are row-independent; `logit:predicted` is row-dependent |

## Legacy filenames

```text
{job}.{ep}.{head}.attr_{method}.npy
```

Example:

```text
demo_pred.ep_main.cls_head.attr_ig.npy
demo_pred.ep_main.reg_head.attr_ig.npy
```

Legacy mode does not write a shared **attribution target** across classification
rows: each row's class is chosen from that row's prediction.

## Explicit filenames

One file per invocation. Qualifiers map from the target string:

| Target form | Filename pattern |
| --- | --- |
| `<head>:probability:<k>` | `{job}.{ep}.{head}.attr_{method}.probability_{k}.npy` |
| `<head>:logit:<k>` | `{job}.{ep}.{head}.attr_{method}.logit_{k}.npy` |
| `<head>:logit-difference:<p>,<n>` | `{job}.{ep}.{head}.attr_{method}.logit-difference_{p}_{n}.npy` |
| `<head>:logit:predicted` | `{job}.{ep}.{head}.attr_{method}.logit_predicted.npy` |
| `<head>:profile-probability:<track>,<bin>` | `{job}.{ep}.{head}.attr_{method}.profile-probability_{track}_{bin}.npy` |
| `<head>:profile-logit:<track>,<bin>` | `{job}.{ep}.{head}.attr_{method}.profile-logit_{track}_{bin}.npy` |
| `<head>:count:<track>` | `{job}.{ep}.{head}.attr_{method}.count_{track}.npy` |
| `<head>:log1p-count:<track>` | `{job}.{ep}.{head}.attr_{method}.log1p-count_{track}.npy` |

Examples (placeholder stems):

```text
demo_pred.ep_main.cls_head.attr_ig.probability_1.npy
demo_pred.ep_main.cls_head.attr_saliency.logit-difference_1_0.npy
demo_pred.ep_main.cls_head.attr_deepshap.logit_predicted.npy
demo_pred.ep_profile.atac_head.attr_ig.profile-probability_atac_a_12.npy
demo_pred.ep_profile.atac_head.attr_ig.log1p-count_atac_a.npy
```

Structural target-string examples validate against
[attribution-target-string.schema.json](../schemas/v0.1.0a8/attribution-target-string.schema.json)
on the [Attribution workflow](../workflows/attribution.md#examples) page.

## Methods (artifact context)

| Method | Effect on artifacts |
| --- | --- |
| `ig` | Integrated Gradients; zero baseline; `n_steps=50` |
| `saliency` | Signed saliency |
| `deepshap` | DeepLiftShap with a duplicated all-zeros reference batch of size `2` |

The method token appears in the filename; it does not change shape or dtype.

## Related pages

- [Attribution workflow](../workflows/attribution.md)
- [`pred_model`](../cli/pred_model.md)
- [Predictions](predictions.md)
- [Profiles](../profiles.md)
- [Formats overview](../formats.md)
- [Schemas](../reference/schemas.md)
