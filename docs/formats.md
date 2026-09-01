# Formats

Short reference for arrays and artifacts used by the CLIs.

## One-hot sequences (`.npy`)

Encoder inputs are NumPy arrays of one-hot encoded sequences, referenced from
data config as `encoder.ohe_npy`. Full contract: [Arrays](data/arrays.md).

- Shape `(N, 4, L)` with channel order **A, C, G, T**
- Path may be a single string or a non-empty array of paths (multi-source)
- Multi-source runs require `source_fracs` with one positive weight per source
- For a single source, `source_fracs` must be exactly `[1]` (or `[1.0]`)

Row order must stay aligned with any label arrays for the same source.

## Labels (`.npy`)

Train and validation configs supply per-head label arrays under each
predictor payload (path or path array matching the OHE sources). Full
contract: [Labels](data/labels.md).

- `ClassPredictor` / `RegressPredictor`: `label_npy` — shapes `(N, n_class)`
  and `(N, 1)` respectively (rank-1 regression labels fail)
- `ProfilePredictor`: paired `profile_npy` `(N, T, P)` and `count_npy`
  `(N, T)`, plus optional boolean `mask_npy` `(N, L_embed)` on train/val

Prediction (`pred_model`) does not require labels. Profile test payloads, when
present, must include both profile and count arrays and must not include a
mask.

## Checkpoints (`.pth`)

Training and tuning write PyTorch checkpoints under `--opath` (a parent file
plus per-catalogued-module files). New writes use format constant
`seq2func_ckpt_v2`; loaders also accept legacy `seq2func_ckpt_v1` for
ordinary-model trees. Full contract: [Checkpoints](artifacts/checkpoints.md).
`pred_model` loads the **top-level / parent** checkpoint via `--checkpoint`.

Train/tune configs may set optional `init_checkpoint` to load listed modules
from a parent or submodule `.pth` before training. See
[Config](config.md#init_checkpoint-train--tune).

## Hparams JSON

Pre-inheritance hyperparameter objects used by `train_model` and
`pred_model`. After training, the parent sidecar
`{stem}.{top_level_model_name}.hparam.json` is the usual artifact to pass back
into prediction; child sidecars hold effective nested values. See
[Sidecars](artifacts/sidecars.md) and
[Hyperparameters](configuration/hyperparameters.md).

Nested encoder/head `learning_rate` values may be `0` to freeze that module;
the top-level `learning_rate` must stay strictly positive. See
[Concepts](concepts.md#learning-rates-and-freezing).

## Tune-space JSON

Envelope for `tune_model`. Full contract:
[Tuning spaces](configuration/tuning-spaces.md).

- `method`: `grid`, `random`, or `bayes`
- `parameters`: nested tree of leaf descriptors

Leaf forms:

| Keys | Meaning |
| --- | --- |
| `{"value": ...}` | Fixed value |
| `{"values": [...]}` | Discrete choices |
| `{"distribution": "uniform"\|"log_uniform", "min": ..., "max": ...}` | Continuous range (`log_uniform` requires `min > 0`) |

The same learning-rate rules apply inside `parameters`: top-level
`learning_rate` leaves must be `> 0`; nested `.learning_rate` leaves may be
`≥ 0` (including fixed `{"value": 0}`).

`init_checkpoint` is not allowed in the tune-space file (put it on the tune
config instead). Do not put `track_names` or `bin_size` in the tune-space.

## Prediction outputs

Canonical tables: [Predictions](artifacts/predictions.md). For each prediction
head, `pred_model` writes under `--opath`:

| Head type | Filename suffix | Shape | dtype |
| --- | --- | --- | --- |
| `ClassPredictor` | `.pred_class.npy` | `(N, n_class)` | float32 |
| `RegressPredictor` | `.pred.npy` | `(N, 1)` | float32 |
| `ProfilePredictor` | `.profile.npy` / `.count.npy` | `(N, T, P)` / `(N, T)` | float32 |

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred_class.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.profile.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.count.npy
```

When `--attribution` is set (`ig`, `saliency`, or `deepshap`) **without**
`--attribution-target`, it also writes per-head float32 arrays shaped
`(N, 4, L)` (legacy predicted-class / regress targets):

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.npy
```

With `--attribution-target`, it writes one target-qualified float32 array
`(N, 4, L)` for the selected `ClassPredictor` or `ProfilePredictor` head:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.probability_{k}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.logit_{k}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.logit-difference_{p}_{n}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.logit_predicted.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.profile-probability_{track}_{bin}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.profile-logit_{track}_{bin}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.count_{track}.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.log1p-count_{track}.npy
```

Predictor map keys must not contain `:`. Prediction `.pred_class.npy` /
`.pred.npy` / `.profile.npy` / `.count.npy` files are unchanged by attribution
targeting.
