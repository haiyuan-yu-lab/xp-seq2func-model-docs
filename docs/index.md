# xp-seq2func-model

Train, tune, and run predictions for sequence-to-function models.

This site documents release **0.1.0a7**.

## What ships in 0.1.0a7

| Component | Kind | Role |
| --- | --- | --- |
| `train_model` | CLI | Train with fixed hyperparameters |
| `tune_model` | CLI | Hyperparameter search via Weights & Biases sweeps |
| `pred_model` | CLI | Run inference and write prediction arrays (optional Captum attribution) |
| `EncoderPredictor` | Model | Top-level model: encoder (`ConvEncoder` or `ConvSelfAttEncoder`) + one or more `ClassPredictor` / `RegressPredictor` heads |
| `init_checkpoint` | Config | Optional train/tune key to load selected module weights before training |

!!! note "Attribution targets"
    `pred_model` accepts optional `--attribution-target` for fixed
    `ClassPredictor` scalars (`probability` / `logit` / `logit-difference` /
    `logit:predicted`). Omitting it keeps legacy all-head filenames and prints
    a deprecation notice. Predictor map keys must not contain `:`. See
    [pred_model](cli/pred_model.md).

!!! warning "Alpha release"
    **0.1.0a7** is a pre-release. Config schemas and CLI flags may change. Pin
    the tag if you need a fixed cut.

## Where to start

1. [Install](install.md) from the `v0.1.0a7` code tag
2. Skim [Concepts](concepts.md) and [Formats](formats.md)
3. Check [Config](config.md) keys for train / tune / pred JSON
4. Use the [CLI overview](cli/index.md), then the command pages

Code repository: [haiyuan-yu-lab/xp-seq2func-model](https://github.com/haiyuan-yu-lab/xp-seq2func-model)
(tag `v0.1.0a7`).
