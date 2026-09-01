# Multi-source loading

Multi-source path, weight, nesting, and cross-source alignment contracts for
**v0.1.0a8**.

Documentation does not publish `.npy` binaries; examples use placeholder paths
only. Array geometry belongs on [Arrays](arrays.md) and [Labels](labels.md).
Split loader keys belong on [Splits](splits.md). Command surfaces belong on the
CLI and configuration pages linked below.

## Source identity

A **source** is one parallel slot in the encoder one-hot path list.

| Form of `encoder.ohe_npy` | Source count `S` |
| --- | --- |
| Non-empty string | `S = 1` |
| Non-empty array of paths | `S` = array length |

Source identity is the **parallel index** into that list (and into every
aligned label or mask path list). Index `0` is the first path, index `1` the
second, and so on. Empty path arrays fail closed.

`source_fracs` is required on every split and must have length `S`. Every entry
must be a number `> 0`. When `S = 1`, the only valid value is `[1]` (or
`[1.0]`).

## Nesting: single-source vs multi-source

Every split (`train_data`, `val_data`, `test_data`) uses the same nesting:

```text
split
├── encoder
│   ├── ohe_npy   # string | path array (defines S)
│   └── label     # must be null
├── predictor     # map of head key → typed payload (required train/val)
├── shuffle
├── num_workers
├── pin_memory
├── source_fracs  # length S; all > 0; S=1 ⇒ [1]
├── persistent_workers?   # bool | null
└── prefetch_factor?       # int ≥ 1 | null
```

| Nesting | Path fields | `source_fracs` |
| --- | --- | --- |
| Single-source | Bare strings (or length-1 arrays) | Must be `[1]` |
| Multi-source | Parallel path arrays of length `S` | Length `S`, every entry `> 0` |

All label and mask path lists on a split must use the **same `S` and the same
order** as `encoder.ohe_npy`. Train/val require a predictor payload for every
head declared in `model_config.predictor`. Every labeled head must cover **all**
sources (no partial path lists). Prediction may omit `predictor` or individual
heads for unlabeled inference.

Schema snapshots:
[data-source.schema.json](../schemas/v0.1.0a8/data-source.schema.json) (train/val)
and [test-data.schema.json](../schemas/v0.1.0a8/test-data.schema.json)
(prediction). Shared `$defs` live in
[defs.schema.json](../schemas/v0.1.0a8/defs.schema.json).

## Split usage

| Split | Commands | Labels | Profile `mask_npy` |
| --- | --- | --- | --- |
| `train_data` | `train_model`, `tune_model` | Required for every declared head | Optional |
| `val_data` | `train_model`, `tune_model` | Required for every declared head | Optional |
| `test_data` | `pred_model` | Optional | Forbidden |

Typical loader flags: `shuffle: true` on train, `shuffle: false` on val/test.
`batch_size` is **not** a split field; set it in hparams (or the tune-space).

## Loader and sampler options

| Key | Role |
| --- | --- |
| `shuffle` | Controls index sampling (see below) |
| `num_workers` | DataLoader worker count (`≥ 0`) |
| `pin_memory` | DataLoader pin-memory flag |
| `source_fracs` | Per-source positive weights; length `S` |
| `persistent_workers` | Optional; meaningful when `num_workers > 0` |
| `prefetch_factor` | Optional (`≥ 1` or `null`); meaningful when `num_workers > 0` |

### `shuffle` and `source_fracs`

| `shuffle` | Sampling behavior |
| --- | --- |
| `true` | Epoch draws reweight by `source_fracs` (normalized mixture over sources) |
| `false` | Full-draw contiguous order over the concatenated index space; `source_fracs` is still validated but does **not** reweight |

Heads share one index stream: every prediction head on a split advances over
the same sampled global indices.

### Prediction row order

With `shuffle: false` (the usual prediction setting), output rows follow
sources **concatenated in list order**: all rows of source `0`, then source
`1`, and so on. Prediction `N` is the sum of per-source row counts after that
ordering. See [Predictions](../artifacts/predictions.md).

## Cross-source invariants

These rules apply on every applicable head type. Per-array shapes and dtypes:
[Arrays](arrays.md), [Labels](labels.md), [Profiles](../profiles.md),
[Masks](masks.md), [Geometry](geometry.md).

### Shared across all heads

| Invariant | Rule |
| --- | --- |
| Shared sequence length | All OHE sources share one `L` |
| Per-source row alignment | For each source `s`, OHE and every label/mask array share `N_s` |
| Path parallelism | Every path field has the same `S` and source order as `encoder.ohe_npy` |
| Empty paths | Empty path arrays fail |
| Head coverage (train/val) | Predictor map keys ↔ `model_config.predictor` keys; every labeled head covers all sources |
| Shared index stream | All heads on a split consume the same sampler indices |

### `ClassPredictor`

| Invariant | Rule |
| --- | --- |
| Label field | `label_npy` path or path array |
| Shape | `(N_s, n_class)` per source |
| Class count | Trailing width equals that head's `model_config.n_class` (`≥ 2`) and is identical across sources |

