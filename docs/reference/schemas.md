# Schemas

Documentation-owned JSON Schema snapshots for exact release **v0.1.0a8**.

These files live under `schemas/v0.1.0a8/` on this site. They are **not**
canonical runtime definitions. Runtime validators in the installed package
remain authoritative for filesystem properties, array contents, and other
behavior JSON Schema cannot express.

## Draft and identifiers

- JSON Schema Draft **2020-12**
- Stable `$id` values under
  `https://haiyuan-yu-lab.github.io/xp-seq2func-model-docs/schemas/v0.1.0a8/`
- Reusable shared definitions in `defs.schema.json`

## Available snapshots

| Schema | Purpose |
| --- | --- |
| [`defs.schema.json`](../schemas/v0.1.0a8/defs.schema.json) | Reusable `$defs` for paths, numbers, and strings |
| [`init-checkpoint.schema.json`](../schemas/v0.1.0a8/init-checkpoint.schema.json) | Optional train/tune `init_checkpoint` object |

Additional public JSON surfaces will receive snapshots in later documentation
slices.

## Example association convention

Complete inline JSON examples in Markdown may declare their schema with an HTML
comment immediately before a fenced `json` block. The comment path is relative
to the MkDocs `docs/` directory, for example:

`<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->`

Docs-only checks validate those complete examples structurally. Illustrative
fragments omit the comment and are skipped.

## Example: init_checkpoint

<!-- schema: schemas/v0.1.0a8/init-checkpoint.schema.json -->
```json
{
  "path": "/path/to/checkpoint.pth",
  "modules": ["encoder_model_name"]
}
```

See also [Config: init_checkpoint](../config.md#init_checkpoint-train--tune).
