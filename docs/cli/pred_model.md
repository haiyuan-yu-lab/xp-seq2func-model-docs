# pred_model

Run inference with a trained `EncoderPredictor` and write per-head prediction
arrays for exact release **v0.1.0a8**. Optionally compute Captum input
attributions.

## Command snapshot

```text
usage: pred_model [-h] --config CONFIG --opath OPATH
                     [--verbosity VERBOSITY] --checkpoint CHECKPOINT --hparams
                     HPARAMS [--attribution {ig,saliency,deepshap}]
                     [--attribution-target TARGET]

Predict with a seq2func model

options:
  -h, --help            show this help message and exit
  --config CONFIG       Path to config JSON
  --opath OPATH         Output directory for artifacts
  --verbosity VERBOSITY
                        Log verbosity: 0, 1, or 2 (default: 1)
  --checkpoint CHECKPOINT
                        Path to top-level / parent .pth checkpoint
  --hparams HPARAMS     Path to top-level pre-inheritance hparams JSON
                        ({stem}.{top_level_model_name}.hparam.json)
  --attribution {ig,saliency,deepshap}
                        Optional Captum attribution method
                        (ig|saliency|deepshap). Omitted = off.
  --attribution-target TARGET
                        Optional explicit attribution target (requires
                        --attribution). Exactly one value. Forms:
                        <head>:probability:<k>, <head>:logit:<k>,
                        <head>:logit-difference:<p>,<n>,
                        <head>:logit:predicted, <head>:profile-
                        probability:<track>,<bin>, <head>:profile-
                        logit:<track>,<bin>, <head>:count:<track>,
                        <head>:log1p-count:<track>.
```

CLI help snapshot for **v0.1.0a8** (committed Markdown; documentation build does
not import the package or regenerate this text).

## Flags

| Flag | Required | Default | Notes |
| --- | --- | --- | --- |
| `--config` | yes | — | Prediction / test config JSON path |
| `--opath` | yes | — | Output directory for prediction arrays |
| `--checkpoint` | yes | — | Top-level / parent `.pth` checkpoint |
| `--hparams` | yes | — | Top-level pre-inheritance hparams JSON (`{stem}.{top_level_model_name}.hparam.json`) |
| `--verbosity` | no | `1` | Must be `0`, `1`, or `2` |
| `--attribution` | no | off | Captum method: `ig`, `saliency`, or `deepshap`. Omitted = off. |
| `--attribution-target` | no | — | Explicit target string (requires `--attribution`). Exactly one value. |

There is no `--device` flag. Prediction requires CUDA. `CUDA_VISIBLE_DEVICES` is
optional process environment (same idea as training) and is not a CLI flag.

## Required inputs

| Input | Contract |
| --- | --- |
| Prediction config | [Prediction configuration](../configuration/prediction.md) |
| Parent checkpoint | [Checkpoints](../artifacts/checkpoints.md) |
| Parent hparams sidecar | [Sidecars](../artifacts/sidecars.md), [Hyperparameters](../configuration/hyperparameters.md) |
| Arrays named by `test_data` | [Arrays](../data/arrays.md); labels optional per [Labels](../data/labels.md); profile masks forbidden per [Masks](../data/masks.md) |

## Outputs

Under `--opath`, successful runs always write one prediction artifact set per
head declared in `model_config.predictor`:

| Head type | Pattern | Shape | dtype |
| --- | --- | --- | --- |
| `ClassPredictor` | `{job}.{ep}.{head}.pred_class.npy` | `(N, n_class)` probabilities | float32 |
| `RegressPredictor` | `{job}.{ep}.{head}.pred.npy` | `(N, 1)` | float32 |
| `ProfilePredictor` | `{job}.{ep}.{head}.profile.npy` and `.count.npy` | `(N, T, P)` and `(N, T)` | float32 |

`{job}` is `job_name`, `{ep}` is the top-level `EncoderPredictor` `model_name`,
and `{head}` is that head's `model_name`. Full tables:
[Predictions](../artifacts/predictions.md).

Optional attribution arrays (when `--attribution` is set) are summarized under
[Attribution flags](#attribution-flags-summary). Deep attribution targeting is
documented separately in [Attribution](../workflows/attribution.md) and
[Attributions](../artifacts/attributions.md).

## Exit outcomes

| Outcome | Exit | Notes |
| --- | --- | --- |
| Success | `0` | Prediction arrays written under `--opath` |
| Failure | non-zero | Diagnostic text on stderr |

## Failure conditions

Failures include (described without stabilizing exact exception text):

- Missing required flags (`--config`, `--opath`, `--checkpoint`, `--hparams`)
- Verbosity outside `{0, 1, 2}`
- Unreadable or invalid JSON for config or hparams
- Missing, unknown, or forbidden prediction-config keys (see
  [Prediction configuration](../configuration/prediction.md))
- Top-level `model_type` other than `EncoderPredictor`
- Schema / composition mismatches in `model_config` or hparams
- No CUDA device available to the process
- Invalid or unreadable parent checkpoint / hparams sidecar
- Data shape, dtype, or alignment failures on `test_data`
- Empty path lists or invalid `source_fracs`
- `mask_npy` present on a test profile payload
- Profile test labels supplied without both `profile_npy` and `count_npy`
- `--attribution-target` without `--attribution`
- More than one attribution target value
- Targetless (`--attribution` only) attribution when any `ProfilePredictor`
  head is present
- Invalid attribution method or target syntax

## Attribution flags (summary)

Attribution is optional CLI behavior. Deep dive pages own the full target
grammar and filename tables; this command page records the flags and common
outcomes.

| Mode | CLI | Writes |
| --- | --- | --- |
| Off | omit `--attribution` | Prediction arrays only |
| Legacy | `--attribution METHOD` only | One `attr_{METHOD}.npy` per head; rejected if any profile head is present |
| Explicit | `--attribution METHOD --attribution-target TARGET` | One target-qualified `attr_*.npy` for the selected head |

`--attribution-target` forms (exactly one value):

```text
<head>:probability:<k>
<head>:logit:<k>
<head>:logit-difference:<p>,<n>
<head>:logit:predicted
<head>:profile-probability:<track>,<bin>
<head>:profile-logit:<track>,<bin>
<head>:count:<track>
<head>:log1p-count:<track>
```

Predictor map keys must not contain `:`. Ordinary prediction arrays for all
heads are unchanged when attribution is enabled. See
[Attribution](../workflows/attribution.md).

## Minimal example

Placeholder paths only; this documentation does not ship datasets or
checkpoints.

```bash
pred_model \
  --config /path/to/pred.json \
  --hparams /path/to/out/demo_train.ep_main.hparam.json \
  --checkpoint /path/to/out/demo_train.ep_main.pth \
  --opath /path/to/pred_out \
  --verbosity 1
```

## Behavior

1. Validates the prediction config and hparams against the `EncoderPredictor`
   composition in `model_config`
2. Requires CUDA
3. Builds the model, loads `--checkpoint`, and runs prediction over `test_data`
   (labels not required)
4. Writes prediction arrays for every head under `--opath`
5. If `--attribution` is set, optionally writes attribution arrays (legacy or
   explicit target mode)

## Related pages

- [Prediction configuration](../configuration/prediction.md)
- [Predictions](../artifacts/predictions.md)
- [Profiles](../profiles.md)
- [Train to predict](../workflows/train-to-predict.md)
- [Config overview](../config.md)
- [Attribution](../workflows/attribution.md)