### `RegressPredictor`

| Invariant | Rule |
| --- | --- |
| Label field | `label_npy` path or path array |
| Shape | `(N_s, 1)` per source (rank-1 `(N,)` fails) |
| Trailing width | `(1,)` identical across sources |

### `ProfilePredictor`

| Invariant | Rule |
| --- | --- |
| Fields | `profile_npy` and `count_npy` together; optional `mask_npy` on train/val only |
| Profile geometry | `(N_s, T, P)` with track count `T = len(track_names)` and bin count `P` fixed by retained length / `bin_size` |
| Count geometry | `(N_s, T)` with the same `T` |
| Cross-source | Trailing `(T, P)` / `(T,)` match across sources |
| Positional validity mask | Boolean `(N_s, L_embed)` when present; same `S` and order; forbidden on `test_data` |

Profile geometry details: [Profiles](../profiles.md). Mask semantics:
[Masks](masks.md) and [Profile masks workflow](../workflows/profile-masks.md).

## Valid examples

### Single-source train/val block

<!-- schema: schemas/v0.1.0a8/data-source.schema.json -->
```json
{
  "encoder": {
    "ohe_npy": "/path/to/train_ohe.npy",
    "label": null
  },
  "predictor": {
    "cls": { "label_npy": "/path/to/train_cls_labels.npy" },
    "reg": { "label_npy": "/path/to/train_reg_labels.npy" }
  },
  "shuffle": true,
  "num_workers": 0,
  "pin_memory": true,
  "source_fracs": [1]
}
```

### Multi-source train/val block (class + regress + profile/mask)

<!-- schema: schemas/v0.1.0a8/data-source.schema.json -->
```json
{
  "encoder": {
    "ohe_npy": [
      "/path/to/src0_train_ohe.npy",
      "/path/to/src1_train_ohe.npy"
    ],
    "label": null
  },
  "predictor": {
    "cls": {
      "label_npy": [
        "/path/to/src0_train_cls_labels.npy",
        "/path/to/src1_train_cls_labels.npy"
      ]
    },
    "reg": {
      "label_npy": [
        "/path/to/src0_train_reg_labels.npy",
        "/path/to/src1_train_reg_labels.npy"
      ]
    },
    "prof": {
      "profile_npy": [
        "/path/to/src0_train_profile.npy",
        "/path/to/src1_train_profile.npy"
      ],
      "count_npy": [
        "/path/to/src0_train_count.npy",
        "/path/to/src1_train_count.npy"
      ],
      "mask_npy": [
        "/path/to/src0_train_mask.npy",
        "/path/to/src1_train_mask.npy"
      ]
    }
  },
  "shuffle": true,
  "num_workers": 2,
  "pin_memory": true,
  "source_fracs": [0.7, 0.3],
  "persistent_workers": true,
  "prefetch_factor": 2
}
```

### Multi-source unlabeled `test_data`

<!-- schema: schemas/v0.1.0a8/test-data.schema.json -->
```json
{
  "encoder": {
    "ohe_npy": [
      "/path/to/src0_test_ohe.npy",
      "/path/to/src1_test_ohe.npy"
    ],
    "label": null
  },
  "shuffle": false,
  "num_workers": 0,
  "pin_memory": true,
  "source_fracs": [0.5, 0.5]
}
```

## Invalid cases and semantic rejections

JSON Schema snapshots catch structural problems. Runtime also rejects the
conditions below (exact exception strings are not stabilized here).

| Condition | Why it fails |
| --- | --- |
| Empty `ohe_npy` / label / mask path array | Path lists must be non-empty |
| Label or mask path list length ≠ `S` | Parallel source identity broken |
| Missing train/val head, or extras not in `model_config` | Head coverage invariant |
| Labeled head that omits a source | All labeled heads must cover all sources |
| `source_fracs` omitted, wrong length, `≤ 0`, or `S=1` and not `[1]` | Weight contract |
| Disagreeing OHE `L` across sources | Shared sequence length |
| Per-source label/mask `N_s` ≠ that source's OHE `N_s` | Row alignment |
| Classification trailing width ≠ `n_class`, or differs across sources | Class-count invariant |
| Regression labels rank-1 or trailing width ≠ 1 | Regression shape invariant |
| Profile/count trailing geometry disagrees across sources | Profile geometry invariant |
| `mask_npy` on `test_data` | Masks are train/val only |
| Profile payload with only one of `profile_npy` / `count_npy` | Paired fields required together |
| Unknown split keys or `batch_size` on the split | Fail-closed loader surface |

## Related pages

- [Multi-source data workflow](../workflows/multi-source-data.md)
- [Splits](splits.md)
- [Arrays](arrays.md)
- [Labels](labels.md)
- [Formats overview](../formats.md)
- [Train configuration](../configuration/train.md)
- [Tune configuration](../configuration/tune.md)
- [Prediction configuration](../configuration/prediction.md)
- [Schemas](../reference/schemas.md)
