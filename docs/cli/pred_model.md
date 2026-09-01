# pred_model

Run inference with a trained `EncoderPredictor` and write per-head prediction
arrays. Optionally compute Captum input attributions.

## Usage

```bash
pred_model --config CONFIG --opath OPATH --checkpoint CHECKPOINT \
  --hparams HPARAMS [--attribution METHOD] \
  [--attribution-target TARGET] [--verbosity N]
```

## Flags

| Flag | Required | Description |
| --- | --- | --- |
| `--config` | yes | Test / pred config JSON |
| `--opath` | yes | Output directory |
| `--checkpoint` | yes | Path to top-level / parent `.pth` checkpoint |
| `--hparams` | yes | Top-level pre-inheritance hparams JSON (`{stem}.{top_level_model_name}.hparam.json`) |
| `--attribution` | no | Captum method: `ig`, `saliency`, or `deepshap`. Omitted = off. |
| `--attribution-target` | no | Explicit `ClassPredictor` or `ProfilePredictor` target (requires `--attribution`). Exactly one value. |
| `--verbosity` | no | `0`, `1`, or `2` (default `1`) |

## Attribution targets

`--attribution-target` selects one head and one scalar. Forms:

```text
<head-key>:probability:<class-index>
<head-key>:logit:<class-index>
<head-key>:logit-difference:<positive-index>,<negative-index>
<head-key>:logit:predicted
<head-key>:profile-probability:<track-name>,<bin-index>
<head-key>:profile-logit:<track-name>,<bin-index>
<head-key>:count:<track-name>
<head-key>:log1p-count:<track-name>
```

- `probability` / fixed `logit` / `logit-difference` use the same scalar meaning for every row
- `logit:predicted` attributes each row's argmax-class logit
- Classification forms require a `ClassPredictor` head; profile and count forms require a `ProfilePredictor` head
- Track names must be configured on that head, and bin indices must be in `[0, P)` where `P` is the head's bin count for the input length
- `count` attributes the reconstructed count; `log1p-count` attributes the unrestricted internal log-count
- Predictor map keys must not contain `:` (validated for every `EncoderPredictor` config)

With an explicit target, `pred_model` writes **one** target-qualified attribution file for that head. Ordinary prediction arrays for all heads are unchanged.

## Behavior

1. Validates the test config and hparams
2. Requires CUDA
3. Builds the model, loads `--checkpoint`, and runs `predict` over `test_data`
   (labels not required)
4. Writes one prediction array per head under `--opath`:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred_class.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.profile.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.count.npy
```

`ClassPredictor` heads use `.pred_class.npy`, `RegressPredictor` heads use
`.pred.npy`, and `ProfilePredictor` heads use paired `.profile.npy` /
`.count.npy`.

5. If `--attribution` is set without `--attribution-target`, writes one legacy
   attribution array per head and emits a deprecation warning at verbosity ≥ 1:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.npy
```

Legacy `ClassPredictor` targets are per-row predicted-class logits (arrays may
mix class meanings). `RegressPredictor` targets channel 0. A model containing
any `ProfilePredictor` head rejects targetless attribution.

6. If `--attribution-target` is also set, writes one explicit file instead:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.probability_{k}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.logit_{k}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.logit-difference_{p}_{n}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.logit_predicted.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.profile-probability_{track}_{bin}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.profile-logit_{track}_{bin}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.count_{track}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.log1p-count_{track}.npy
```

Attribution arrays are float32 with shape `(N, 4, L)` (same layout as the
one-hot input). At verbosity ≥ 1, explicit runs log the resolved method, head,
domain, and target.

See [Config](../config.md) and [Formats](../formats.md) for details.
