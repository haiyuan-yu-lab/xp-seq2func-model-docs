# xp-seq2func-model

Train, tune, and run predictions for sequence-to-function models.

This site documents exact release **v0.1.0a8**.

## Supported public interface

For **v0.1.0a8**, the supported public interface is:

- the three console commands `train_model`, `tune_model`, and `pred_model`
- the JSON configuration contracts those commands accept
- the input data and output artifact contracts they read and write

Python imports from the installed package are **not** a supported API in this
release. Prefer the CLIs and file contracts documented on this site.

## What ships in v0.1.0a8

| Component | Kind | Role |
| --- | --- | --- |
| `train_model` | CLI | Train with fixed hyperparameters |
| `tune_model` | CLI | Hyperparameter search via Weights & Biases sweeps |
| `pred_model` | CLI | Run inference and write prediction arrays (optional Captum attribution) |
| `EncoderPredictor` | Model composition | Top-level CLI model: encoder plus one or more prediction heads |
| `init_checkpoint` | Config | Optional train/tune key to load selected module weights before training |

!!! note "Attribution targets"
    `pred_model` accepts optional `--attribution-target` for fixed
    class-head scalars (`probability` / `logit` / `logit-difference` /
    `logit:predicted`) and profile-head scalars
    (`profile-probability` / `profile-logit` / `count` / `log1p-count`).
    Omitting it keeps legacy all-head filenames and prints a deprecation
    notice, and is rejected when the model contains a profile head. Prediction
    head map keys must not contain `:`. See [pred_model](cli/pred_model.md) and
    [Profile reconstruction](profiles.md).

!!! warning "Alpha release"
    **v0.1.0a8** is a pre-release. Config schemas and CLI flags may change.
    Documentation accuracy is promised for this exact tag only. See
    [Compatibility](reference/compatibility.md).

## Where to start

1. [Install](install.md) from the `v0.1.0a8` code tag (requires repository access)
2. Skim [Core concepts](concepts.md) and the [Quickstart](getting-started/quickstart.md)
3. Review [CLI Reference](cli/index.md) and [Configuration](config.md)
4. Browse [Data Contracts](data/arrays.md) and [Artifacts](artifacts/checkpoints.md) as needed

## LLM resources

- [`llms.txt`](llms.txt) — curated map of key pages with one-line descriptions
- [`llms-full.txt`](llms-full.txt) — navigation-ordered concatenation of
  canonical Markdown sources

Code repository: [haiyuan-yu-lab/xp-seq2func-model](https://github.com/haiyuan-yu-lab/xp-seq2func-model)
(tag `v0.1.0a8`).
