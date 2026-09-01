# Compatibility

Compatibility statement for exact release **v0.1.0a8**.

## Exact-release accuracy

This documentation site describes the public CLI, configuration, data, and
artifact contracts of tag **v0.1.0a8** only. Facts on this site are intended to
match that exact release.

## No cross-alpha promise

Alpha tags may change flags, configuration keys, array contracts, and artifact
layouts without a migration guide. Do not assume that configs, checkpoints, or
workflows written for an earlier or later alpha are compatible with
**v0.1.0a8**, or the reverse.

Within **v0.1.0a8**, new training runs write typed `seq2func_ckpt_v2`
checkpoints. Loaders accept those files and legacy `seq2func_ckpt_v1` checkpoints
for ordinary-model target trees; see [Checkpoints](../artifacts/checkpoints.md).

Pin the `v0.1.0a8` tag when you need a fixed cut.

## Supported interface boundary

Supported for **v0.1.0a8**:

- `train_model`, `tune_model`, and `pred_model`
- Their documented configuration JSON contracts
- Their documented input data and output artifact contracts

Not supported as a public API:

- Python imports from the installed package
- Incidental module, class, or function surfaces reachable by import

Treat importable symbols as unstable implementation detail unless and until a
future release explicitly documents a Python API.

## Installation access

Source installation requires repository access and authentication. **v0.1.0a8**
is not published to PyPI and is not anonymously installable. See
[Install](../install.md).

## Schema snapshots

JSON Schema files under [`schemas/v0.1.0a8/`](schemas.md) are
documentation-owned snapshots for this exact release. They assist structural
checks and editor tooling; runtime validators in the installed package remain
authoritative for filesystem and tensor semantics that JSON Schema cannot
express.
