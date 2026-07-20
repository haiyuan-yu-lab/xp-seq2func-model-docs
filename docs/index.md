# xp-seq2func-model

Train, tune, and run predictions for sequence-to-function models.

This site documents release **0.1.0a2**.

## What ships in 0.1.0a2

| Component | Kind | Role |
| --- | --- | --- |
| `train_model` | CLI | Train with fixed hyperparameters |
| `tune_model` | CLI | Hyperparameter search via Weights & Biases sweeps |
| `pred_model` | CLI | Run inference and write prediction arrays |
| `EncoderPredictor` | Model | Top-level model: `ConvEncoder` + one or more `ClassPredictor` heads |

!!! warning "Alpha release"
    **0.1.0a2** is a pre-release. Config schemas and CLI flags may change. Pin
    the tag if you need a fixed cut.

## Where to start

1. [Install](install.md) from the `v0.1.0a2` code tag
2. Skim [Concepts](concepts.md) and [Formats](formats.md)
3. Check [Config](config.md) keys for train / tune / pred JSON
4. Use the [CLI overview](cli/index.md), then the command pages

Code repository: [haiyuan-yu-lab/xp-seq2func-model](https://github.com/haiyuan-yu-lab/xp-seq2func-model)
(tag `v0.1.0a2`).
