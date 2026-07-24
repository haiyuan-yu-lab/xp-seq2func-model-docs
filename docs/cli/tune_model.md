# tune_model

Run a Weights & Biases hyperparameter sweep for an `EncoderPredictor`.

## Usage

```bash
tune_model --config CONFIG --opath OPATH --tune-space TUNE_SPACE \
  [--num-agents N] [--max-trials N] [--verbosity N]
```

## Flags

| Flag | Required | Description |
| --- | --- | --- |
| `--config` | yes | Tune config JSON |
| `--opath` | yes | Output directory |
| `--tune-space` | yes | Tune-space JSON (`method` + `parameters`) |
| `--num-agents` | no | Concurrent W&B agent workers (integer ≥ 1). Default: number of `CUDA_VISIBLE_DEVICES` tokens. When set, must equal that count. |
| `--max-trials` | no | Per-agent W&B trial cap (integer ≥ 1). Default: `20`. |
| `--verbosity` | no | `0`, `1`, or `2` (default `1`) |

## Environment

`CUDA_VISIBLE_DEVICES` must be set to a comma-separated list of non-empty,
unique device tokens. Each agent worker pins to one token.

## Behavior

1. Validates the tune config and tune-space against `model_config`
2. Creates or resumes a W&B sweep from `wandb.sweep_id` / `wandb.sweep_name`
3. Launches one agent process per device token
4. Each trial samples hparams, builds the model (applying `init_checkpoint` when
   set), trains with early stopping, and logs metrics (including `val_loss`
   with a `min` summary for sweep optimization)

`job_name`, `num_agents`, and `max_trials` are not allowed inside the tune
config JSON — use the CLI flags for agent/trial controls. Do not put
`init_checkpoint` in the tune-space file; it belongs only on the tune config.

See [Config](../config.md#init_checkpoint-train--tune) and
[Formats](../formats.md) for JSON layouts.
