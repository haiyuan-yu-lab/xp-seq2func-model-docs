# pred_model

Run inference with a trained `EncoderPredictor` and write per-head prediction
arrays.

## Usage

```bash
pred_model --config CONFIG --opath OPATH --checkpoint CHECKPOINT \
  --hparams HPARAMS [--verbosity N]
```

## Flags

| Flag | Required | Description |
| --- | --- | --- |
| `--config` | yes | Test / pred config JSON |
| `--opath` | yes | Output directory |
| `--checkpoint` | yes | Path to top-level / parent `.pth` checkpoint |
| `--hparams` | yes | Top-level pre-inheritance hparams JSON (`{stem}.{top_level_model_name}.hparam.json`) |
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

See [Config](../config.md) and [Formats](../formats.md) for details.
