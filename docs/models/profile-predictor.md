# ProfilePredictor

Profile prediction head for **v0.1.0a8**.

Nestable only under `EncoderPredictor.predictor`. Consumes the shared trimmed
encoder embedding and emits a **profile distribution** over **profile bins**
plus a paired nonnegative **profile count** per **profile track**. See
[Model composition](composition.md). Geometry, masks, artifacts, and
attribution targets are expanded on [Profile reconstruction](../profiles.md).

## Configuration

| Key | Type | Notes |
| --- | --- | --- |
| `model_name` | non-empty string | Unique across the composition tree; used in artifact filenames |
| `track_names` | non-empty array of unique strings | Ordered profile-track identities; each must match `[A-Za-z0-9][A-Za-z0-9._-]*` (no `:` or `,`) |
| `bin_size` | integer ≥ 1 | Contiguous retained bases per profile bin |

`T = len(track_names)`. Retained length `L_embed` after `embedding_trimming`
must be positive and exactly divisible by `bin_size`; then
`P = L_embed / bin_size`.

<!-- schema: schemas/v0.1.0a8/profile-predictor-model-config.schema.json -->
```json
{
  "model_name": "atac_profile",
  "track_names": ["short", "mono", "di"],
  "bin_size": 10
}
```

Nested reference under `predictor`:

```json
{
  "model_type": "ProfilePredictor",
  "model_config": {
    "model_name": "atac_profile",
    "track_names": ["short", "mono", "di"],
    "bin_size": 10
  }
}
```

`ProfilePredictor` is never a valid top-level CLI `model_type`.

## Hyperparameters

Each `hparams.predictor.<head_key>` entry for this head uses the profile
wrapper with exact keys `profile_alpha`, `profile_loss`, `count_alpha`,
`count_loss`, and `predictor_config` (no scalar `alpha` / `loss`):

| Key | Type | Notes |
| --- | --- | --- |
| `profile_alpha` | finite number ≥ 0 | Weight on the profile-distribution component |
| `count_alpha` | finite number ≥ 0 | Weight on the profile-count component |
| `profile_loss` | `{ "type", "params" }` | Must be `profile_cross_entropy` with `params: {}` |
| `count_loss` | `{ "type", "params" }` | Must be `log1p_mse` with `params: {}` |
| `predictor_config` | object | Count-branch FC stack settings (below) |

`predictor_config` fields (count branch only; profile average-pooling is fixed
by `bin_size`):

| Key | Type | Notes |
| --- | --- | --- |
| `n_fc_layers` | integer ≥ 1 | Required; final layer maps to width `T` |
| `fc_hidden_dims` | array of integers ≥ 1 | Length ≥ `n_fc_layers - 1` (prefix used) |
| `dropout` | number in `[0, 1)` | Required |
| `activation` | `relu` \| `gelu` \| `silu` | Required |
| `pooling_methods` | `GAP` \| `GMP` | Required; pools the **unbinned** retained embedding |
| `batch_size` | integer ≥ 1 | Optional; inherits from parent when omitted |
| `learning_rate` | number ≥ 0 | Optional; `0` freezes **both** profile and count branches |
| `n_channels` | integer ≥ 1 | Optional; inherits from parent when omitted |

Canonical wrapper, inheritance, and freeze rules:
[Hyperparameters](../configuration/hyperparameters.md). Loss object contract:
[Losses](../configuration/losses.md).

<!-- schema: schemas/v0.1.0a8/profile-head-hparams-wrapper.schema.json -->
```json
{
  "profile_alpha": 1.0,
  "profile_loss": { "type": "profile_cross_entropy", "params": {} },
  "count_alpha": 1.0,
  "count_loss": { "type": "log1p_mse", "params": {} },
  "predictor_config": {
    "n_fc_layers": 1,
    "fc_hidden_dims": [],
    "dropout": 0.0,
    "activation": "relu",
    "pooling_methods": "GAP"
  }
}
```

Across the whole model, at least one scalar `alpha` or profile component weight
must be strictly positive. Zero-weight components still require labels and
still emit diagnostics. Do not put `track_names` or `bin_size` in a tune space.

## Losses

| Component | Required `type` | Consumes | Mask interaction |
| --- | --- | --- | --- |
| Profile distribution | `profile_cross_entropy` | Profile logits vs `profile_npy` | Optional positional validity mask excludes invalid bins |
| Profile count | `log1p_mse` | Count logits vs `count_npy` | Never masked |

Masks never change public predictions, reconstructed counts, or attribution
arrays. See [Profile masks](../workflows/profile-masks.md).

## Inputs and outputs

| Tensor | Shape | Notes |
| --- | --- | --- |
| Input | `(B, C, L_embed)` | Shared trimmed encoder embedding |
| Profile distributions | `(N, T, P)` | Softmax over `P` independently per row/track (sums to 1) |
| Profile counts | `(N, T)` | Nonnegative reconstructed totals |

Channels follow `track_names` order. Profile bin `j` covers retained positions
`[j * bin_size, (j + 1) * bin_size)` from the left edge of the retained window
(no padding or truncation).

### Count pairing

Every profile track has exactly one paired profile count. Count labels are
authoritative magnitudes; equality to the sum of profile-label bins is **not**
required. Training always consumes both arrays together.

## Labels and artifacts

| Surface | Contract |
| --- | --- |
| Data keys | `profile_npy`, `count_npy`; optional `mask_npy` on train/val only |
| Profile labels | `(N, T, P)` finite nonnegative; rank-2 shortcuts invalid even when `T = 1` |
| Count labels | `(N, T)` finite nonnegative |
| Positional validity mask | boolean `(N, L_embed)`; missing ⇒ all-valid |
| Prediction artifacts | `{job}.{ep}.{head}.profile.npy` and `.count.npy` |

Train/val require both profile and count arrays for every declared profile
head. Prediction may omit the head payload, or supply both label fields
together; `mask_npy` is rejected on test. Full shape/dtype tables:
[Labels](../data/labels.md) and [Masks](../data/masks.md).

## Related pages

- [Profile reconstruction](../profiles.md)
- [ClassPredictor](class-predictor.md) / [RegressPredictor](regress-predictor.md)
- [Model composition](composition.md)
- [Profile masks](../workflows/profile-masks.md)
- [Prediction artifacts](../artifacts/predictions.md)
- [Losses](../configuration/losses.md)
