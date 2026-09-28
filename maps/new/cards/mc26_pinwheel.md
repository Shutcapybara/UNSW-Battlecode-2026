# Winding shelves
**NEW THIS EXPANSION · plausibility 0.85 · sampling weight 5.8621%**

[Map](../mc26_pinwheel.map) · [Preview](../previews/mc26_pinwheel.png) · [Full suite](../EXPLAINER.md)

Two mirrored bent walls create longer sheltered approaches and a contested inner turn without a closed trap.

Plausibility rationale: Bent shelves, broad openings and interior food support sheltered and direct approaches.
Limitation: Long bodies can still congest the turns; the first closed-basin draft was repaired before play.

Family: `mc26_pinwheel`. Conservative split group: `loops_and_detours`. Related designs must remain in the same dataset partition.

Structure: 34×30; 54 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 27 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'10:30': 12, '4:20': 18, '8:24': 24}`. Expected scheduled attempts by tick 500: 1777.98; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 198–237 rounds. Median combined bed harvest 302.5; median splits 151.0; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'valjean-v01-portal-memory', 'side': 'A'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_04_mc26_pinwheel_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json`) | fafnir-v01-phalanx | valjean-v01-portal-memory | A | 198 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_04_mc26_pinwheel_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json`) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 237 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `0853b27480020bbeafb4b7104fbd02e8646ad44cf947fad39fbefcfa41bf7551`.
