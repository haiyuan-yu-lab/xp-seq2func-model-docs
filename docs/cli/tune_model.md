# tune_model

Run a Weights & Biases hyperparameter sweep for an `EncoderPredictor` in exact
release **v0.1.0a9**.

## Command snapshot

```text
usage: tune_model [-h] --config CONFIG --opath OPATH
                     [--verbosity VERBOSITY] --tune-space TUNE_SPACE
                     [--num-agents NUM_AGENTS] [--max-trials MAX_TRIALS]

Tune a seq2func model with W&B

options:
  -h, --help            show this help message and exit
  --config CONFIG       Path to config JSON
  --opath OPATH         Output directory for artifacts
  --verbosity VERBOSITY
                        Log verbosity: 0, 1, or 2 (default: 1)
  --tune-space TUNE_SPACE
                        Path to tune-space JSON
  --num-agents NUM_AGENTS
                        Number of concurrent W&B agent workers (integer >= 1).
                        Default: count of CUDA_VISIBLE_DEVICES tokens. When
                        set, must equal that count.
  --max-trials MAX_TRIALS
                        Per-agent W&B trial cap (integer >= 1). Default: 20.
                        Passed as count to each wandb.agent call.
```

CLI help snapshot for **v0.1.0a9** (committed Markdown; documentation build does
not import the package or regenerate this text).

## Flags

| Flag | Required | Default | Notes |
| --- | --- | --- | --- |
| `--config` | yes | — | Tune config JSON path |
| `--tune-space` | yes | — | Tune-space JSON path (`method` + `parameters`) |
| `--opath` | yes | — | Output directory for trial checkpoints and sidecars |
| `--verbosity` | no | `1` | Must be `0`, `1`, or `2` |
| `--num-agents` | no | token count of `CUDA_VISIBLE_DEVICES` | Integer ≥ 1; when set, must equal that token count |
| `--max-trials` | no | `20` | Integer ≥ 1; **per-agent** W&B trial cap passed as `count` to each `wandb.agent` call |

There is no `--device` flag and no `--hparams` flag. Searchable hyperparameters
come from `--tune-space`. Agent concurrency and trial caps are CLI-only (not
tune-config JSON keys).

## Required environment

| Variable | Contract |
| --- | --- |
| `CUDA_VISIBLE_DEVICES` | **Required** for `tune_model`. Comma-separated non-empty device tokens with no duplicates. |

The parent process does not initialize CUDA. It spawns one worker per token;
each worker remaps its single token so that worker sees `cuda:0`. See
[Tuning workflow](../workflows/tuning.md).

## Required inputs

| Input | Contract |
| --- | --- |
| Tune config | [Tune configuration](../configuration/tune.md) |
| Tune-space JSON | [Tuning spaces](../configuration/tuning-spaces.md) |
| Arrays named by the config | [Arrays](../data/arrays.md), [Labels](../data/labels.md), [Splits](../data/splits.md) |

## Outputs

Under `--opath`, each successful trial writes artifacts whose stem is the W&B
`run_id` for that trial:

| Artifact | Pattern |
| --- | --- |
| Parent checkpoint | `{run_id}.{top_model_name}.pth` |
| Child checkpoints | `{run_id}.{child_model_name}.pth` |
| Parent hparam sidecar | `{run_id}.{top_model_name}.hparam.json` |
| Child hparam sidecars | `{run_id}.{child_model_name}.hparam.json` |

Reuse the checkpoint envelope, sidecar shapes, and metric logging contracts
from [Checkpoints](../artifacts/checkpoints.md),
[Sidecars](../artifacts/sidecars.md), and
[Metrics](../artifacts/metrics.md). There is no metrics file under `--opath`.

## Exit outcomes

| Outcome | Exit | Notes |
| --- | --- | --- |
| All workers succeed | `0` | Parent waited for every agent process |
| Setup failure or any worker fatal failure | non-zero | Diagnostic text on stderr; parent still waits for all workers before exiting |

## Failure conditions

Failures include (described without stabilizing exact exception text):

- Missing required flags (`--config`, `--tune-space`, `--opath`)
- Verbosity outside `{0, 1, 2}`
- Unreadable or invalid tune-config or tune-space JSON
- Missing, unknown, or forbidden tune-config keys (forbidden: `optimizer`,
  `loss`, `job_name`, `num_agents`, `max_trials`)
- Invalid tune `wandb` block (`disabled` mode, missing `sweep_name` when
  `sweep_id` is empty, forbidden `name` / `num_agents` / `max_trials`)
- Bad tune-space envelope or leaf descriptors (fails at load; does not start
  agents)
- Top-level `model_type` other than `EncoderPredictor`
- Schema / composition mismatches in `model_config` or the tune-space tree
- Unset, empty, duplicate, or otherwise invalid `CUDA_VISIBLE_DEVICES`
- `--num-agents` set to a value other than the device-token count
- `--max-trials` less than 1
- Sweep create/attach failure
- Fatal worker failure during a trial (that worker exits; siblings continue
  until they finish)

**Trial-local** invalid hparam draws abort that trial only; the worker continues
to later trials. A bad tune-space **file** fails before agents start.

## Minimal example

Placeholder paths only; this documentation does not ship datasets or
checkpoints.

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

## Behavior

1. Validates the tune config and tune-space against the `EncoderPredictor`
   composition in `model_config`
2. Resolves agent count and per-agent trial cap from CLI / `CUDA_VISIBLE_DEVICES`
3. Creates a W&B sweep when `wandb.sweep_id` is empty (using `wandb.sweep_name`),
   or attaches to an existing `sweep_id`
4. Spawns one agent worker per device token without initializing CUDA in the
   parent
5. Each trial samples hparams from the sweep, builds the model (applying
   `init_checkpoint` when set), trains with early stopping on minimum
   validation loss, logs metrics (including `val_loss` with a `min` summary),
   and writes best-epoch artifacts under `--opath` using the trial `run_id`
   as stem

## Related pages

- [Tune configuration](../configuration/tune.md)
- [Tuning spaces](../configuration/tuning-spaces.md)
- [Tuning workflow](../workflows/tuning.md)
- [Config overview](../config.md)
