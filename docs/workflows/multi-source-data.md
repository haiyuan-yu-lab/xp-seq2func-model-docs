# Multi-source data workflow

Combine multiple one-hot sequence sources in **v0.1.0a8**.

- `encoder.ohe_npy` may be a string or a non-empty path array
- `source_fracs` must provide one positive weight per source
- Single-source runs use `source_fracs: [1]`

Label and mask path arrays must stay aligned with the OHE sources. See
[Formats](../formats.md) and [Multi-source data contract](../data/multi-source.md).

Coming in a later documentation slice: complete invariants and invalid examples.
