# FAQ

## Do I need a GPU?

Yes. All three CLIs require CUDA at runtime and exit if no CUDA device is
available.

## Why does tune_model insist on CUDA_VISIBLE_DEVICES?

Each W&B agent worker is pinned to one device token from that variable. The
token list must be non-empty, comma-separated, and free of duplicates. If you
pass `--num-agents`, it must equal the token count.

## Can I use ConvEncoder or ClassPredictor as the top-level model_type?

No. In **0.1.0a2** only `EncoderPredictor` is a top-level CLI model type.
`ConvEncoder` and `ClassPredictor` are nestable components inside
`model_config`.

## Where do prediction files go?

Under `--opath`, named:

```text
{job_name}.{encoder_predictor_model_name}.{head_model_name}.pred_class.npy
```

## Is there a PyPI package?

Not for this alpha. Install from the `v0.1.0a2` git tag as described in
[Install](install.md).
