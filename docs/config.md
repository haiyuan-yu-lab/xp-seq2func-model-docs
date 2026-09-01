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
[Profiles](profiles.md).

Head loss objects live in hparams (not the CLI config). Supported loss types:

| `type` | Typical head | `params` |
| --- | --- | --- |
| `categorical_cross_entropy` | `ClassPredictor` | must be `{}` |
| `mse` | `RegressPredictor` | must be `{}` |
| `profile_cross_entropy` | `ProfilePredictor` profile component | must be `{}` |
| `log1p_mse` | `ProfilePredictor` count component | must be `{}` |

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
| `init_checkpoint` | Optional. Load selected module weights before training (see below). |

## Tune config (`tune_model --config`)

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
(top-level, encoder, or a prediction head). The checkpoint must contain
`states` for those names; other modules keep random init. Shape / key
mismatches fail with a clear error. Combine with nested `learning_rate: 0` to
freeze loaded modules.

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
`RegressPredictor` labels must have trailing width 1 (shape `(N, 1)` per
source array).
