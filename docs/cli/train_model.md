# train_model

Train an `EncoderPredictor` with fixed hyperparameters.

## Usage

```bash
train_model --config CONFIG --opath OPATH --hparams HPARAMS [--verbosity N]
```

## Flags

| Flag | Required | Description |
| --- | --- | --- |
| `--config` | yes | Train config JSON |
| `--opath` | yes | Output directory |
| `--hparams` | yes | Top-level pre-inheritance hparams JSON |
| `--verbosity` | no | `0`, `1`, or `2` (default `1`) |

## Behavior

1. Validates the train config and hparams against the `EncoderPredictor`
   composition in `model_config`
2. Requires CUDA
3. Builds the model; if `init_checkpoint` is set, loads the listed modules from
   that `.pth` before training
4. Builds train and validation dataloaders from `train_data` / `val_data`
5. Optionally initializes W&B from `wandb` (skipped when `mode` is `disabled`)
6. Trains with early stopping (`grace_epochs`) and writes checkpoints under
   `--opath` using `job_name` as the stem

See [Config](../config.md#init_checkpoint-train--tune) for `init_checkpoint`
and [Formats](../formats.md) for array and checkpoint layouts.
