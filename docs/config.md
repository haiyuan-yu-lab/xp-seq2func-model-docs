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
| `predictor` | object | Map of head name → `{ "model_type": "ClassPredictor", "model_config": {...} }` |
| `embedding_trimming` | integer ≥ 0 | Trim applied to encoder embedding |

All `model_name` values in the tree must be unique.

## Train config (`train_model --config`)

Required: `model_type`, `model_config`, `train_data`, `val_data`, `job_name`,
`random_seed`, `max_epochs`, `early_stopping`, `wandb`.

Forbidden at top level: `optimizer`, `loss`.

| Key | Notes |
| --- | --- |
| `job_name` | Non-empty string; also used as the W&B run name |
| `max_epochs` | Integer ≥ 1 |
| `early_stopping` | `{ "grace_epochs": <int ≥ 1> }` |
| `wandb` | Requires `project` and `mode` (`online` \| `offline` \| `disabled`). Optional: `entity`, `tags`, `notes`. Do not set `name`, `sweep_id`, or `sweep_name`. |

## Tune config (`tune_model --config`)

Required: `model_type`, `model_config`, `train_data`, `val_data`,
`random_seed`, `max_epochs`, `early_stopping`, `wandb`.

Forbidden at top level: `optimizer`, `loss`, `job_name`, `num_agents`,
`max_trials` (pass agent/trial caps on the CLI).

| Key | Notes |
| --- | --- |
| `wandb` | Requires `project` and `mode` (`online` \| `offline` only). Optional: `entity`, `tags`, `notes`, `sweep_id`, `sweep_name`. If `sweep_id` is empty, `sweep_name` is required. |

## Test / pred config (`pred_model --config`)

Required: `model_type`, `model_config`, `test_data`, `job_name`,
`random_seed`.

Forbidden: `wandb`, `loss`, `optimizer`, `max_epochs`, `early_stopping`.

## Data blocks (`train_data` / `val_data` / `test_data`)

Common required keys: `encoder`, `shuffle`, `num_workers`, `pin_memory`,
`source_fracs`.

| Key | Notes |
| --- | --- |
| `encoder.ohe_npy` | Path string or non-empty path array |
| `encoder.label` | Must be `null` |
| `predictor` | Map of head → `{ "label": <path or path array> }` (required for train/val; omitted for unlabeled pred) |
| `source_fracs` | Positive weights; length equals number of OHE sources; single-source must be `[1]` |
| `persistent_workers` | Optional bool or null |
| `prefetch_factor` | Optional int ≥ 1 or null |

Train/val require labels for every head declared in `model_config.predictor`.
