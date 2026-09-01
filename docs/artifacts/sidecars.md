# Hyperparameter sidecars

Hyperparameter sidecar JSON written alongside checkpoints in **v0.1.0a9**.

## Producers and consumers

| Role | Surface |
| --- | --- |
| Producer | `train_model` / `tune_model` write one `.hparam.json` per catalogued module under `--opath` |
| Consumer | `pred_model --hparams` loads the **top-level** pre-inheritance sidecar |

## Filenames

| Artifact | Pattern | Contents |
| --- | --- | --- |
| Parent sidecar | `{job}.{top_model_name}.hparam.json` | Top-level **pre-inheritance** hparams tree |
| Child sidecar | `{job}.{child_model_name}.hparam.json` | That child's **effective** (post-inheritance) hparams |

`{job}` matches the checkpoint stem. Pass the parent sidecar back into
prediction:

```bash
pred_model \
  --config /path/to/pred.json \
  --hparams /path/to/out/demo_train.ep_main.hparam.json \
  --checkpoint /path/to/out/demo_train.ep_main.pth \
  --opath /path/to/pred_out \
  --verbosity 1
```

## Contract boundaries

| Topic | Public rule |
| --- | --- |
| Parent file | Same shape as the fixed-hparams JSON accepted by `train_model --hparams` |
| Child files | Effective nested values after inheritance fill; useful for inspection |
| Unknown keys | Fail closed when reloaded as top-level hparams |
| Private details | Exact serialization of omitted inherited keys on nested slots is an implementation detail |

Canonical field tables: [Hyperparameters](../configuration/hyperparameters.md).

## Related pages

- [Checkpoints](checkpoints.md)
- [Hyperparameters](../configuration/hyperparameters.md)
- [`pred_model`](../cli/pred_model.md)
- [Formats overview](../formats.md)
