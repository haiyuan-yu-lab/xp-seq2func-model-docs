# Tuning workflow

Hyperparameter search with `tune_model` for **v0.1.0a8**.

- Requires Weights & Biases sweeps (`wandb.mode` online or offline)
- Agents are constrained by `CUDA_VISIBLE_DEVICES`
- Optional `init_checkpoint` applies at the start of each trial

Coming in a later documentation slice: sweep creation, per-agent trial limits,
and GPU assignment detail. See [tune_model](../cli/tune_model.md) and
[Config](../config.md).
