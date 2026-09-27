# Wrapped resource belt
**NEW THIS EXPANSION · plausibility 0.85 · sampling weight 5.8621%**

[Map](../mc26_equatorial_belt.map) · [Preview](../previews/mc26_equatorial_belt.png) · [Full suite](../EXPLAINER.md)

A renewable belt wraps across the horizontal seam, with staggered openings from the outer water.

Plausibility rationale: A continuous food belt and staggered gates make both wrapping and access choice purposeful.
Limitation: A repeated band is more stylized than natural basins; wrapping is not itself strategic novelty.

Family: `mc26_equatorial_belt`. Conservative split group: `wrapped_contact`. Related designs must remain in the same dataset partition.

Structure: 40×20; 172 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 7 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'20:60': 12, '8:24': 160}`. Expected scheduled attempts by tick 500: 5077.18; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 83–245 rounds. Median combined bed harvest 656.0; median splits 283.5; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_05_mc26_equatorial_belt_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json) | fafnir-v01-phalanx | ouroboros-v13-ladder | A | 245 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_05_mc26_equatorial_belt_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json) | ouroboros-v13-ladder | fafnir-v01-phalanx | B | 83 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `76e7c9ffd6502bd2b3f38091d303f656d2ba06fb774d15c3c6ea1d1f4865f3f9`.
