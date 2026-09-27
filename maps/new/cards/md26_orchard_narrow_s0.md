# Narrow orchard
**REUSED PRIOR SYNTHETIC · plausibility 0.88 · sampling weight 3.0345%**

[Map](../md26_orchard_narrow_s0.map) · [Preview](../previews/md26_orchard_narrow_s0.png) · [Full suite](../EXPLAINER.md)

Narrow orchard; prior map card and full evidence retained in the preceding batch.

Plausibility rationale: Productive rooms each have two distinct exits and an open exterior.
Limitation: One-cell exits can congest; prior side sensitivity lowers confidence in balance, not design coherence.

Family: `md26_orchard`. Conservative split group: `productive_rooms_and_deployment`. Related designs must remain in the same dataset partition.

Structure: 30×24; 58 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 27 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'12:36': 8, '4:16': 50}`. Expected scheduled attempts by tick 500: 2644.19; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 6 fixtures (0 new, 6 reused), 426–500 rounds. Median combined bed harvest 827.0; median splits 502.5; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'valjean-v01-portal-memory', 'side': 'A'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `quarantined_control`. Prior balance notes: Productive rooms and repeated entrance/exit traffic are confirmed on both layouts. Fairness/robustness remains below the 4/5 inclusion requirement: strong side sweeps recur in sibling/reflection controls. The reflected pair spans 107 and 500 rounds and the narrow second layout is an A sweep. Retain as a provisional diagnostic control, not accepted training material.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/048_md26_orchard_narrow_s0_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json) | fafnir-v01-phalanx | ouroboros-v13-ladder | A | 426 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/049_md26_orchard_narrow_s0_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json) | ouroboros-v13-ladder | fafnir-v01-phalanx | B | 500 | False |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/050_md26_orchard_narrow_s0_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json) | fafnir-v01-phalanx | valjean-v01-portal-memory | A | 500 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/051_md26_orchard_narrow_s0_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 452 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/052_md26_orchard_narrow_s0_fafnir-v01-phalanx_vs_von_neumann-x06-info.json) | fafnir-v01-phalanx | von_neumann-x06-info | B | 500 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/054_md26_orchard_narrow_s0_von_neumann-x06-info_vs_fafnir-v01-phalanx.json) | von_neumann-x06-info | fafnir-v01-phalanx | A | 497 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `3284b8537f1ccea05b7d6bf1e7033ae1bb7a358856ae017a8be4909495f6f6d1`.
