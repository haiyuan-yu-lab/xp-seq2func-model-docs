# Multi-source data workflow

Combine multiple one-hot sequence sources across training, tuning, and
prediction in **v0.1.0a9**.

This workflow page shows command shapes and complete text-only JSON examples.
Canonical nesting, source identity, sampler behavior, and cross-source
invariants live on [Multi-source](../data/multi-source.md). Array and label
geometry: [Arrays](../data/arrays.md), [Labels](../data/labels.md). CLI flag
contracts: [`train_model`](../cli/train_model.md),
[`tune_model`](../cli/tune_model.md), [`pred_model`](../cli/pred_model.md).

## Checklist

1. Choose source order; keep that order identical on every path field
2. Ensure every OHE source shares one sequence length `L`
3. Align per-source row counts `N_s` across OHE, labels, and optional masks
4. Set `source_fracs` to length `S` (use `[1]` when `S = 1`)
5. Use `shuffle: true` on train when mixture reweighting is desired; use
   `shuffle: false` on val/test for full-draw / deterministic concat order
6. On train/val, supply every declared prediction head for **all** sources
7. On prediction, omit labels for unlabeled inference; never put `mask_npy` on
   `test_data`

## Train with two sources

Placeholder paths only. Pair with a complete hparams document from
[Hyperparameters](../configuration/hyperparameters.md).

<!-- schema: schemas/v0.1.0a9/train-config.schema.json -->
```json
{
  "model_type": "EncoderPredictor",
  "model_config": {
    "model_name": "ep_main",
    "embedding_trimming": 0,
    "encoder": {
      "model_type": "ConvEncoder",
      "model_config": { "model_name": "enc" }
    },
    "predictor": {
      "cls": {
        "model_type": "ClassPredictor",
        "model_config": { "model_name": "cls_head", "n_class": 2 }
      },
      "reg": {
        "model_type": "RegressPredictor",
        "model_config": { "model_name": "reg_head" }
      },
      "prof": {
        "model_type": "ProfilePredictor",
        "model_config": {
          "model_name": "prof_head",
          "track_names": ["signal"],
          "bin_size": 1
        }
      }
    }
  },
  "train_data": {
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
    "num_workers": 0,
    "pin_memory": true,
    "source_fracs": [0.7, 0.3]
  },
  "val_data": {
    "encoder": {
      "ohe_npy": [
        "/path/to/src0_val_ohe.npy",
        "/path/to/src1_val_ohe.npy"
      ],
      "label": null
    },
    "predictor": {
      "cls": {
        "label_npy": [
          "/path/to/src0_val_cls_labels.npy",
          "/path/to/src1_val_cls_labels.npy"
        ]
      },
      "reg": {
        "label_npy": [
          "/path/to/src0_val_reg_labels.npy",
          "/path/to/src1_val_reg_labels.npy"
        ]
      },
      "prof": {
        "profile_npy": [
          "/path/to/src0_val_profile.npy",
          "/path/to/src1_val_profile.npy"
        ],
        "count_npy": [
          "/path/to/src0_val_count.npy",
          "/path/to/src1_val_count.npy"
        ]
      }
    },
    "shuffle": false,
    "num_workers": 0,
    "pin_memory": true,
    "source_fracs": [0.5, 0.5]
  },
  "job_name": "demo_multi_train",
  "random_seed": 0,
  "max_epochs": 20,
  "early_stopping": { "grace_epochs": 5 },
  "wandb": {
    "project": "seq2func-train",
    "mode": "disabled"
  }
}
```

```bash
train_model \
  --config /path/to/train_multi.json \
  --hparams /path/to/hparams.json \
  --opath /path/to/out \
  --verbosity 1
```

## Tune with the same multi-source splits

Tune configs reuse the train/val split contract. Pair with a tune-space from
[Tuning spaces](../configuration/tuning-spaces.md). Do not put data paths in
the tune-space file.

<!-- schema: schemas/v0.1.0a9/tune-config.schema.json -->
```json
{
  "model_type": "EncoderPredictor",
  "model_config": {
    "model_name": "ep_main",
    "embedding_trimming": 0,
    "encoder": {
      "model_type": "ConvEncoder",
      "model_config": { "model_name": "enc" }
    },
    "predictor": {
      "cls": {
        "model_type": "ClassPredictor",
        "model_config": { "model_name": "cls_head", "n_class": 2 }
      },
      "reg": {
        "model_type": "RegressPredictor",
        "model_config": { "model_name": "reg_head" }
      }
    }
  },
  "train_data": {
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
      }
    },
    "shuffle": true,
    "num_workers": 0,
    "pin_memory": true,
    "source_fracs": [0.6, 0.4]
  },
  "val_data": {
    "encoder": {
      "ohe_npy": [
        "/path/to/src0_val_ohe.npy",
        "/path/to/src1_val_ohe.npy"
      ],
      "label": null
    },
    "predictor": {
      "cls": {
        "label_npy": [
          "/path/to/src0_val_cls_labels.npy",
          "/path/to/src1_val_cls_labels.npy"
        ]
      },
      "reg": {
        "label_npy": [
          "/path/to/src0_val_reg_labels.npy",
          "/path/to/src1_val_reg_labels.npy"
        ]
      }
    },
    "shuffle": false,
    "num_workers": 0,
    "pin_memory": true,
    "source_fracs": [0.5, 0.5]
  },
  "random_seed": 0,
  "max_epochs": 20,
  "early_stopping": { "grace_epochs": 5 },
  "wandb": {
    "project": "seq2func-tune",
    "mode": "online",
    "sweep_name": "demo-multi-sweep"
  }
}
```

```bash
export CUDA_VISIBLE_DEVICES=0
tune_model \
  --config /path/to/tune_multi.json \
  --tune-space /path/to/tune_space.json \
  --opath /path/to/out \
  --verbosity 1
```

## Predict over concatenated sources

Unlabeled multi-source prediction. Output rows follow source list order when
`shuffle` is `false`. Artifact filenames:
[Predictions](../artifacts/predictions.md).

<!-- schema: schemas/v0.1.0a9/pred-config.schema.json -->
```json
{
  "model_type": "EncoderPredictor",
  "model_config": {
    "model_name": "ep_main",
    "embedding_trimming": 0,
    "encoder": {
      "model_type": "ConvEncoder",
      "model_config": { "model_name": "enc" }
    },
    "predictor": {
      "cls": {
        "model_type": "ClassPredictor",
        "model_config": { "model_name": "cls_head", "n_class": 2 }
      },
      "reg": {
        "model_type": "RegressPredictor",
        "model_config": { "model_name": "reg_head" }
      },
      "prof": {
        "model_type": "ProfilePredictor",
        "model_config": {
          "model_name": "prof_head",
          "track_names": ["signal"],
          "bin_size": 1
        }
      }
    }
  },
  "test_data": {
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
  },
  "job_name": "demo_multi_pred",
  "random_seed": 0
}
```

```bash
pred_model \
  --config /path/to/pred_multi.json \
  --hparams /path/to/out/demo_multi_train.ep_main.hparam.json \
  --checkpoint /path/to/out/demo_multi_train.ep_main.pth \
  --opath /path/to/pred_out \
  --verbosity 1
```

## Related pages

- [Multi-source](../data/multi-source.md)
- [Splits](../data/splits.md)
- [Train configuration](../configuration/train.md)
- [Tune configuration](../configuration/tune.md)
- [Prediction configuration](../configuration/prediction.md)
- [Train to predict](train-to-predict.md)
- [Schemas](../reference/schemas.md)
