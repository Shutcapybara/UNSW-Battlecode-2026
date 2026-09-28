# Scattered fleets
**NEW THIS EXPANSION · plausibility 0.81 · sampling weight 5.5862%**

[Map](../mc26_scattered_fleets.map) · [Preview](../previews/mc26_scattered_fleets.png) · [Full suite](../EXPLAINER.md)

Each team starts in separated sectors, including a forward group near opposing territory; area is decoupled from local contact.

Plausibility rationale: Mirrored forward groups and rear groups create multiple local fronts on a larger map.
Limitation: Interleaved deployment is a stronger extrapolation and can create strong opening-policy interactions.

Family: `mc26_scattered_fleets`. Conservative split group: `distributed_deployment`. Related designs must remain in the same dataset partition.

Structure: 42×30; 54 active beds; 0 portal pairs; 6 starting dragons, lengths [3, 3, 3, 3, 3, 3]. Nearest opposing heads: 12 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'6:26': 54}`. Expected scheduled attempts by tick 500: 1666.05; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 309–323 rounds. Median combined bed harvest 403.0; median splits 156.5; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_13_mc26_scattered_fleets_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json`) | fafnir-v01-phalanx | ouroboros-v13-ladder | A | 309 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_13_mc26_scattered_fleets_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json`) | ouroboros-v13-ladder | fafnir-v01-phalanx | B | 323 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `175cbcfbefb936e89be4109d54bb95e8b818569fc756155a438325e62135b172`.
