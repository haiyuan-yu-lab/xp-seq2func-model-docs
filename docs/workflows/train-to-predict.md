# Train to predict

End-to-end path from training artifacts to prediction outputs for **v0.1.0a8**.

1. Install from tag `v0.1.0a8` ([Install](../install.md)).
2. Author train config and hparams ([Config](../config.md)).
3. Run `train_model` and collect the parent checkpoint under `--opath`.
4. Author a prediction config pointing at test arrays ([Formats](../formats.md)).
5. Run `pred_model` with `--checkpoint` set to the parent `.pth`.

Coming in a later documentation slice: full JSON walkthroughs and artifact
tables. Until then see [CLI overview](../cli/index.md) and
[Artifacts](../artifacts/checkpoints.md).
