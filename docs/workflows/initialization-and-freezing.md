# Initialization and freezing

Warm-start and freeze selected modules during train or tune in **v0.1.0a8**.

- Optional `init_checkpoint` loads catalogued `model_name` entries from a
  `.pth` before training
- Nested `learning_rate: 0` freezes a module and omits it from Adam
- Top-level `learning_rate` must remain `> 0`
- Freezing every trainable module fails when Adam is built

Canonical learning-rate, inheritance, and Adam rules:
[Hyperparameters](../configuration/hyperparameters.md).
Also see [Concepts](../concepts.md#learning-rates-and-freezing) and
[Config: init_checkpoint](../config.md#init_checkpoint-train--tune).
