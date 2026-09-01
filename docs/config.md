# Config

CLI configs are JSON objects. Required keys differ by command. Unknown keys and
forbidden keys are rejected.

## Shared fields

| Key | Type | Notes |
| --- | --- | --- |
| `model_type` | string | Must be `EncoderPredictor` |
| `model_config` | object | Composition tree (see below) |
| `random_seed` | integer | Seeds process RNGs |

### `model_config` (EncoderPredictor)

Required keys:

| Key | Type | Notes |
| --- | --- | --- |
| `model_name` | string | Unique across the composition tree |
| `encoder` | object | `{ "model_type": "ConvEncoder"\|"ConvSelfAttEncoder", "model_config": {...} }` |
| `predictor` | object | Map of head name → `{ "model_type": "ClassPredictor"\|"RegressPredictor"\|"ProfilePredictor", "model_config": {...} }` |
| `embedding_trimming` | integer ≥ 0 | Trim applied to encoder embedding |

All `model_name` values in the tree must be unique. `ProfilePredictor`
`model_config` also requires ordered `track_names` and `bin_size` (≥ 1). See
[Profiles](profiles.md). Full nesting tables and validated examples:
[Model composition](models/composition.md).

Head loss objects live in hparams (not the CLI config). Canonical loss
contract: [Losses](configuration/losses.md).

## Train config (`train_model --config`)

Canonical field tables, complete examples, and schema snapshots:
[Train configuration](configuration/train.md).

Required: `model_type`, `model_config`, `train_data`, `val_data`, `job_name`,
`random_seed`, `max_epochs`, `early_stopping`, `wandb`.

Forbidden at top level: `optimizer`, `loss`.

| Key | Notes |
| --- | --- |
| `job_name` | Non-empty string; artifact stem and W&B run name |
| `max_epochs` | Integer ≥ 1 |
| `early_stopping` | `{ "grace_epochs": <int ≥ 1> }` |
| `wandb` | Requires `project` and `mode` (`online` \| `offline` \| `disabled`). Optional: `entity`, `tags`, `notes`. Do not set `name`, `sweep_id`, or `sweep_name`. |
| `init_checkpoint` | Optional. Load selected module weights before training (see below). |

## Tune config (`tune_model --config`)

Canonical field tables, complete examples, and schema snapshots:
[Tune configuration](configuration/tune.md). Search-space envelope:
[Tuning spaces](configuration/tuning-spaces.md).

Required: `model_type`, `model_config`, `train_data`, `val_data`,
`random_seed`, `max_epochs`, `early_stopping`, `wandb`.

Forbidden at top level: `optimizer`, `loss`, `job_name`, `num_agents`,
`max_trials` (pass agent/trial caps on the CLI).

| Key | Notes |
| --- | --- |
| `wandb` | Requires `project` and `mode` (`online` \| `offline` only). Optional: `entity`, `tags`, `notes`, `sweep_id`, `sweep_name`. If `sweep_id` is empty, `sweep_name` is required. |
| `init_checkpoint` | Optional. Same shape as train; applied at the start of each trial. |

<a id="init_checkpoint-train--tune"></a>
### init_checkpoint (train and tune)

Optional object on the train or tune config (not in hparams or tune-space).
The object value matches the documentation schema snapshot below:

<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->
```json
{
  "path": "/path/to/checkpoint.pth",
  "modules": ["encoder_model_name"]
}
```

Place that object under the `init_checkpoint` key of the train or tune config.
Documentation schema:
[init-checkpoint.schema.json](schemas/v0.1.0a8/init-checkpoint.schema.json).

| Key | Type | Notes |
| --- | --- | --- |
| `path` | non-empty string | Path to a `seq2func_ckpt_v1` `.pth` (parent or submodule artifact) |
| `modules` | non-empty string array | Catalogued `model_name` values to load; no duplicates |

Each entry in `modules` must match a `model_name` in the constructed tree
(top-level, encoder, or a prediction head)—not predictor map keys. The
checkpoint must contain `states` for those names; other modules keep random
init. Shape / key mismatches fail with a clear error. Combine with nested
`learning_rate: 0` to freeze loaded modules. Workflow examples and the
selective-init vs full-restore distinction:
[Initialization and freezing](workflows/initialization-and-freezing.md).

## Test / pred config (`pred_model --config`)

Canonical field tables, complete examples, and schema snapshots:
[Prediction configuration](configuration/prediction.md).

Required: `model_type`, `model_config`, `test_data`, `job_name`,
`random_seed`.

Forbidden at top level: `wandb`, `loss`, `optimizer`, `max_epochs`,
`early_stopping`, `init_checkpoint`, and keys matching `attribution*`
(attribution is CLI-only).

## Data blocks (`train_data` / `val_data` / `test_data`)

Canonical train/val split tables: [Splits](data/splits.md). Test / prediction
split tables: [Prediction configuration](configuration/prediction.md). Array
and label geometry: [Arrays](data/arrays.md), [Labels](data/labels.md).

Common required keys: `encoder`, `shuffle`, `num_workers`, `pin_memory`,
`source_fracs`. Train/val also require `predictor`.

| Key | Notes |
| --- | --- |
| `encoder.ohe_npy` | Path string or non-empty path array; arrays shaped `(N, 4, L)` with channels A, C, G, T |
| `encoder.label` | Must be `null` |
| `predictor` | Map of head → typed label payload (required for train/val; optional for unlabeled pred) |
| `source_fracs` | Positive weights; length equals number of OHE sources; single-source must be `[1]` |
| `persistent_workers` | Optional bool or null |
| `prefetch_factor` | Optional int ≥ 1 or null |

`batch_size` belongs in hparams, not in the data block.

Predictor payload fields by head type:

| Head type | Train/val payload | Test notes |
| --- | --- | --- |
| `ClassPredictor` / `RegressPredictor` | `{ "label_npy": <path or path array> }` | Optional; omit for unlabeled inference |
| `ProfilePredictor` | `{ "profile_npy": ..., "count_npy": ..., "mask_npy"?: ... }` | Both profile and count required together when supplied; `mask_npy` forbidden |

Train/val require labels for every head declared in `model_config.predictor`.
Prediction may omit labels. Classification labels are `(N, n_class)`;
regression labels are `(N, 1)` (rank-1 fails). Profile payload details:
[Profiles](profiles.md).
