# Checkpoints

Checkpoint artifacts written and consumed in **v0.1.0a8**.

## Producers and consumers

| Role | Surface |
| --- | --- |
| Producer | `train_model` and `tune_model` write under `--opath` |
| Consumer | `pred_model --checkpoint` loads the **parent** `.pth` |
| Consumer | Optional `init_checkpoint` on train/tune loads selected modules from a parent or child `.pth` |

## Filenames

Let `{job}` be `job_name` (train) or the trial stem (tune),
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
| `format` | yes | Constant `seq2func_ckpt_v1` |
| `root_model_name` | yes | Catalogued `model_name` this file is rooted at |
| `states` | yes | Map of catalogued module name → owned parameter tensors |
| `contracts` | optional | Present when the saved subtree includes a `ProfilePredictor`; omitted otherwise |

Private tensor layouts inside `states` are not stabilized in this
documentation. Profile `contracts` entries, when present, identify profile
heads for consumers; exact profile contract fields are documented with
[Profiles](../profiles.md).

## Selection rules

| Consumer | Which file |
| --- | --- |
| `pred_model` | Parent `{job}.{top_model_name}.pth` |
| `init_checkpoint` | Parent or child `.pth` that contains `states` for the listed `modules` |

Shape or key mismatches when loading listed modules fail closed. Exact error
text is not stabilized here.

## Related pages

- [`train_model`](../cli/train_model.md)
- [Sidecars](sidecars.md)
- [Config: init_checkpoint](../config.md#init_checkpoint-train--tune)
- [Formats overview](../formats.md)
- [Train to predict](../workflows/train-to-predict.md)
