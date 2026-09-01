# Profile masks workflow

Positional validity masks for profile prediction heads in **v0.1.0a8**.

A **positional validity mask** is a boolean annotation aligned to retained
sequence positions, where `true` marks positions eligible for position-wise
losses and metrics.

- Train/val profile payloads may include optional `mask_npy`
- Test payloads must not include a mask
- Mask geometry follows the retained embedding length after trimming

See [Profiles](../profiles.md), [Glossary](../reference/glossary.md), and
[Masks](../data/masks.md).

Coming in a later documentation slice: loss and metric interaction tables.
