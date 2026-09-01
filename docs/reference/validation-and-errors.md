# Validation and errors

How **v0.1.0a9** commands respond to invalid inputs.

## Fail-closed behavior

The CLIs reject unsupported configuration keys, malformed JSON, incompatible
array shapes, and other contract violations before producing misleading
artifacts. Prefer fixing the rejected condition over relying on partial
outputs.

Exact exception text and stack traces are **not** a stability contract. Use
the condition descriptions on contract pages and `--verbosity` output for
diagnosis.

## CLI and environment

| Condition | Where documented |
| --- | --- |
| Missing required flags or invalid verbosity | [train_model](../cli/train_model.md), [tune_model](../cli/tune_model.md), [pred_model](../cli/pred_model.md) |
| No CUDA device at runtime | All three CLIs require CUDA; see [FAQ](../faq.md#do-i-need-a-gpu) |
| Empty, duplicate, or mismatched `CUDA_VISIBLE_DEVICES` for tune agents | [tune_model](../cli/tune_model.md), [Tuning workflow](../workflows/tuning.md) |
| `--num-agents` set but not equal to device-token count | [tune_model](../cli/tune_model.md) |
| `--attribution-target` without `--attribution` | [pred_model](../cli/pred_model.md) |

## Configuration JSON

| Condition | Where documented |
| --- | --- |
| Unknown or forbidden top-level keys | [Configuration overview](../config.md), command config pages |
| `model_type` other than `EncoderPredictor` | [Model composition](../models/composition.md) |
| Duplicate `model_name` values in the tree | [Model configuration](../configuration/model.md) |
| Train/tune missing required data, W&B, or early-stopping blocks | [Train config](../configuration/train.md), [Tune config](../configuration/tune.md) |
| Pred config with `wandb`, `init_checkpoint`, or `attribution*` keys | [Prediction config](../configuration/prediction.md) |
| Invalid `init_checkpoint` path or module list | [Config: init_checkpoint](../config.md#init_checkpoint-train--tune), [Initialization and freezing](../workflows/initialization-and-freezing.md) |
| Tune-space leaf forms, method, or forbidden geometry fields | [Tuning spaces](../configuration/tuning-spaces.md) |
| Loss object shape / type mismatches | [Losses](../configuration/losses.md) |
| Top-level `learning_rate` ≤ 0 or freezing every trainable module | [Hyperparameters](../configuration/hyperparameters.md), [Concepts](../concepts.md#learning-rates-and-freezing) |

## Data arrays and labels

| Condition | Where documented |
| --- | --- |
| OHE shape, channel order, or multi-source path length mismatches | [Arrays](../data/arrays.md), [Multi-source](../data/multi-source.md) |
| `source_fracs` length or positivity failures | [Splits](../data/splits.md), [Multi-source](../data/multi-source.md) |
| Classification / regression `label_npy` shape or value failures | [Labels](../data/labels.md) |
| Profile/count pair missing, mask on test, or non-boolean mask | [Profiles](../profiles.md), [Masks](../data/masks.md), [Profile masks](../workflows/profile-masks.md) |
| `L_embed` not divisible by `bin_size`, or track/bin geometry drift | [Geometry](../data/geometry.md), [ProfilePredictor](../models/profile-predictor.md) |

## Checkpoints, sidecars, and prediction

| Condition | Where documented |
| --- | --- |
| Missing modules, incompatible state keys/shapes, profile `contracts` mismatch | [Checkpoints](../artifacts/checkpoints.md) |
| Hparams sidecar / inheritance mismatches for prediction | [Sidecars](../artifacts/sidecars.md), [Hyperparameters](../configuration/hyperparameters.md) |
| Attribution target syntax, head-type, range, or profile-without-target | [Attribution](../workflows/attribution.md#invalid-combinations), [Attributions](../artifacts/attributions.md) |

## Exit outcomes

Failed validation exits non-zero. Successful runs exit zero after writing the
expected artifacts under `--opath`.

## Related pages

- [FAQ](../faq.md)
- [Compatibility](compatibility.md)
- [Schemas](schemas.md)
- [Profiles](../profiles.md)
- [Masks](../data/masks.md)
