# train_model

Train an `EncoderPredictor` with fixed hyperparameters for exact release
**v0.1.0a8**.

## Command snapshot

```text
usage: train_model [-h] --config CONFIG --opath OPATH [--verbosity VERBOSITY]
                   --hparams HPARAMS

Train a seq2func model

options:
  -h, --help            show this help message and exit
  --config CONFIG       Path to config JSON
  --opath OPATH         Output directory for artifacts
  --verbosity VERBOSITY
                        Log verbosity: 0, 1, or 2 (default: 1)
  --hparams HPARAMS     Path to top-level pre-inheritance hparams JSON
```

CLI help snapshot for **v0.1.0a8** (committed Markdown; documentation build does
not import the package or regenerate this text).

## Flags

| Flag | Required | Default | Notes |
| --- | --- | --- | --- |
| `--config` | yes | — | Train config JSON path |
| `--hparams` | yes | — | Top-level pre-inheritance hparams JSON path |
| `--opath` | yes | — | Output directory for checkpoints and sidecars |
| `--verbosity` | no | `1` | Must be `0`, `1`, or `2` |

There is no `--device` flag. Training requires CUDA. `CUDA_VISIBLE_DEVICES` is
optional process environment and is not a CLI flag.

## Required inputs

| Input | Contract |
| --- | --- |
| Train config | [Train configuration](../configuration/train.md) |
| Hparams JSON | [Hyperparameters](../configuration/hyperparameters.md) |
| Arrays named by the config | [Arrays](../data/arrays.md), [Labels](../data/labels.md), [Masks](../data/masks.md), [Splits](../data/splits.md) |

## Outputs

Under `--opath`, successful runs write:

| Artifact | Pattern |
| --- | --- |
| Parent checkpoint | `{job_name}.{top_model_name}.pth` |
| Child checkpoints | `{job_name}.{child_model_name}.pth` |
| Parent hparam sidecar | `{job_name}.{top_model_name}.hparam.json` |
| Child hparam sidecars | `{job_name}.{child_model_name}.hparam.json` |

`job_name` is both the artifact stem and the Weights & Biases run name when
logging is enabled. Metrics go to the console and optionally to W&B; there is
no metrics file under `--opath`. See
[Checkpoints](../artifacts/checkpoints.md),
[Sidecars](../artifacts/sidecars.md), and
[Metrics](../artifacts/metrics.md).

## Exit outcomes

| Outcome | Exit | Notes |
| --- | --- | --- |
| Success | `0` | Artifacts written under `--opath` |
| Failure | non-zero | Diagnostic text on stderr |

## Failure conditions

Failures include (described without stabilizing exact exception text):

- Missing required flags (`--config`, `--hparams`, `--opath`)
- Verbosity outside `{0, 1, 2}`
- Unreadable or invalid JSON for config or hparams
- Missing, unknown, or forbidden train-config keys (forbidden: `optimizer`,
  `loss`)
- Top-level `model_type` other than `EncoderPredictor`
- Schema / composition mismatches in `model_config` or hparams
- No CUDA device available to the process
- Invalid `init_checkpoint` path, modules, or state mismatch
- Data shape, dtype, or alignment failures
- Profile label/mask geometry failures (`profile_npy` / `count_npy` / optional `mask_npy`)
- Empty path lists
- Invalid `source_fracs`
- Every trainable module frozen
- Training produces no best checkpoint state

## Minimal example

Placeholder paths only; this documentation does not ship datasets or
checkpoints.

```bash
train_model \
  --config /path/to/train.json \
  --hparams /path/to/hparams.json \
  --opath /path/to/out \
  --verbosity 1
```

## Behavior

1. Validates the train config and hparams against the `EncoderPredictor`
   composition in `model_config`
2. Requires CUDA
3. Builds the model; if `init_checkpoint` is set, loads the listed modules from
   that `.pth` before training
4. Builds train and validation dataloaders from `train_data` / `val_data`
5. Optionally initializes W&B from `wandb` (skipped when `mode` is `disabled`)
6. Trains with early stopping on minimum validation loss (`grace_epochs`)
7. Writes best-epoch checkpoints and hparam sidecars under `--opath`

## Related pages

- [Train configuration](../configuration/train.md)
- [Hyperparameters](../configuration/hyperparameters.md)
- [Profiles](../profiles.md)
- [Train to predict](../workflows/train-to-predict.md)
- [Config overview](../config.md)
