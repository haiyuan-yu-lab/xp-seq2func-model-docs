# Train to predict

End-to-end path from training artifacts to prediction outputs for **v0.1.0a8**.

1. Install from tag `v0.1.0a8` ([Install](../install.md)).
2. Author a [train config](../configuration/train.md) and
   [hparams](../configuration/hyperparameters.md) JSON (placeholder paths only in
   these docs).
3. Run [`train_model`](../cli/train_model.md):

```bash
train_model \
  --config /path/to/train.json \
  --hparams /path/to/hparams.json \
  --opath /path/to/out \
  --verbosity 1
```

4. Collect the parent checkpoint and parent hparam sidecar under `--opath`:

```text
/path/to/out/{job_name}.{top_model_name}.pth
/path/to/out/{job_name}.{top_model_name}.hparam.json
```

5. Author a prediction config pointing at test arrays ([Config](../config.md),
   [Formats](../formats.md)).
6. Run `pred_model` with `--checkpoint` set to the parent `.pth` and
   `--hparams` set to the parent `.hparam.json`.

Training also writes per-module child `.pth` / `.hparam.json` files and logs
metrics to the console (and optionally W&B). Full prediction, attribution, and
output-array contracts arrive in a later documentation slice; until then see
[`pred_model`](../cli/pred_model.md) and
[Checkpoints](../artifacts/checkpoints.md).
