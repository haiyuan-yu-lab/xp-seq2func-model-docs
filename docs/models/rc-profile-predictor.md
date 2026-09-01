# RCProfilePredictor

Reverse-complement-aware profile head for **v0.1.0a9** (`preserve` and `swap_pair`
modes).

Nestable only under `EncoderPredictor.predictor`. It preserves the same
external role as `ProfilePredictor` — profile/count labels, component losses,
Pearson metrics, `*.profile.npy` / `*.count.npy` artifacts, and explicit
profile/count attribution targets — while making profile and count outputs
follow the selected `track_transform` under the embedding reverse-complement
transform.

See [Model composition](composition.md) and
[ProfilePredictor](profile-predictor.md) for the ordinary counterpart.

## Configuration

| Key | Type | Notes |
| --- | --- | --- |
| `model_name` | non-empty string | Unique across the composition tree; used in artifact filenames |
| `track_names` | non-empty array of unique strings | Ordered profile-track identities; each must match `[A-Za-z0-9][A-Za-z0-9._-]*` |
| `bin_size` | integer ≥ 1 | Contiguous retained bases per profile bin |
| `track_transform` | `"preserve"` \| `"swap_pair"` | Required; `swap_pair` requires exactly two tracks (names arbitrary) |

`T = len(track_names)`. Retained length `L_embed` after `embedding_trimming`
must be positive and exactly divisible by `bin_size`; then
`P = L_embed / bin_size`.

### Preserve mode

Track order is unchanged under embedding RC; profile bins reverse.

```json
{
  "model_name": "atac_profile",
  "track_names": ["short", "mono"],
  "bin_size": 10,
  "track_transform": "preserve"
}
```

### Strand-coupled (`swap_pair`) mode

Exactly two tracks. Under embedding RC, profile bins reverse **and** the two
track slots swap; counts swap track slots only (no position axis).

```json
{
  "model_name": "strand_profile",
  "track_names": ["alpha", "beta"],
  "bin_size": 10,
  "track_transform": "swap_pair"
}
```

Nested reference under `predictor`:

```json
{
  "model_type": "RCProfilePredictor",
  "model_config": {
    "model_name": "atac_profile",
    "track_names": ["short", "mono"],
    "bin_size": 10,
    "track_transform": "preserve"
  }
}
```

<!-- schema: schemas/v0.1.0a9/rc-profile-predictor-model-config.schema.json -->

## Hyperparameters

Each `hparams.predictor.<head_key>` entry uses the same profile wrapper as
`ProfilePredictor` (`profile_alpha`, `profile_loss`, `count_alpha`,
`count_loss`, `predictor_config`).

`predictor_config` fields match `ProfilePredictor`, with extra constraints:

| Key | Type | Notes |
| --- | --- | --- |
| `n_fc_layers` | integer ≥ 1 | Required; final layer maps to width `T` |
| `fc_hidden_dims` | array of integers ≥ 1 | Length ≥ `n_fc_layers - 1` (prefix used); every entry must be **even** when `track_transform` is `swap_pair` |
| `dropout` | number in `[0, 1)` | Required |
| `activation` | `relu` \| `gelu` \| `silu` | Required |
| `pooling_methods` | `GAP` \| `GMP` | Required; count branch only |
| `batch_size` | integer ≥ 1 | Optional; inherits from parent when omitted |
| `learning_rate` | number ≥ 0 | Optional; `0` freezes both branches |
| `n_channels` | **even** integer ≥ 2 | Optional; inherits from parent when omitted |

Canonical wrapper, inheritance, and freeze rules:
[Hyperparameters](../configuration/hyperparameters.md). Loss object contract:
[Losses](../configuration/losses.md).

## Forward behavior

### Profile branch

After the same fixed `AvgPool1d` binning as `ProfilePredictor`, a
representation-aware pointwise projection maps even regular channels to
`T` track logits.

| `track_transform` | Projection | Eval-mode RC behavior |
| --- | --- | --- |
| `preserve` | Independent Reg→scalar map per track | Flip bin axis only |
| `swap_pair` | Single Reg→one-regular-pair map (`T = 2`) | Flip bins and swap track slots |

Softmax still normalizes over bins independently per row/track.

| Mode | Profile behavior |
| --- | --- |
| Eval | Equivariance per table above |
| Train | No profile dropout in this revision |

### Count branch

| `track_transform` | Stack | Eval-mode RC behavior |
| --- | --- | --- |
| `preserve` | Ordinary pooled FC, then average both embedding orientations | Invariant |
| `swap_pair` | Regular-equivariant pooled FC (even hidden widths) | Swap the two track slots |

**Preserve** symmetrization:

```text
log_counts(x) = 0.5 × ( f(x) + f(RC_embed(x)) )
counts = expm1(max(log_counts, 0))
```

**Swap pair** (no orientation average):

```text
log_counts(x) = g(x)
counts = expm1(max(log_counts, 0))
```

| Mode | Count behavior |
| --- | --- |
| Eval | Per table above |
| Train | Dropout applied in-distribution (successive calls need not match) |

There is no required encoder family pairing.

## Inputs and outputs

| Tensor | Shape | Notes |
| --- | --- | --- |
| Input | `(B, C, L_embed)` | Shared trimmed encoder embedding; `C` must be even |
| Profile distributions | `(N, T, P)` | Softmax over `P` independently per row/track |
| Profile counts | `(N, T)` | Nonnegative reconstructed totals |

Labels, masks, losses, metrics, and artifacts remain in configured `track_names`
order for both modes.

## Labels and artifacts

Same contracts as [ProfilePredictor](profile-predictor.md): `profile_npy`,
`count_npy`, optional train/val `mask_npy`, and paired prediction artifacts
`*.profile.npy` / `*.count.npy`.

## Checkpoints

New training runs write typed `seq2func_ckpt_v2` checkpoints with
`model_type: RCProfilePredictor` and `track_transform` (`preserve` or
`swap_pair`) in `contracts`. Legacy `seq2func_ckpt_v1` checkpoints cannot load
into a composition tree that contains this head type.

## Related pages

- [ProfilePredictor](profile-predictor.md)
- [RCRegressPredictor](rc-regress-predictor.md)
- [Model composition](composition.md)
- [Profile reconstruction](../profiles.md)
- [Checkpoints](../artifacts/checkpoints.md)
