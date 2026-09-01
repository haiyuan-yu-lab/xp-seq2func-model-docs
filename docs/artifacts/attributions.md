# Attributions

Attribution array artifacts from `pred_model` in **v0.1.0a8**.

Attribution is optional. Enable with `--attribution {ig,saliency,deepshap}`.
Add `--attribution-target` for one explicit scalar target (required when any
`ProfilePredictor` head is present). Arrays are float32 shaped `(N, 4, L)`.

| Mode | Typical filename |
| --- | --- |
| Legacy (no target) | `{job}.{ep}.{head}.attr_{method}.npy` |
| Explicit target | `{job}.{ep}.{head}.attr_{method}.<target-qualifier>.npy` |

Flag summary and target forms: [pred_model](../cli/pred_model.md). Deep
attribution targeting, domains, and filename grammar:
[Attribution workflow](../workflows/attribution.md).
