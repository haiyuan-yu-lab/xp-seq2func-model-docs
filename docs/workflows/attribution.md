# Attribution workflow

Interpret model outputs with Captum attribution in **v0.1.0a8**.

- Enable with `pred_model --attribution METHOD`
- Prefer an explicit `--attribution-target` so every row shares one
  **attribution target** and **output domain**
- Legacy **predicted-class attribution** selects a class per row and is not one
  shared target across the array
- Models that include a profile prediction head require an explicit target

See [pred_model](../cli/pred_model.md), [Profiles](../profiles.md), and
[Attribution artifacts](../artifacts/attributions.md).

Coming in a later documentation slice: full target syntax tables and examples.
