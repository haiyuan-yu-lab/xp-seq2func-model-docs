# Tuning workflow

End-to-end hyperparameter search with `tune_model` for **v0.1.0a9**.

This page explains GPU assignment, W&B requirements, sweep creation, agent
behavior, and the per-agent meaning of trial limits. Field tables live on the
canonical configuration pages — link there instead of duplicating them.

## Prerequisites

1. Install from tag `v0.1.0a9` ([Install](../install.md)).
2. Set `CUDA_VISIBLE_DEVICES` to the device tokens you want agents to use
   (required for tune).
3. Author a [tune config](../configuration/tune.md) and
   [tune-space](../configuration/tuning-spaces.md) JSON (placeholder paths
   only in these docs).
4. Ensure Weights & Biases can create or attach a sweep for the configured
   `project` / `entity` (`wandb.mode` is `online` or `offline`).

## GPU assignment

| Rule | Behavior |
| --- | --- |
| Requirement | `CUDA_VISIBLE_DEVICES` must be set |
| Token list | Comma-separated, non-empty tokens, no duplicates |
| Parent process | Does **not** initialize CUDA |
| Workers | One agent worker per token |
| Remap | Each worker sees only its token as `cuda:0` |
| `--num-agents` | Optional; default is the token count; when set, must equal that count |

Example with two GPUs:

```bash
export CUDA_VISIBLE_DEVICES=0,1
tune_model \
  --config /path/to/tune.json \
  --tune-space /path/to/tune_space.json \
  --opath /path/to/out \
  --num-agents 2 \
  --max-trials 20 \
  --verbosity 1
```

## W&B requirements

| Topic | Rule |
| --- | --- |
| Mode | `online` or `offline` only (`disabled` is invalid for tune) |
| Project | Required `wandb.project` |
| New sweep | When `wandb.sweep_id` is empty, `wandb.sweep_name` is required |
| Existing sweep | Non-empty `wandb.sweep_id` attaches; `sweep_name` is not required |
| Forbidden | `wandb.name`, `wandb.num_agents`, `wandb.max_trials` |

Sweep objective uses validation loss: each trial logs `val_loss` with a W&B
`min` summary. Metric names and early-stopping patience reuse the
[Metrics](../artifacts/metrics.md) and
[early stopping](../configuration/tune.md#early_stopping) contracts.

## Sweep creation and agent behavior

1. Parent validates tune config and tune-space.
2. Parent creates a sweep (`wandb.sweep`) when `sweep_id` is empty, or uses the
   provided `sweep_id`.
3. Parent spawns one worker process per device token.
4. Each worker runs `wandb.agent` against the sweep with
   `count=--max-trials`.
5. Each trial draws hparams, optionally loads `init_checkpoint` modules,
   trains with early stopping, and writes best-epoch artifacts under
   `--opath` using the trial `run_id` as stem.
6. Parent joins every worker. Exit `0` only if all workers succeed; otherwise
   non-zero. A peer failure does not kill siblings mid-flight.

Invalid hparam **draws** abort that trial only; the worker continues. A bad
tune-space **file** fails during parent setup and never starts agents.

## Per-agent trial limits

| Flag | Meaning |
| --- | --- |
| `--max-trials` | Cap passed to **each** `wandb.agent` call (default `20`) |
| Job bound (approx.) | About `max_trials × num_agents` trials across the job |

`--max-trials` is not a global shared budget documented here as a single
coordinated counter across workers. Size the job from the per-agent cap and
the agent count.

## Artifacts and reuse

Successful trials write:

```text
/path/to/out/{run_id}.{top_model_name}.pth
/path/to/out/{run_id}.{top_model_name}.hparam.json
```

plus per-module child files. Reuse:

- [Checkpoints](../artifacts/checkpoints.md)
- [Sidecars](../artifacts/sidecars.md)
- [Hyperparameters](../configuration/hyperparameters.md)
- [Model composition](../models/composition.md)
- [Splits](../data/splits.md) / [Arrays](../data/arrays.md) / [Labels](../data/labels.md)

After a promising trial, pass that trial's parent `.pth` and parent
`.hparam.json` into `pred_model` the same way as a train artifact (see
[Train to predict](train-to-predict.md)).

Optional warm-start / freeze patterns:
[Initialization and freezing](initialization-and-freezing.md).

## Related pages

- [`tune_model` CLI](../cli/tune_model.md)
- [Tune configuration](../configuration/tune.md)
- [Tuning spaces](../configuration/tuning-spaces.md)
- [Config overview](../config.md)
