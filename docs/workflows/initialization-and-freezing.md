# Initialization and freezing

Warm-start selected modules from a checkpoint and freeze or fine-tune them
during `train_model` or `tune_model` in **v0.1.0a8**.

Placeholder paths only. This documentation does not ship checkpoints and does
not open `.pth` files during docs checks.

## Who supports what

| Surface | Checkpoint init | Notes |
| --- | --- | --- |
| `train_model` | Optional config `init_checkpoint` | Loads listed modules before training |
| `tune_model` | Optional config `init_checkpoint` | Same object applied at the start of **every** trial |
| `pred_model` | **Forbidden** | Uses `--checkpoint` for a full parent restore instead |

`init_checkpoint` belongs on the train or tune config JSON only. It is not a
CLI flag, not allowed on prediction configs, and not allowed under
`model_config`, data blocks, hparams, or the tune-space file.

Object shape and schema snapshot:
[Config: init_checkpoint](../config.md#init_checkpoint-train--tune),
[init-checkpoint.schema.json](../schemas/v0.1.0a8/init-checkpoint.schema.json).

## Selectable modules

| Rule | Behavior |
| --- | --- |
| Names | Catalogued `model_name` values from the composition tree |
| Not map keys | Predictor map keys (for example `"cls"`) are **not** module names |
| List | Non-empty; unique strings; required when `init_checkpoint` is present |
| Authoritative | The config `modules` list decides what loads; the checkpoint is cross-checked only |
| Path | Parent or child checkpoint `.pth` (`seq2func_ckpt_v2` or compatible legacy `seq2func_ckpt_v1`) that contains `states` for every listed name |
| Unlisted | Modules not named in `modules` keep post-construction (random) init |

Catalogued names cover the top-level `EncoderPredictor`, the nested encoder,
and each prediction head. Internal profile branches are not separately
catalogued; loading or freezing a `ProfilePredictor` `model_name` covers both
branches. See [Model composition](../models/composition.md) and
[Checkpoints](../artifacts/checkpoints.md).

## Selective init vs full restore

| Mechanism | Command | What loads | Optimizer / resume |
| --- | --- | --- | --- |
| `init_checkpoint` | `train_model` / `tune_model` | Only listed catalogued modules | Fresh Adam; **no** optimizer-state resume in this release |
| `--checkpoint` | `pred_model` | Full parent checkpoint restore for inference | No training / no optimizer |

Selective initialization is **not** an ordinary training resume and is **not**
the prediction full-restore path. Omitting `init_checkpoint` leaves every
module at post-construction initialization.

Typed v2 checkpoints may initialize compatible scalar heads across ordinary and
RC-aware counterparts (`ClassPredictor` ↔ `RCClassPredictor`,
`RegressPredictor` ↔ `RCRegressPredictor`). The target module keeps its own
`model_type` and forward behavior; profile ↔ RC profile init remains rejected.
See [Checkpoints: scalar counterpart init](../artifacts/checkpoints.md#v2-scalar-counterpart-init-traintune-only).

## Validation and failure conditions

Described without stabilizing exact exception text:

| Condition | Outcome |
| --- | --- |
| Missing / unreadable `path` | Fail closed |
| Payload not a supported checkpoint dict (`seq2func_ckpt_v2` or compatible legacy `seq2func_ckpt_v1`) | Fail closed |
| v1 checkpoint into a target tree with an RC-aware predictor head | Fail closed |
| v2 `model_type` mismatch for a listed module | Fail closed, except v2 scalar counterpart init pairs (`ClassPredictor` ↔ `RCClassPredictor`, `RegressPredictor` ↔ `RCRegressPredictor`) with compatible tensors and architecture |
| v2 profile ↔ RC profile init for a listed module | Fail closed even when public shapes match |
| Empty `modules`, duplicates, or unknown `model_name` | Fail closed |
| Listed name missing from checkpoint `states` | Fail closed |
| Tensor key / shape mismatch for a listed module | Fail closed |
| Extra `states` keys not listed in `modules` | Ignored |
| Top-level `learning_rate` ≤ 0 | Fail closed (hparams / draw validation) |
| Every trainable module frozen (`learning_rate: 0`) | Fail closed when Adam is built |
| `init_checkpoint` on a prediction config | Forbidden key |
| Tune: same init object after a trial draw | Shape/name mismatch fails that trial load |

## Inheritance and learning rates

Canonical contracts (do not duplicate the full tables here):

- [Hyperparameters](../configuration/hyperparameters.md) — inheritance fill,
  top-level vs nested rates, freezing, Adam
- [Concepts: learning rates and freezing](../concepts.md#learning-rates-and-freezing)

Summary for this workflow:

| Location | Allowed | Effect of `0` |
| --- | --- | --- |
| Top-level `learning_rate` | number **> 0** | Not allowed |
| Nested encoder `learning_rate` | number ≥ 0 | Freezes that encoder; omitted from Adam |
| Nested head `predictor_config.learning_rate` | number ≥ 0 | Freezes that head; omitted from Adam |
| `ProfilePredictor` freeze | nested rate `0` | Freezes **both** profile and count branches |

Missing nested `batch_size`, `learning_rate`, and `n_channels` inherit from the
parent. Present child objects replace; they do not deep-merge. Distinct positive
rates become separate Adam parameter groups. Adam kwargs beyond learning rate
are fixed; there is no top-level `optimizer` or scheduler control in this
release.

## Train examples

Assume a composition whose catalogued names are `ep_main`, `enc`, `cls_head`,
and `reg_head`. CLI:

```bash
train_model \
  --config /path/to/train.json \
  --hparams /path/to/hparams.json \
  --opath /path/to/out \
  --verbosity 1
```

### Warm start (load, keep training)

Train-config fragment:

<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->
```json
{
  "path": "/path/to/prior.ep_main.pth",
  "modules": ["enc", "cls_head", "reg_head"]
}
```

Place that object under `"init_checkpoint"` on the train config. Hparams keep a
positive top-level `learning_rate` and omit nested rates so every loaded module
continues training.

### Selective initialization

Load only the encoder; heads stay randomly initialized:

<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->
```json
{
  "path": "/path/to/prior.enc.pth",
  "modules": ["enc"]
}
```

`path` may point at the parent `.pth` or the child `enc` artifact as long as
`states` contains `enc`.

### Freeze after init

Same selective `init_checkpoint` as above, plus nested freeze in hparams:

<!-- schema: schemas/v0.1.0a8/encoder-predictor-hparams.schema.json -->
```json
{
  "batch_size": 32,
  "learning_rate": 0.001,
  "n_channels": 16,
  "encoder": {
    "n_layers": 2,
    "kernel_size": 5,
    "dilation": [1, 2],
    "learning_rate": 0
  },
  "predictor": {
    "cls": {
      "alpha": 1,
      "loss": { "type": "categorical_cross_entropy", "params": {} },
      "predictor_config": {
        "n_fc_layers": 2,
        "fc_hidden_dims": [64],
        "dropout": 0.1,
        "activation": "gelu",
        "pooling_methods": "GAP"
      }
    },
    "reg": {
      "alpha": 1,
      "loss": { "type": "mse", "params": {} },
      "predictor_config": {
        "n_fc_layers": 1,
        "fc_hidden_dims": [],
        "dropout": 0.0,
        "activation": "relu",
        "pooling_methods": "GMP"
      }
    }
  }
}
```

The encoder loads from the checkpoint and stays frozen; heads train at the
inherited top-level rate. Full inheritance / freeze rules:
[Hyperparameters](../configuration/hyperparameters.md).

### Fine-tuning with distinct rates

Initialize the encoder, keep it trainable at a lower rate, and train heads at
the top-level rate:

Train-config `init_checkpoint`:

<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->
```json
{
  "path": "/path/to/prior.ep_main.pth",
  "modules": ["enc"]
}
```

Hparams override (illustrative nested rates):

```json
{
  "learning_rate": 0.001,
  "encoder": {
    "learning_rate": 0.0001
  }
}
```

(Other required hparam keys omitted here; see the complete example on
[Hyperparameters](../configuration/hyperparameters.md).)

## Tune examples

Put the same `init_checkpoint` object on the **tune config** (not the
tune-space). Every trial applies that object after its hparam draw.

```bash
export CUDA_VISIBLE_DEVICES=0
tune_model \
  --config /path/to/tune.json \
  --tune-space /path/to/tune_space.json \
  --opath /path/to/tune_out \
  --max-trials 20 \
  --verbosity 1
```

### Warm start every trial

Tune-config fragment (same schema as train):

<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->
```json
{
  "path": "/path/to/prior.ep_main.pth",
  "modules": ["enc"]
}
```

### Freeze or fine-tune via the tune-space

Nested learning-rate leaves may fix or sample `0` (freeze) or positive rates
(fine-tune). Top-level `learning_rate` leaves must stay **> 0** for every
allowed draw. Canonical envelope:
[Tuning spaces](../configuration/tuning-spaces.md).

Illustrative encoder freeze leaf:

```json
{
  "encoder": {
    "learning_rate": { "value": 0 }
  }
}
```

## What this release does not provide

- Prediction-time `init_checkpoint` (use `pred_model --checkpoint` for full
  restore)
- Optimizer-state or scheduler resume / checkpoint continuation
- Configurable optimizer algorithms or scheduler objects beyond nested
  learning rates (Adam is fixed)

## Related pages

- [Config: init_checkpoint](../config.md#init_checkpoint-train--tune)
- [Hyperparameters](../configuration/hyperparameters.md)
- [Checkpoints](../artifacts/checkpoints.md)
- [Train configuration](../configuration/train.md) /
  [Tune configuration](../configuration/tune.md)
- [Tuning workflow](tuning.md)
- [Train to predict](train-to-predict.md)
