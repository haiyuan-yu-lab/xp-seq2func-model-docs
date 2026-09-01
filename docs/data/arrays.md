# Arrays

NumPy array contracts used by the **v0.1.0a8** CLIs. This page covers sequence
(one-hot) arrays referenced as `encoder.ohe_npy`. Label arrays are documented
on [Labels](labels.md).

Documentation does not publish `.npy` binaries; examples use placeholder paths
only.

## One-hot sequence arrays (`encoder.ohe_npy`)

| Property | Contract |
| --- | --- |
| Path form | Non-empty string, or non-empty array of paths (one per source) |
| Requiredness | Required on every split (`train_data` / `val_data` / `test_data`) |
| Shape | `(N, 4, L)` per source file |
| Channel order | Axis 1 is bases **A, C, G, T** (indices `0..3`) |
| dtype / values | Numeric one-hot (or soft) encodings over the four channels; rank must be 3 with channel axis length 4 |
| Alignment | Row `i` pairs with row `i` of every label array for the same source |
| Cross-source | All sources share one sequence length `L`; row counts `N_s` may differ |

`N` is the per-source row count. `L` is the shared input length. Empty path
lists fail closed.

## Path and source alignment

| Rule | Behavior |
| --- | --- |
| `S` | Number of OHE paths after normalizing a bare string to a length-1 list |
| Parallel labels | Every head path field must list the same `S` in the same order |
| `source_fracs` | Length `S`; all entries `> 0`; `S = 1` ⇒ `[1]` |

`batch_size` is not part of the array contract; it lives in hparams.

## Invalid cases (described)

- Rank other than 3, or channel axis ≠ 4
- Sources with disagreeing `L`
- Label row count that does not match that source's `N`
- Empty `ohe_npy` arrays

Exact exception strings are not stabilized here.

## Related pages

- [Splits](splits.md)
- [Labels](labels.md)
- [Geometry](geometry.md)
- [Formats overview](../formats.md)
- [ConvEncoder inputs](../models/conv-encoder.md)
