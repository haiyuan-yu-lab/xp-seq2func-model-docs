# Train to predict

End-to-end path from training artifacts to prediction outputs for **v0.1.0a8**.
Placeholder paths only; this documentation does not ship datasets or
checkpoints.

## 1. Install and prepare CUDA

1. Install from tag `v0.1.0a8` ([Install](../install.md)).
2. Confirm a CUDA device is visible to the process (`CUDA_VISIBLE_DEVICES` is
   optional environment, not a CLI flag).

## 2. Train

Author a [train config](../configuration/train.md) and
[hparams](../configuration/hyperparameters.md) JSON, then run
[`train_model`](../cli/train_model.md):

```bash
train_model \
  --config /path/to/train.json \
  --hparams /path/to/hparams.json \
  --opath /path/to/out \
  --verbosity 1
```

## 3. Collect parent artifacts

Under `/path/to/out`, take the **parent** checkpoint and **parent** hparam
sidecar (not child module files):

```text
/path/to/out/{job_name}.{top_model_name}.pth
/path/to/out/{job_name}.{top_model_name}.hparam.json
```

Example when `job_name` is `demo_train` and `model_name` is `ep_main`:

```text
/path/to/out/demo_train.ep_main.pth
/path/to/out/demo_train.ep_main.hparam.json
```

See [Checkpoints](../artifacts/checkpoints.md) and
[Sidecars](../artifacts/sidecars.md).

## 4. Author a prediction config

Write a prediction config with the same `model_config` composition as
training, a `test_data` block pointing at test one-hot arrays, and a
`job_name` / `random_seed`. Labels are optional.

Canonical contract: [Prediction configuration](../configuration/prediction.md).

Minimal unlabeled shape:

```json
{
  "model_type": "EncoderPredictor",
  "model_config": { "...": "same composition as train" },
  "test_data": {
    "encoder": {
      "ohe_npy": "/path/to/test_ohe.npy",
      "label": null
    },
    "shuffle": false,
    "num_workers": 0,
    "pin_memory": true,
    "source_fracs": [1]
  },
  "job_name": "demo_pred",
  "random_seed": 0
}
```

## 5. Run prediction

```bash
pred_model \
  --config /path/to/pred.json \
  --hparams /path/to/out/demo_train.ep_main.hparam.json \
  --checkpoint /path/to/out/demo_train.ep_main.pth \
  --opath /path/to/pred_out \
  --verbosity 1
```

Optional Captum attribution uses `--attribution` and, when needed,
`--attribution-target`. See [`pred_model`](../cli/pred_model.md) and
[Attribution](attribution.md).

## 6. Read outputs

Under `/path/to/pred_out`, successful runs write one artifact set per head:

```text
/path/to/pred_out/demo_pred.ep_main.cls_head.pred_class.npy
/path/to/pred_out/demo_pred.ep_main.reg_head.pred.npy
```

| Head | Suffix | Shape |
| --- | --- | --- |
| `ClassPredictor` | `.pred_class.npy` | `(N, n_class)` float32 probabilities |
| `RegressPredictor` | `.pred.npy` | `(N, 1)` float32 |
| `ProfilePredictor` | `.profile.npy` / `.count.npy` | `(N, T, P)` / `(N, T)` float32 |

Full tables: [Predictions](../artifacts/predictions.md). Exit `0` on success;
non-zero on failure.

## Related pages

- [`train_model`](../cli/train_model.md)
- [`pred_model`](../cli/pred_model.md)
- [Prediction configuration](../configuration/prediction.md)
- [Getting started quickstart](../getting-started/quickstart.md)
