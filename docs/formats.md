# Formats

Short reference for arrays and artifacts used by the CLIs.

## One-hot sequences (`.npy`)

Encoder inputs are NumPy arrays of one-hot encoded sequences, referenced from
data config as `encoder.ohe_npy`.

- Path may be a single string or a non-empty array of paths (multi-source)
- Multi-source runs require `source_fracs` with one positive weight per source
- For a single source, `source_fracs` must be exactly `[1]` (or `[1.0]`)

Row order must stay aligned with any label arrays for the same source.

## Labels (`.npy`)

Train and validation configs supply per-head label arrays under
`predictor.<head>.label` (path or path array matching the OHE sources).

- `ClassPredictor`: class label layout expected by that head
- `RegressPredictor`: arrays with trailing width 1 (`(N, 1)`)

Prediction (`pred_model`) does not require labels.

## Checkpoints (`.pth`)

Training and tuning write PyTorch checkpoints under `--opath` (a parent file
plus per-catalogued-module files such as `{stem}.{encoder_model_name}.pth`).
`pred_model` loads the **top-level / parent** checkpoint via `--checkpoint`.

Train/tune configs may set optional `init_checkpoint` to load listed modules
from a parent or submodule `.pth` before training. See
[Config](config.md#init_checkpoint-train--tune).

## Hparams JSON

Pre-inheritance hyperparameter objects used by `train_model` and
`pred_model`. After training, a sidecar
`{stem}.{top_level_model_name}.hparam.json` is the usual artifact to pass back
into prediction.

Nested encoder/head `learning_rate` values may be `0` to freeze that module;
the top-level `learning_rate` must stay strictly positive. See
[Concepts](concepts.md#learning-rates-and-freezing).

## Tune-space JSON

Envelope for `tune_model`:

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
config instead).

## Prediction outputs

For each predictor head, `pred_model` writes under `--opath`:

| Head type | Filename suffix |
| --- | --- |
| `ClassPredictor` | `.pred_class.npy` |
| `RegressPredictor` | `.pred.npy` |

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred_class.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred.npy
```

When `--attribution` is set (`ig`, `saliency`, or `deepshap`), it also writes
per-head float32 arrays shaped `(N, 4, L)`:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{method}.npy
```
