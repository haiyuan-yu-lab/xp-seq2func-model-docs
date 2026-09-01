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
| [`wandb-tune.schema.json`](../schemas/v0.1.0a8/wandb-tune.schema.json) | Tune-config `wandb` block |
| [`data-source.schema.json`](../schemas/v0.1.0a8/data-source.schema.json) | Train/val split data block (`train_data` / `val_data`) |
| [`test-data.schema.json`](../schemas/v0.1.0a8/test-data.schema.json) | Prediction `test_data` block (labels optional; no `mask_npy`) |
| [`train-config.schema.json`](../schemas/v0.1.0a8/train-config.schema.json) | Complete `train_model --config` JSON |
| [`tune-config.schema.json`](../schemas/v0.1.0a8/tune-config.schema.json) | Complete `tune_model --config` JSON |
| [`tune-space.schema.json`](../schemas/v0.1.0a8/tune-space.schema.json) | Complete `tune_model --tune-space` JSON |
| [`pred-config.schema.json`](../schemas/v0.1.0a8/pred-config.schema.json) | Complete `pred_model --config` JSON |
| [`attribution-target-string.schema.json`](../schemas/v0.1.0a8/attribution-target-string.schema.json) | Structural patterns for `pred_model --attribution-target` strings |
| [`encoder-predictor-model-config.schema.json`](../schemas/v0.1.0a8/encoder-predictor-model-config.schema.json) | Top-level `EncoderPredictor` `model_config` tree |
| [`encoder-predictor-hparams.schema.json`](../schemas/v0.1.0a8/encoder-predictor-hparams.schema.json) | Top-level pre-inheritance fixed hyperparameters |
| [`scalar-head-hparams-wrapper.schema.json`](../schemas/v0.1.0a8/scalar-head-hparams-wrapper.schema.json) | `ClassPredictor` / `RegressPredictor` hparams wrapper |
| [`profile-predictor-model-config.schema.json`](../schemas/v0.1.0a8/profile-predictor-model-config.schema.json) | Nestable `ProfilePredictor` `model_config` |
| [`profile-head-hparams-wrapper.schema.json`](../schemas/v0.1.0a8/profile-head-hparams-wrapper.schema.json) | `ProfilePredictor` hparams wrapper |
| [`profile-label-payload.schema.json`](../schemas/v0.1.0a8/profile-label-payload.schema.json) | Train/val profile payload (`profile_npy` / `count_npy` / optional `mask_npy`) |
| [`profile-test-label-payload.schema.json`](../schemas/v0.1.0a8/profile-test-label-payload.schema.json) | Test profile payload (no `mask_npy`) |
| [`loss.schema.json`](../schemas/v0.1.0a8/loss.schema.json) | Loss object `{ type, params }` |

## Example association convention

Complete inline JSON examples in Markdown may declare their schema with an HTML
comment immediately before a fenced `json` block. The comment path is relative
to the MkDocs `docs/` directory, for example:

`<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->`

Docs-only checks validate those complete examples structurally. Illustrative
fragments omit the comment and are skipped.


## Example: profile configuration fragments

<!-- schema: schemas/v0.1.0a8/profile-predictor-model-config.schema.json -->
```json
{
  "model_name": "atac_profile",
  "track_names": ["short", "mono", "di"],
  "bin_size": 10
}
```

<!-- schema: schemas/v0.1.0a8/profile-head-hparams-wrapper.schema.json -->
```json
{
  "profile_alpha": 1.0,
  "profile_loss": { "type": "profile_cross_entropy", "params": {} },
  "count_alpha": 1.0,
  "count_loss": { "type": "log1p_mse", "params": {} },
  "predictor_config": {
    "n_fc_layers": 1,
    "fc_hidden_dims": [],
    "dropout": 0.0,
    "activation": "relu",
    "pooling_methods": "GAP"
  }
}
```

<!-- schema: schemas/v0.1.0a8/profile-label-payload.schema.json -->
```json
{
  "profile_npy": "/path/to/train_profile.npy",
  "count_npy": "/path/to/train_count.npy",
  "mask_npy": "/path/to/train_mask.npy"
}
```

See [ProfilePredictor](../models/profile-predictor.md),
[Profiles](../profiles.md), and [Masks](../data/masks.md).

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

## Example: multi-source data nesting

Single-source and multi-source nesting, `source_fracs`, and parallel path lists
are documented on [Multi-source](../data/multi-source.md). Complete train,
tune, and prediction examples live on
[Multi-source data workflow](../workflows/multi-source-data.md). Those
examples validate against `data-source.schema.json`, `test-data.schema.json`,
`train-config.schema.json`, `tune-config.schema.json`, and
`pred-config.schema.json` as associated.

Reusable nested definitions (`pathOrPathArray`, `sourceFracs`,
`encoderDataBlock`, `splitDataBlock`, `testDataBlock`, scalar and profile label
payloads) live in
[defs.schema.json](../schemas/v0.1.0a8/defs.schema.json).

## Example: prediction config (excerpt association)

Complete prediction-config examples live on
[Prediction configuration](../configuration/prediction.md) and validate against
[pred-config.schema.json](../schemas/v0.1.0a8/pred-config.schema.json).
Test-data-only examples validate against
[test-data.schema.json](../schemas/v0.1.0a8/test-data.schema.json).

## Example: attribution-target strings

Structural string examples live on
[Attribution workflow](../workflows/attribution.md) and validate against
[attribution-target-string.schema.json](../schemas/v0.1.0a8/attribution-target-string.schema.json).
Artifact filename contracts:
[Attributions](../artifacts/attributions.md). Runtime remains authoritative for
class ranges, track membership, bin counts, and head-type checks.

<!-- schema: schemas/v0.1.0a8/attribution-target-string.schema.json -->
```json
"cls:probability:1"
```

<!-- schema: schemas/v0.1.0a8/attribution-target-string.schema.json -->
```json
"prof:profile-logit:short,0"
```

## Example: tune config and tune-space

Complete tune-config and tune-space examples live on
[Tune configuration](../configuration/tune.md) and
[Tuning spaces](../configuration/tuning-spaces.md). They validate against
[tune-config.schema.json](../schemas/v0.1.0a8/tune-config.schema.json) and
[tune-space.schema.json](../schemas/v0.1.0a8/tune-space.schema.json).
Tune `wandb` fragments use
[wandb-tune.schema.json](../schemas/v0.1.0a8/wandb-tune.schema.json).
