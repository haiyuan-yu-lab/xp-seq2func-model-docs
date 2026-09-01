# Attribution workflow

Choose an **attribution target** and **output domain**, run Captum attribution
through `pred_model`, and interpret the resulting arrays for exact release
**v0.1.0a8**.

Attribution is CLI-only. Prediction JSON must not contain keys matching
`attribution*`; see [Prediction configuration](../configuration/prediction.md).
Array contracts live on [Attributions](../artifacts/attributions.md). Flag
summary: [`pred_model`](../cli/pred_model.md).

## Modes

| Mode | CLI | Behavior |
| --- | --- | --- |
| Off | omit `--attribution` | Prediction arrays only; no `attr_*.npy` |
| Legacy | `--attribution METHOD` only | One `attr_{method}.npy` per `ClassPredictor` / `RegressPredictor` head; **rejected** if any `ProfilePredictor` is present |
| Explicit | `--attribution METHOD --attribution-target TARGET` | Exactly one target-qualified `attr_*.npy` for the selected head |

`--attribution-target` requires `--attribution` and accepts exactly one value
per invocation. Ordinary prediction arrays for every head are always written
whether attribution is off, legacy, or explicit.

### Legacy versus explicit

| Aspect | Legacy (no `--attribution-target`) | Explicit (`--attribution-target`) |
| --- | --- | --- |
| Files written | One per scalar head | One for the named head only |
| Class heads | **Predicted-class attribution**: per-row argmax of that head's probabilities (row-dependent) | Fixed class / logit / logit-difference are row-independent; `logit:predicted` is row-dependent |
| Regression heads | Channel `0` of the scalar output | Not a valid explicit-target head type |
| Profile heads | Rejected | Required; profile-bin or count targets only |
| Shared target meaning | No single shared class across the array for classification | Explicit fixed targets share one meaning across rows |

Prefer an explicit target whenever you need one **attribution target** with a
stable **output domain** across the batch.

## Attribution-target grammar

```text
<head>:<domain>:<selector>
```

| Part | Rule |
| --- | --- |
| `<head>` | Predictor map key from `model_config.predictor` (must not contain `:`) |
| `<domain>` | Output-domain token from the tables below |
| `<selector>` | Class index, class pair, `predicted`, track name, or `track,bin` |

Filenames use each head's `model_name`, not the map key. The map key appears
only in the target string.

Structural snapshot (patterns only):
[attribution-target-string.schema.json](../schemas/v0.1.0a8/attribution-target-string.schema.json).
Runtime validation remains authoritative for class ranges, track membership,
bin counts, leading zeros, and head-type compatibility.

### ClassPredictor forms

| Form | Output domain | Row dependence | Filename qualifier |
| --- | --- | --- | --- |
| `<head>:probability:<k>` | Class probability for fixed class `k` | Row-independent | `probability_{k}` |
| `<head>:logit:<k>` | Class logit for fixed class `k` | Row-independent | `logit_{k}` |
| `<head>:logit-difference:<p>,<n>` | Logit(`p`) − logit(`n`) | Row-independent | `logit-difference_{p}_{n}` |
| `<head>:logit:predicted` | Logit of the per-row predicted class | Row-dependent (**predicted-class attribution**) | `logit_predicted` |

`k`, `p`, and `n` are nonnegative decimal integers without leading zeros
(except the digit `0` itself). For logit-difference, `p` and `n` must be
distinct and both in `[0, n_class)`.

### ProfilePredictor forms

| Form | Output domain | Row dependence | Filename qualifier |
| --- | --- | --- | --- |
| `<head>:profile-probability:<track>,<bin>` | Profile-bin probability | Row-independent | `profile-probability_{track}_{bin}` |
| `<head>:profile-logit:<track>,<bin>` | Profile-bin logit | Row-independent | `profile-logit_{track}_{bin}` |
| `<head>:count:<track>` | Reconstructed profile count | Row-independent | `count_{track}` |
| `<head>:log1p-count:<track>` | Internal unrestricted log-count `z` for that track (not `log1p` of the reconstructed count) | Row-independent | `log1p-count_{track}` |

`<track>` must match a configured `track_names` entry for that head.
`<bin>` is a nonnegative decimal integer without leading zeros and must lie in
`[0, P)`. Profile distribution and profile count attributions require separate
invocations. Positional validity masks do not change attribution targets or
arrays; see [Profiles](../profiles.md) and
[Profile masks](profile-masks.md).

### Profile incompatibility of legacy mode

