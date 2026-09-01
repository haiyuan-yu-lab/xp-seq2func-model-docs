# Checkpoints

Checkpoint artifacts written and consumed in **v0.1.0a8**.

- Train and tune write a parent `.pth` plus per-module artifacts under
  `--opath`
- `pred_model --checkpoint` loads the parent checkpoint
- Optional `init_checkpoint` can load selected modules before training

See [Formats](../formats.md) and
[Config: init_checkpoint](../config.md#init_checkpoint-train--tune).

Coming in a later documentation slice: filename patterns and state layout.
