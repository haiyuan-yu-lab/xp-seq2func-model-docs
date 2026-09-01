# Checkpoints

Checkpoint artifacts written and consumed in **v0.1.0a9**.

## Producers and consumers

| Role | Surface |
| --- | --- |
| Producer | `train_model` and `tune_model` write under `--opath` |
| Consumer | `pred_model --checkpoint` loads the **parent** `.pth` |
| Consumer | Optional `init_checkpoint` on train/tune loads selected modules from a parent or child `.pth` |

## Filenames

Let `{job}` be `job_name` (train) or the W&B trial `run_id` (tune),
`{top_model_name}` the top-level `EncoderPredictor.model_name`, and
`{child_model_name}` each nested catalogued `model_name` (encoder and heads).

| Artifact | Pattern |
| --- | --- |
| Parent checkpoint | `{job}.{top_model_name}.pth` |
| Child checkpoint | `{job}.{child_model_name}.pth` |

Training writes one file per catalogued module for the best validation-loss
epoch. Pair each `.pth` with its hparam sidecar; see [Sidecars](sidecars.md).

## Payload contract (public envelope)

Each `.pth` is a dict payload with:

| Key | Required | Notes |
| --- | --- | --- |
| `format` | yes | New writes use `seq2func_ckpt_v2`. Loaders also accept legacy `seq2func_ckpt_v1` under the compatibility rules below |
| `root_model_name` | yes | Catalogued `model_name` this file is rooted at |
| `states` | yes | Map of catalogued module name → owned parameter tensors |
| `contracts` | yes (v2) | Per-module identity metadata for every catalogued name in the saved subtree |

### v2 contracts

Every catalogued module in the saved subtree has a `contracts` entry:

| Module kind | Entry shape |
| --- | --- |
| Non-profile modules (encoder, scalar heads, top-level container) | `{"model_type": "<Type>"}` only |
| `ProfilePredictor` | `model_type`, ordered `track_names`, and `bin_size` |
| `RCProfilePredictor` | `model_type`, ordered `track_names`, `bin_size`, and `track_transform` (`preserve` or `swap_pair`) |

Loaders require an exact `model_type` match for each module in addition to
tensor key/shape checks. Profile heads also require matching track order and
bin geometry so same-shaped but semantically reordered heads fail to load.
See [Profiles](../profiles.md).

### v2 scalar counterpart init (train/tune only)

`init_checkpoint` on train/tune may load compatible scalar-head weights across
these bidirectional pairs when the checkpoint is `seq2func_ckpt_v2`:

| Ordinary | RC-aware counterpart |
| --- | --- |
| `ClassPredictor` | `RCClassPredictor` |
| `RegressPredictor` | `RCRegressPredictor` |

Requirements:

- Listed module names, tensor keys, and tensor shapes must match the constructed
  target instance.
- Architecture-defining fields implied by the target (for example `n_class` on
  class heads and pooled-FC geometry such as `n_channels` and FC depth) must be
  compatible.
- Loaded weights seed the **target** module’s forward behavior; checkpoint
  `contracts` keep the source `model_type`.

Not permitted:

- `ProfilePredictor` ↔ `RCProfilePredictor` init transfer (even when public
  shapes match).
- Counterpart transfer from legacy `seq2func_ckpt_v1` checkpoints.
- Cross-type transfer on `pred_model --checkpoint` full restore (exact
  `model_type` required throughout the tree).

### Legacy v1 compatibility

Checkpoints written by earlier software may use `seq2func_ckpt_v1`. Those
payloads record profile semantics only (`track_names`, `bin_size` on profile
heads) and omit `model_type` for other modules.

| Scenario | Policy |
| --- | --- |
| Ordinary-model target tree (no RC-aware predictor heads) | v1 checkpoints load for full restore and selective init when tensor keys/shapes and profile contracts match |
| v1 checkpoint into a target tree with an RC-aware predictor head (`RCClassPredictor`, `RCRegressPredictor`, …) | v1 checkpoints are **rejected** — use a typed v2 checkpoint |
| v2 scalar counterpart init (`ClassPredictor` ↔ `RCClassPredictor`, `RegressPredictor` ↔ `RCRegressPredictor`) | Permitted on train/tune `init_checkpoint` only; see [Scalar counterpart init](#v2-scalar-counterpart-init-traintune-only) |

`RCClassPredictor` and `RCRegressPredictor` are part of the public catalog in this release. Legacy v1
checkpoints cannot initialize trees that include RC-aware predictor heads.

Private tensor layouts inside `states` are not stabilized in this
documentation.

## Selection rules

| Consumer | Which file |
| --- | --- |
| `pred_model` | Parent `{job}.{top_model_name}.pth` |
| `init_checkpoint` | Parent or child `.pth` that contains `states` for the listed `modules` |

Shape, key, `model_type`, or profile-contract mismatches when loading listed
modules fail closed. Exact error text is not stabilized here.

## Related pages

- [`train_model`](../cli/train_model.md)
- [Sidecars](sidecars.md)
- [Config: init_checkpoint](../config.md#init_checkpoint-train--tune)
- [Initialization and freezing](../workflows/initialization-and-freezing.md)
- [Formats overview](../formats.md)
- [Train to predict](../workflows/train-to-predict.md)
