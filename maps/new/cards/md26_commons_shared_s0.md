# Shared commons
**REUSED PRIOR SYNTHETIC · plausibility 0.93 · sampling weight 3.2069%**

[Map](../md26_commons_shared_s0.map) · [Preview](../previews/md26_commons_shared_s0.png) · [Full suite](../EXPLAINER.md)

Shared commons; prior map card and full evidence retained in the preceding batch.

Plausibility rationale: Readable shared supply with broad gates and fallback food; a conservative extension of renewable reference maps.
Limitation: Central control and exit congestion can favor particular approaches.

Family: `md26_commons`. Conservative split group: `resource_geography_timing`. Related designs must remain in the same dataset partition.

Structure: 24×20; 56 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 17 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'20:40': 8, '4:12': 48}`. Expected scheduled attempts by tick 500: 3111.13; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 6 fixtures (0 new, 6 reused), 79–315 rounds. Median combined bed harvest 255.5; median splits 147.5; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'valjean-v01-portal-memory', 'side': 'A'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `accepted`. Prior balance notes: Matched supply with the spread sibling produces a readable renewable contest and many successful splits; actual income and overlap recur on the second layout. Early-contact acceleration is not stable across layouts, so that hypothesis is NOT promoted. A Valjean side sweep and orientation sensitivity remain caveats.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/000_md26_commons_shared_s0_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json) | fafnir-v01-phalanx | ouroboros-v13-ladder | B | 97 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/001_md26_commons_shared_s0_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json) | ouroboros-v13-ladder | fafnir-v01-phalanx | A | 315 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/002_md26_commons_shared_s0_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json) | fafnir-v01-phalanx | valjean-v01-portal-memory | A | 107 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/003_md26_commons_shared_s0_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 79 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/004_md26_commons_shared_s0_fafnir-v01-phalanx_vs_von_neumann-x06-info.json) | fafnir-v01-phalanx | von_neumann-x06-info | B | 163 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/006_md26_commons_shared_s0_von_neumann-x06-info_vs_fafnir-v01-phalanx.json) | von_neumann-x06-info | fafnir-v01-phalanx | A | 103 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `ab0b7775eda3bf0ea5d3fbf836e68045826874b46e6082362010b7a8d1c8c6c4`.
