# Overland causeway
**REUSED PRIOR SYNTHETIC · plausibility 0.90 · sampling weight 3.1034%**

[Map](../md26_causeway_detour_s0.map) · [Preview](../previews/md26_causeway_detour_s0.png) · [Full suite](../EXPLAINER.md)

Overland causeway; prior map card and full evidence retained in the preceding batch.

Plausibility rationale: A coherent divider and several overland passages create meaningful route choices.
Limitation: Prior side and orientation sensitivity remains unresolved.

Family: `md26_causeway`. Conservative split group: `portal_shortcuts_and_dividers`. Related designs must remain in the same dataset partition.

Structure: 32×24; 42 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 33 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'10:30': 24, '3:11': 18}`. Expected scheduled attempts by tick 500: 1868.92; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 6 fixtures (0 new, 6 reused), 153–282 rounds. Median combined bed harvest 252.5; median splits 129.0; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'ouroboros-v13-ladder', 'side': 'A'}, {'opponent': 'valjean-v01-portal-memory', 'side': 'A'}, {'opponent': 'von_neumann-x06-info', 'side': 'A'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `quarantined_control`. Prior balance notes: Quarantined matched control: A wins all six direct games across three side-swapped opponent pairs, while its second layout and horizontal reflection favor B. This triggers the frozen practical bias warning. Keep for diagnosing initiative/geometry sensitivity; no default training weight.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/024_md26_causeway_detour_s0_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json`) | fafnir-v01-phalanx | ouroboros-v13-ladder | A | 282 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/025_md26_causeway_detour_s0_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json`) | ouroboros-v13-ladder | fafnir-v01-phalanx | A | 220 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/026_md26_causeway_detour_s0_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json`) | fafnir-v01-phalanx | valjean-v01-portal-memory | A | 195 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/027_md26_causeway_detour_s0_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json`) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 217 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/028_md26_causeway_detour_s0_fafnir-v01-phalanx_vs_von_neumann-x06-info.json`) | fafnir-v01-phalanx | von_neumann-x06-info | A | 160 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/030_md26_causeway_detour_s0_von_neumann-x06-info_vs_fafnir-v01-phalanx.json`) | von_neumann-x06-info | fafnir-v01-phalanx | A | 153 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `b456bc59c49b6da25e4d63f5ccd18f114c7b0213941125dc7e19a284cbf7e397`.
