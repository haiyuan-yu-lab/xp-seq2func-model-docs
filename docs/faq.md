# FAQ

## Do I need a GPU?

Yes. All three CLIs require CUDA at runtime and exit if no CUDA device is
available.

## Why does tune_model insist on CUDA_VISIBLE_DEVICES?

Each W&B agent worker is pinned to one device token from that variable. The
token list must be non-empty, comma-separated, and free of duplicates. If you
pass `--num-agents`, it must equal the token count.

## Can I use ConvEncoder, ConvSelfAttEncoder, ClassPredictor, RegressPredictor, ProfilePredictor, or their RC-aware counterparts as the top-level model_type?

No. In **v0.1.0a8** only `EncoderPredictor` is a top-level CLI model type.
Encoders (`ConvEncoder`, `RCConvEncoder`, `ConvSelfAttEncoder`,
`RCConvSelfAttEncoder`) and prediction heads (`ClassPredictor`,
`RCClassPredictor`, `RegressPredictor`, `RCRegressPredictor`,
`ProfilePredictor`, `RCProfilePredictor`) are nestable components inside
`model_config`.

## Where do prediction files go?

Under `--opath`, named by head type:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred_class.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.profile.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.count.npy
```

(`ClassPredictor` / `RCClassPredictor` → `.pred_class.npy`; `RegressPredictor`
/ `RCRegressPredictor` → `.pred.npy`; `ProfilePredictor` / `RCProfilePredictor`
→ paired `.profile.npy` / `.count.npy`.)

With `--attribution METHOD`, also:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{METHOD}.npy
```

Add `--attribution-target` to select one scalar and write a single
target-qualified `attr_*.npy` instead: a classification head probability,
logit, logit-difference, or predicted logit, or a profile head profile bin
(`profile-probability` / `profile-logit`) or track count (`count` /
`log1p-count`). Models containing a profile head require an explicit target.
See [pred_model](cli/pred_model.md) and [Profiles](profiles.md).

## Can I freeze an encoder or head during training?

Yes. Set that module's nested `learning_rate` to `0` in hparams (or in the
tune-space leaf for that path). The module's parameters are frozen and left
out of Adam. Top-level `learning_rate` must remain `> 0`. Freezing a
`ProfilePredictor` freezes both branches. See
[Concepts](concepts.md#learning-rates-and-freezing) and
[Initialization and freezing](workflows/initialization-and-freezing.md).

## Can I initialize from a pretrained encoder (or other module)?

Yes. On the train or tune config, set optional `init_checkpoint` with `path`
(to a `.pth`) and `modules` (catalogued `model_name` strings to load). Other
modules stay randomly initialized. Combine with nested `learning_rate: 0` to
freeze the loaded modules. This is selective weight init, not
`pred_model --checkpoint` full restore and not optimizer-state resume. See
[Initialization and freezing](workflows/initialization-and-freezing.md) and
[Config](config.md#init_checkpoint-train--tune).

## Is there a PyPI package?

No. **v0.1.0a8** is not published to PyPI and is not anonymously installable.
Source installation requires repository access and authentication. See
[Install](install.md) and [Compatibility](reference/compatibility.md).

## Are Python imports a supported API?

No. For **v0.1.0a8**, the supported public interface is the three CLIs and their
configuration, data, and artifact contracts. See the [Home](index.md) page and
[Compatibility](reference/compatibility.md).
