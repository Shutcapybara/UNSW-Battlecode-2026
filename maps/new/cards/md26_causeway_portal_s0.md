# Portal causeway
**REUSED PRIOR SYNTHETIC · plausibility 0.92 · sampling weight 3.1724%**

[Map](../md26_causeway_portal_s0.map) · [Preview](../previews/md26_causeway_portal_s0.png) · [Full suite](../EXPLAINER.md)

Portal causeway; prior map card and full evidence retained in the preceding batch.

Plausibility rationale: Useful paired shortcuts coexist with ordinary routes and food on both sides.
Limitation: Shortcut benefit is established structurally; safe commitment remains policy dependent.

Family: `md26_causeway`. Conservative split group: `portal_shortcuts_and_dividers`. Related designs must remain in the same dataset partition.

Structure: 32×24; 42 active beds; 2 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 12 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'10:30': 24, '3:11': 18}`. Expected scheduled attempts by tick 500: 1868.92; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 6 fixtures (0 new, 6 reused), 179–500 rounds. Median combined bed harvest 408.0; median splits 246.5; total portal crossings 394.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `accepted`. Prior balance notes: All portal pairs carry real traffic; the shortcut saves 11.524 mean terrain steps from initial heads to beds and ordinary alternatives remain. Each direct opponent beats Fafnir on both sides, including the held-back policy; the same screening winners recur on the second layout and reflection. This supports comparable opportunity, not a 50:50 target or proof of portal-memory activation.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/032_md26_causeway_portal_s0_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json`) | fafnir-v01-phalanx | ouroboros-v13-ladder | B | 393 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/033_md26_causeway_portal_s0_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json`) | ouroboros-v13-ladder | fafnir-v01-phalanx | A | 247 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/034_md26_causeway_portal_s0_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json`) | fafnir-v01-phalanx | valjean-v01-portal-memory | B | 500 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/035_md26_causeway_portal_s0_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json`) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 266 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/036_md26_causeway_portal_s0_fafnir-v01-phalanx_vs_von_neumann-x06-info.json`) | fafnir-v01-phalanx | von_neumann-x06-info | B | 298 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/038_md26_causeway_portal_s0_von_neumann-x06-info_vs_fafnir-v01-phalanx.json`) | von_neumann-x06-info | fafnir-v01-phalanx | A | 179 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `00e7e652f5602503e3cbbdcdcbb94e76a4ef091e48b6fc125c673ea82ac8c4b2`.