Targetless legacy attribution is invalid whenever the model tree contains any
`ProfilePredictor`. Models with profile heads must pass an explicit
`--attribution-target`. The same rule is recorded on
[`pred_model`](../cli/pred_model.md#attribution-flags-summary) and
[Profiles](../profiles.md#attribution).

## Invalid combinations

Rejected conditions (exact exception text is not stabilized):

| Condition | Why |
| --- | --- |
| `--attribution-target` without `--attribution` | Target requires a method |
| More than one `--attribution-target` value | Exactly one target per run |
| Legacy mode with any `ProfilePredictor` | Profile scalars need an explicit target |
| Unknown `<head>` map key | Head must exist in `predictor` |
| Class domain on a non-`ClassPredictor` head | Class forms are classification-only |
| Profile domain on a non-`ProfilePredictor` head | Profile forms are profile-only |
| Explicit target on `RegressPredictor` | Regression has no explicit-target form |
| Class / bin index out of range | Must fit `n_class` or `P` |
| Unknown track name | Must be in that head's `track_names` |
| Logit-difference with `p == n` | Positive and negative must differ |
| Leading zeros on numeric selectors (for example `01`) | Decimal form without padding |
| Wrong number of `:` parts or malformed selectors | Must match the grammar |
| Head map key containing `:` | Colon is the field separator |

## Methods

| Token | Captum method | Notes |
| --- | --- | --- |
| `ig` | Integrated Gradients | Zero baseline; `n_steps=50` |
| `saliency` | Saliency | Signed gradients (`abs=False`) |
| `deepshap` | DeepLiftShap | All-zeros reference batch of size `2` |

## Examples

Placeholder paths only; this documentation does not ship datasets or
checkpoints. Structural target-string checks use the schema snapshot.

### Explicit class probability

<!-- schema: schemas/v0.1.0a8/attribution-target-string.schema.json -->
```json
"cls:probability:1"
```

```bash
pred_model \
  --config /path/to/pred.json \
  --hparams /path/to/out/demo_train.ep_main.hparam.json \
  --checkpoint /path/to/out/demo_train.ep_main.pth \
  --opath /path/to/pred_out \
  --attribution ig \
  --attribution-target cls:probability:1 \
  --verbosity 1
```

Writes (among prediction arrays):

```text
/path/to/pred_out/demo_pred.ep_main.cls_head.attr_ig.probability_1.npy
```

### Logit difference

<!-- schema: schemas/v0.1.0a8/attribution-target-string.schema.json -->
```json
"cls:logit-difference:1,0"
```

```bash
pred_model \
  --config /path/to/pred.json \
  --hparams /path/to/out/demo_train.ep_main.hparam.json \
  --checkpoint /path/to/out/demo_train.ep_main.pth \
  --opath /path/to/pred_out \
  --attribution saliency \
  --attribution-target cls:logit-difference:1,0
```

### Predicted-class logit (row-dependent)

<!-- schema: schemas/v0.1.0a8/attribution-target-string.schema.json -->
```json
"cls:logit:predicted"
```

### Profile bin and count (separate runs)

<!-- schema: schemas/v0.1.0a8/attribution-target-string.schema.json -->
```json
"prof:profile-probability:atac_a,12"
```

<!-- schema: schemas/v0.1.0a8/attribution-target-string.schema.json -->
```json
"prof:log1p-count:atac_a"
```

```bash
pred_model \
  --config /path/to/pred_profile.json \
  --hparams /path/to/out/demo_train.ep_profile.hparam.json \
  --checkpoint /path/to/out/demo_train.ep_profile.pth \
  --opath /path/to/pred_out \
  --attribution deepshap \
  --attribution-target prof:profile-probability:atac_a,12

pred_model \
  --config /path/to/pred_profile.json \
  --hparams /path/to/out/demo_train.ep_profile.hparam.json \
  --checkpoint /path/to/out/demo_train.ep_profile.pth \
  --opath /path/to/pred_out \
  --attribution deepshap \
  --attribution-target prof:log1p-count:atac_a
```

### Legacy (classification / regression only)

```bash
pred_model \
  --config /path/to/pred.json \
  --hparams /path/to/out/demo_train.ep_main.hparam.json \
  --checkpoint /path/to/out/demo_train.ep_main.pth \
  --opath /path/to/pred_out \
  --attribution ig
```

Writes one `attr_ig.npy` per scalar head. Do not use this form when any
profile head is present.

### Invalid target strings (illustrative)

These fail structural or runtime checks; they are not schema-associated
examples:

```text
cls:probability          # missing selector part
cls:logit-difference:1   # needs <p>,<n>
cls:probability:01       # leading zero rejected at runtime
reg:logit:0              # RegressPredictor is not an explicit-target head
prof:probability:0       # class domain on a profile head
```

## Related pages

- [`pred_model`](../cli/pred_model.md)
- [Attributions](../artifacts/attributions.md)
- [Predictions](../artifacts/predictions.md)
- [Profiles](../profiles.md)
- [Prediction configuration](../configuration/prediction.md)
- [Schemas](../reference/schemas.md)
