# Multi-source loading

Multi-source path and weight contracts for **v0.1.0a8**.

- Path fields accept a string or a non-empty parallel path array
- `source_fracs` length must match the number of OHE sources `S`
- Every `source_fracs` entry must be `> 0`
- Single-source runs require `source_fracs: [1]` (or `[1.0]`)
- Per source, OHE rows `N_s` must align with that source's label rows
- All sources share one sequence length `L`; scalar trailing widths are fixed
  per head across sources

Canonical split tables: [Splits](splits.md). Array and label geometry:
[Arrays](arrays.md), [Labels](labels.md).

See also [Multi-source data workflow](../workflows/multi-source-data.md) and
[Formats](../formats.md).
