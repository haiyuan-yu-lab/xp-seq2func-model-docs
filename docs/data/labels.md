# Labels

Label array contracts for prediction heads in **v0.1.0a8**.

- `ClassPredictor` / `RegressPredictor`: `label_npy`
- `ProfilePredictor`: paired `profile_npy` and `count_npy`
- Train/val require labels for every declared head; prediction may omit labels

See [Formats](../formats.md) and [Profiles](../profiles.md).

Coming in a later documentation slice: class-shape and value constraints.
