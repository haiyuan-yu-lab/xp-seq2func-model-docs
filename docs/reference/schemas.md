# Schemas

Documentation-owned JSON Schema snapshots for exact release **v0.1.0a8**.

These files live under `schemas/v0.1.0a8/` on this site. They are **not**
canonical runtime definitions. Runtime validators in the installed package
remain authoritative for filesystem properties, array contents, and other
behavior JSON Schema cannot express.

## Draft and identifiers

- JSON Schema Draft **2020-12**
- Stable `$id` values under
  `https://haiyuan-yu-lab.github.io/xp-seq2func-model-docs/schemas/v0.1.0a8/`
- Reusable shared definitions in `defs.schema.json`

## Available snapshots

| Schema | Purpose |
| --- | --- |
| [`defs.schema.json`](../schemas/v0.1.0a8/defs.schema.json) | Reusable `$defs` for paths, numbers, strings, losses, data blocks, and nested fragments |
| [`init-checkpoint.schema.json`](../schemas/v0.1.0a8/init-checkpoint.schema.json) | Optional train/tune `init_checkpoint` object |
| [`early-stopping.schema.json`](../schemas/v0.1.0a8/early-stopping.schema.json) | Train/tune `early_stopping` object |
| [`wandb-train.schema.json`](../schemas/v0.1.0a8/wandb-train.schema.json) | Train-config `wandb` block |
| [`data-source.schema.json`](../schemas/v0.1.0a8/data-source.schema.json) | Train/val split data block (`train_data` / `val_data`) |
| [`train-config.schema.json`](../schemas/v0.1.0a8/train-config.schema.json) | Complete `train_model --config` JSON |
| [`encoder-predictor-model-config.schema.json`](../schemas/v0.1.0a8/encoder-predictor-model-config.schema.json) | Top-level `EncoderPredictor` `model_config` tree |
| [`encoder-predictor-hparams.schema.json`](../schemas/v0.1.0a8/encoder-predictor-hparams.schema.json) | Top-level pre-inheritance fixed hyperparameters |
| [`scalar-head-hparams-wrapper.schema.json`](../schemas/v0.1.0a8/scalar-head-hparams-wrapper.schema.json) | `ClassPredictor` / `RegressPredictor` hparams wrapper |
| [`loss.schema.json`](../schemas/v0.1.0a8/loss.schema.json) | Loss object `{ type, params }` |

## Example association convention

Complete inline JSON examples in Markdown may declare their schema with an HTML
comment immediately before a fenced `json` block. The comment path is relative
to the MkDocs `docs/` directory, for example:

`<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->`

Docs-only checks validate those complete examples structurally. Illustrative
fragments omit the comment and are skipped.

## Example: init_checkpoint

<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->
```json
{
  "path": "/path/to/checkpoint.pth",
  "modules": ["encoder_model_name"]
}
```

See also [Config: init_checkpoint](../config.md#init_checkpoint-train--tune).

## Example: model composition

<!-- schema: schemas/v0.1.0a8/encoder-predictor-model-config.schema.json -->
```json
{
  "model_name": "ep_main",
  "embedding_trimming": 0,
  "encoder": {
    "model_type": "ConvEncoder",
    "model_config": { "model_name": "enc" }
  },
  "predictor": {
    "cls": {
      "model_type": "ClassPredictor",
      "model_config": { "model_name": "cls_head", "n_class": 2 }
    }
  }
}
```

See [Model composition](../models/composition.md) and
[Hyperparameters](../configuration/hyperparameters.md).

## Example: train config (excerpt association)

Complete train-config examples live on
[Train configuration](../configuration/train.md) and validate against
[train-config.schema.json](../schemas/v0.1.0a8/train-config.schema.json).
Split-only examples validate against
[data-source.schema.json](../schemas/v0.1.0a8/data-source.schema.json).
