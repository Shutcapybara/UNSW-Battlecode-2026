# Seam market
**NEW THIS EXPANSION · plausibility 0.88 · sampling weight 6.0690%**

[Map](../mc26_seam_market.map) · [Preview](../previews/mc26_seam_market.png) · [Full suite](../EXPLAINER.md)

On a wide horizontal cylinder, meaningful food and contact lie across the wrap seam rather than the visual centre.

Plausibility rationale: Food near the horizontal seam makes short contact on a wide map meaningful.
Limitation: Boundary awareness may dominate weak navigation policies; the visual center is misleading by design.

Family: `mc26_seam_market`. Conservative split group: `wrapped_contact`. Related designs must remain in the same dataset partition.

Structure: 44×24; 54 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 7 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'18:42': 24, '4:16': 30}`. Expected scheduled attempts by tick 500: 1877.69; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 95–101 rounds. Median combined bed harvest 177.5; median splits 90.0; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'valjean-v01-portal-memory', 'side': 'B'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_06_mc26_seam_market_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json) | fafnir-v01-phalanx | valjean-v01-portal-memory | B | 101 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_06_mc26_seam_market_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json) | valjean-v01-portal-memory | fafnir-v01-phalanx | B | 95 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `7a194752b2615b1ae5e1dc5f085b32573e0c4e0aa8e1b0c5fbe51b0f909f9b7a`.
