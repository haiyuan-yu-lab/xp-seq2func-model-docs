# pred_model

Run inference with a trained `EncoderPredictor` and write per-head prediction
arrays. Optionally compute Captum input attributions.

## Usage

```bash
pred_model --config CONFIG --opath OPATH --checkpoint CHECKPOINT \
  --hparams HPARAMS [--attribution METHOD] [--verbosity N]
```

## Flags

| Flag | Required | Description |
| --- | --- | --- |
| `--config` | yes | Test / pred config JSON |
| `--opath` | yes | Output directory |
| `--checkpoint` | yes | Path to top-level / parent `.pth` checkpoint |
| `--hparams` | yes | Top-level pre-inheritance hparams JSON (`{stem}.{top_level_model_name}.hparam.json`) |
| `--attribution` | no | Captum method: `ig`, `saliency`, or `deepshap`. Omitted = off. |
| `--verbosity` | no | `0`, `1`, or `2` (default `1`) |

## Behavior

1. Validates the test config and hparams
2. Requires CUDA
3. Builds the model, loads `--checkpoint`, and runs `predict` over `test_data`
   (labels not required)
4. Writes one `.pred_class.npy` per head under `--opath`:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred_class.npy
```

5. If `--attribution` is set, also writes one attribution array per head:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.npy
```

Attribution arrays are float32 with shape `(N, 4, L)` (same layout as the
one-hot input). The target class per sample is the argmax of that head's class
probabilities.

See [Config](../config.md) and [Formats](../formats.md) for details.
