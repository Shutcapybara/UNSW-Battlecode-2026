# Wide orchard
**REUSED PRIOR SYNTHETIC · plausibility 0.90 · sampling weight 3.1034%**

[Map](../md26_orchard_wide_s0.map) · [Preview](../previews/md26_orchard_wide_s0.png) · [Full suite](../EXPLAINER.md)

Wide orchard; prior map card and full evidence retained in the preceding batch.

Plausibility rationale: Wider room exits give readable escape and split space with the same productive footprint.
Limitation: The old orientation and side results do not establish fair outcomes.

Family: `md26_orchard`. Conservative split group: `productive_rooms_and_deployment`. Related designs must remain in the same dataset partition.

Structure: 30×24; 58 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 27 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'12:36': 8, '4:16': 50}`. Expected scheduled attempts by tick 500: 2644.19; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 6 fixtures (0 new, 6 reused), 429–500 rounds. Median combined bed harvest 863.5; median splits 514.0; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'ouroboros-v13-ladder', 'side': 'A'}, {'opponent': 'valjean-v01-portal-memory', 'side': 'A'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `quarantined_control`. Prior balance notes: Productive rooms and repeated entrance/exit traffic are confirmed on both layouts. Fairness/robustness remains below the 4/5 inclusion requirement: strong side sweeps recur in sibling/reflection controls. One reflected game eliminates a side at round 33, versus 429–500 rounds on the primary. This is not an initial forced death, but the large sensitivity needs explanation. Retain as a provisional diagnostic control, not accepted training material.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/056_md26_orchard_wide_s0_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json) | fafnir-v01-phalanx | ouroboros-v13-ladder | A | 429 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/057_md26_orchard_wide_s0_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json) | ouroboros-v13-ladder | fafnir-v01-phalanx | A | 500 | False |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/058_md26_orchard_wide_s0_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json) | fafnir-v01-phalanx | valjean-v01-portal-memory | A | 500 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/059_md26_orchard_wide_s0_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 465 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/060_md26_orchard_wide_s0_fafnir-v01-phalanx_vs_von_neumann-x06-info.json) | fafnir-v01-phalanx | von_neumann-x06-info | A | 500 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/062_md26_orchard_wide_s0_von_neumann-x06-info_vs_fafnir-v01-phalanx.json) | von_neumann-x06-info | fafnir-v01-phalanx | B | 500 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `0d3570a2c9dc2b70c0cd282bb4ae1f669fa9c9fb7d535687ce72285d62ed693b`.
