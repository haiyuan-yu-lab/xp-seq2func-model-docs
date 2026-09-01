# CLI overview

Three console scripts ship with **v0.1.0a9**. Together with their configuration,
data, and artifact contracts, they are the supported public interface for this
release (Python imports are not).

| Command | Purpose |
| --- | --- |
| [`train_model`](train_model.md) | Train with fixed hyperparameters |
| [`tune_model`](tune_model.md) | Hyperparameter search via W&B sweeps |
| [`pred_model`](pred_model.md) | Run inference and write prediction arrays |

## Invocation

After [install](../install.md):

```bash
train_model --help
tune_model --help
pred_model --help
```

## Common flags

All three commands share:

| Flag | Required | Description |
| --- | --- | --- |
| `--config` | yes | Path to config JSON |
| `--opath` | yes | Output directory for artifacts |
| `--verbosity` | no | `0`, `1`, or `2` (default `1`) |

!!! tip "Flags"
    This documentation summarizes commands and config keys.
    **`--help` on the installed build is authoritative** for flags and defaults.
