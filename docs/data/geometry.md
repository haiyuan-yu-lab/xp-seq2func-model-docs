# Geometry

Shared geometry rules for sequence length, embedding trimming, and profile bins
in **v0.1.0a8**.

- Embedding trimming shortens the retained encoder embedding by an integer ≥ 0
- Profile **bin_size** must divide the retained embedding length exactly
- Profile outputs use track count `T` and bin count `P`

See [Profiles](../profiles.md) and [Model composition](../models/composition.md).

Coming in a later documentation slice: complete geometry equations and examples.
