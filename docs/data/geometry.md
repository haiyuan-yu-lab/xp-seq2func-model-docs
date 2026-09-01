# Geometry

Shared geometry rules for sequence length, embedding trimming, and profile bins
in **v0.1.0a8**.

- Embedding trimming `T` shortens each end of the encoder embedding; retained
  length is `L_embed = L - 2T` and must be `> 0`
- All prediction heads share that trimmed embedding
- Profile **bin_size** must divide `L_embed` exactly
- Profile outputs use track count `T` and bin count `P`

See [Model composition](../models/composition.md) and
[Profiles](../profiles.md).
