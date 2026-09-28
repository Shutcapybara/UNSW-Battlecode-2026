# Four-district crossroads
**NEW THIS EXPANSION · plausibility 0.89 · sampling weight 6.1379%**

[Map](../mc26_crossroads.map) · [Preview](../previews/mc26_crossroads.png) · [Full suite](../EXPLAINER.md)

Four porous resource districts connect through a broad cross-shaped junction and an outer route.

Plausibility rationale: Porous districts, a central junction and an outer route offer contest, retreat and flanking.
Limitation: Several rooms share one visual grammar, so this is related to the orchard family.

Family: `mc26_crossroads`. Conservative split group: `productive_rooms_and_deployment`. Related designs must remain in the same dataset partition.

Structure: 32×32; 48 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 25 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'3:15': 12, '6:24': 36}`. Expected scheduled attempts by tick 500: 1847.97; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 109–309 rounds. Median combined bed harvest 262.0; median splits 126.5; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_03_mc26_crossroads_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json`) | fafnir-v01-phalanx | ouroboros-v13-ladder | A | 109 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_03_mc26_crossroads_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json`) | ouroboros-v13-ladder | fafnir-v01-phalanx | B | 309 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `b394dc8a52bf51c8430ebb4062630532bbe7899f6747806c0f9241664e7d0c1f`.
