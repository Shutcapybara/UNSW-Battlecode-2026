# Far harbors
**NEW THIS EXPANSION · plausibility 0.89 · sampling weight 6.1379%**

[Map](../mc26_far_harbors.map) · [Preview](../previews/mc26_far_harbors.png) · [Full suite](../EXPLAINER.md)

Six starting dragons explore several separated harbors in a broad sea; modest departure supply supports the trip.

Plausibility rationale: Six starts, departure food and separated harbors give a coherent larger navigation problem.
Limitation: This is a recombination of established large-map and distributed-income ideas, not a wholly new mechanic.

Family: `mc26_far_harbors`. Conservative split group: `open_navigation`. Related designs must remain in the same dataset partition.

Structure: 48×36; 100 active beds; 0 portal pairs; 6 starting dragons, lengths [4, 4, 4, 4, 4, 4]. Nearest opposing heads: 39 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'10:30': 12, '10:34': 88}`. Expected scheduled attempts by tick 500: 2257.58; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 500–500 rounds. Median combined bed harvest 965.0; median splits 413.5; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'valjean-v01-portal-memory', 'side': 'B'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_12_mc26_far_harbors_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json) | fafnir-v01-phalanx | valjean-v01-portal-memory | B | 500 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_12_mc26_far_harbors_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json) | valjean-v01-portal-memory | fafnir-v01-phalanx | B | 500 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `27b079a28af75391bf41c61cf38412f253c8d5ad2d1c216efcfa6bb328b56aff`.
