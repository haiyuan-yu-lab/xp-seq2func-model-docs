# FAQ

## Do I need a GPU?

Yes. All three CLIs require CUDA at runtime and exit if no CUDA device is
available.

## Why does tune_model insist on CUDA_VISIBLE_DEVICES?

Each W&B agent worker is pinned to one device token from that variable. The
token list must be non-empty, comma-separated, and free of duplicates. If you
pass `--num-agents`, it must equal the token count.

## Can I use ConvEncoder, ConvSelfAttEncoder, ClassPredictor, or RegressPredictor as the top-level model_type?

No. In **0.1.0a6** only `EncoderPredictor` is a top-level CLI model type.
`ConvEncoder`, `ConvSelfAttEncoder`, `ClassPredictor`, and `RegressPredictor`
are nestable components inside `model_config`.

## Where do prediction files go?

Under `--opath`, named by head type:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred_class.npy
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred.npy
```

(`ClassPredictor` → `.pred_class.npy`; `RegressPredictor` → `.pred.npy`.)

With `--attribution METHOD`, also:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.attr_{METHOD}.npy
```

Add `--attribution-target` to select one `ClassPredictor` scalar (probability,
logit, logit-difference, or predicted logit) and write a single target-qualified
`attr_*.npy` instead. See [pred_model](cli/pred_model.md).

## Can I freeze an encoder or head during training?

Yes. Set that module's nested `learning_rate` to `0` in hparams (or in the
tune-space leaf for that path). The module's parameters are frozen and left
out of Adam. Top-level `learning_rate` must remain `> 0`. See
[Concepts](concepts.md#learning-rates-and-freezing).

## Can I initialize from a pretrained encoder (or other module)?

Yes. On the train or tune config, set optional `init_checkpoint` with `path`
(to a `.pth`) and `modules` (catalogued `model_name` strings to load). Other
modules stay randomly initialized. Combine with nested `learning_rate: 0` to
freeze the loaded modules. See
[Config](config.md#init_checkpoint-train--tune).

## Is there a PyPI package?

Not for this alpha. Install from the `v0.1.0a6` git tag as described in
[Install](install.md).
