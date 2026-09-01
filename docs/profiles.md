# Profile reconstruction

`ProfilePredictor` is a nestable head that reconstructs one or more named
signal tracks over a retained sequence window and a paired nonnegative count
per track. Use it alongside `ClassPredictor` and `RegressPredictor` heads in
the same `EncoderPredictor`.

## Geometry

| Quantity | Meaning |
| --- | --- |
| `track_names` | Ordered unique track identifiers (filename-safe tokens) |
| `bin_size` | Contiguous retained bases per output bin (`≥ 1`) |
| `L_embed` | Retained embedding length after `embedding_trimming` |
| `P` | `L_embed / bin_size` (must divide exactly) |

The profile branch average-pools the embedding with kernel/stride `bin_size`
(no padding), then applies a pointwise projection to `len(track_names)`
channels. The count branch pools the **unbinned** embedding and maps it
through an FC stack to one count logit per track.

Public outputs:

| Tensor | Shape | Domain |
| --- | --- | --- |
| Profile | `(N, T, P)` | Probabilities over bins (sum to 1 over `P` per row/track) |
| Count | `(N, T)` | Nonnegative reconstructed totals |

## Data config

Under `train_data` / `val_data` / `test_data`, a profile head payload uses:

| Field | Train/val | Test | Array shape |
| --- | --- | --- | --- |
| `profile_npy` | required | optional with `count_npy` | `(N, T, P)` finite nonnegative |
| `count_npy` | required | optional with `profile_npy` | `(N, T)` finite nonnegative |
| `mask_npy` | optional | forbidden | boolean `(N, L_embed)` |

Path fields accept a string or a non-empty array parallel to `encoder.ohe_npy`.
Supply both profile and count together, or omit the whole payload on test.
Do not put `label_npy` on a profile payload.

### Positional validity masks

`mask_npy` marks retained bases that may participate in profile loss and
Pearson diagnostics. Missing masks behave as all-valid. A profile bin is valid
only when every retained base in that bin is `true`. Masks do not change count
loss, public predictions, or attribution.

## Hparams wrapper

Profile heads use component weights and losses instead of scalar `alpha` /
`loss`:

```json
{
  "profile_alpha": 1.0,
  "profile_loss": {"type": "profile_cross_entropy", "params": {}},
  "count_alpha": 1.0,
  "count_loss": {"type": "log1p_mse", "params": {}},
  "predictor_config": {
    "n_fc_layers": 1,
    "fc_hidden_dims": [],
    "dropout": 0.0,
    "activation": "relu",
    "pooling_methods": "GAP"
  }
}
```

Component weights are finite reals `≥ 0`. At least one scalar `alpha` or
profile component weight in the model must be strictly positive. Zero-weight
components still require labels and still emit diagnostics.

Tune space may sweep the component weights/losses and count-branch fields
above. Do not put `track_names` or `bin_size` in the tune space.

## Minimal example

One single-track head (`bin_size: 1`) and one three-track head (`bin_size: 5`)
over a trimmed window:

```json
{
  "model_type": "EncoderPredictor",
  "model_config": {
    "model_name": "ep_profile",
    "embedding_trimming": 0,
    "encoder": {
      "model_type": "ConvEncoder",
      "model_config": {"model_name": "enc"}
    },
    "predictor": {
      "grocap": {
        "model_type": "ProfilePredictor",
        "model_config": {
          "model_name": "grocap_head",
          "track_names": ["grocap"],
          "bin_size": 1
        }
      },
      "atac": {
        "model_type": "ProfilePredictor",
        "model_config": {
          "model_name": "atac_head",
          "track_names": ["atac_a", "atac_b", "atac_c"],
          "bin_size": 5
        }
      }
    }
  }
}
```

Synthetic array shapes for `L_input = 1000`, `embedding_trimming = 0`:

| Array | `grocap` | `atac` |
| --- | --- | --- |
| Profile labels | `(N, 1, 1000)` | `(N, 3, 200)` |
| Count labels | `(N, 1)` | `(N, 3)` |
| Optional mask | `(N, 1000)` bool | same shared file allowed |

## Prediction artifacts

```text
{job}.{encoder_predictor}.{profile_model}.profile.npy   # float32 (N,T,P)
{job}.{encoder_predictor}.{profile_model}.count.npy     # float32 (N,T)
```

Rows follow deterministic multi-source order; channels follow `track_names`.

## Attribution

Models that contain any `ProfilePredictor` require an explicit
`--attribution-target`. Supported forms:

```text
<head>:profile-probability:<track>,<bin>
<head>:profile-logit:<track>,<bin>
<head>:count:<track>
<head>:log1p-count:<track>
```

Each invocation writes one target-qualified `(N, 4, L_input)` float32 array
while still writing ordinary predictions for every head. Profile and count
attributions need separate invocations.

## Checkpoints

Profile heads serialize as one catalogued module owning both branches. The
checkpoint stores ordered `track_names` and `bin_size` under `contracts` so
same-shaped but semantically reordered heads fail to load.

## Logged diagnostics

Besides combined `train_loss` / `val_loss`, training logs unweighted component
losses and masked Pearson diagnostics:

```text
train|val:<head>:profile_loss
train|val:<head>:count_loss
train|val:<head>:profile_pearson
train|val:<head>:profile_pearson:<track>
```

Combined validation loss remains the only early-stopping and tuning objective.
