# Geometry

Shared geometry rules for sequence length, embedding trimming, and profile bins
in **v0.1.0a9**.

## Embedding trimming

| Quantity | Rule |
| --- | --- |
| Input length | `L` from one-hot arrays shaped `(N, 4, L)` |
| Trimming `T` | Top-level `embedding_trimming` (integer ≥ 0) |
| Retained length | `L_embed = L - 2T` and must be `> 0` |

All prediction heads share that trimmed embedding.

## Profile bins

| Quantity | Rule |
| --- | --- |
| `bin_size` | Integer ≥ 1 on each `ProfilePredictor` |
| Divisibility | `L_embed` must be exactly divisible by `bin_size` |
| Bin count | `P = L_embed / bin_size` |
| Track count | `T = len(track_names)` |
| Bin span | Bin `j` covers retained positions `[j * bin_size, (j + 1) * bin_size)` |

Positional validity masks are stored at retained-base resolution `(N, L_embed)`
and reduce to bin validity by AND within each bin. See [Masks](masks.md).

## Related pages

- [Model composition](../models/composition.md)
- [Profiles](../profiles.md)
- [ProfilePredictor](../models/profile-predictor.md)
- [Arrays](arrays.md)
