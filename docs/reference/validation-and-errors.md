# Validation and errors

How **v0.1.0a8** commands respond to invalid inputs.

## Fail-closed behavior

The CLIs reject unsupported configuration keys, malformed JSON, incompatible
array shapes, and other contract violations before producing misleading
artifacts. Prefer fixing the rejected condition over relying on partial
outputs.

Exact exception text and stack traces are **not** a stability contract. Use
the condition descriptions on contract pages and `--verbosity` output for
diagnosis.

## Affected surfaces

| Surface | Typical rejection causes |
| --- | --- |
| CLI flags | Missing required flags, invalid combinations, bad verbosity |
| Config JSON | Unknown keys, forbidden keys, type or range violations |
| Data arrays | Shape, dtype, alignment, or value-domain failures |
| Checkpoints | Missing modules, incompatible state keys or shapes |
| Attribution | Invalid target syntax, profile models without an explicit target |

## Exit outcomes

Failed validation exits non-zero. Successful runs exit zero after writing the
expected artifacts under `--opath`.

## Related pages

- [FAQ](../faq.md)
- [Compatibility](compatibility.md)
- [Schemas](schemas.md)

!!! note "Later slices"
    Per-contract rejection tables expand in later documentation slices.
