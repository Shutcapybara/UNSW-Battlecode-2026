# Spread commons
**REUSED PRIOR SYNTHETIC · plausibility 0.93 · sampling weight 3.2069%**

[Map](../md26_commons_spread_s0.map) · [Preview](../previews/md26_commons_spread_s0.png) · [Full suite](../EXPLAINER.md)

Spread commons; prior map card and full evidence retained in the preceding batch.

Plausibility rationale: The same resource schedule is spread into multiple viable farming areas, giving a clear distribution contrast.
Limitation: Distributed harvesting need not lead to reliable late crown conversion.

Family: `md26_commons`. Conservative split group: `resource_geography_timing`. Related designs must remain in the same dataset partition.

Structure: 24×20; 56 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 17 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'20:40': 8, '4:12': 48}`. Expected scheduled attempts by tick 500: 3111.13; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 6 fixtures (0 new, 6 reused), 385–500 rounds. Median combined bed harvest 996.5; median splits 612.0; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'valjean-v01-portal-memory', 'side': 'A'}, {'opponent': 'von_neumann-x06-info', 'side': 'A'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `accepted`. Prior balance notes: Matched supply and shore with the shared sibling produce sustained local income, much longer games and meaningful late positions in both layouts. Two primary side-swapped pairs favor A; the second layout and reflection do not reproduce a universal side advantage. Retain with limited fairness evidence and exclude flagged no-action games from training.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/008_md26_commons_spread_s0_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json`) | fafnir-v01-phalanx | ouroboros-v13-ladder | B | 489 | False |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/009_md26_commons_spread_s0_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json`) | ouroboros-v13-ladder | fafnir-v01-phalanx | A | 385 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/010_md26_commons_spread_s0_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json`) | fafnir-v01-phalanx | valjean-v01-portal-memory | A | 500 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/011_md26_commons_spread_s0_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json`) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 500 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/012_md26_commons_spread_s0_fafnir-v01-phalanx_vs_von_neumann-x06-info.json`) | fafnir-v01-phalanx | von_neumann-x06-info | A | 447 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/014_md26_commons_spread_s0_von_neumann-x06-info_vs_fafnir-v01-phalanx.json`) | von_neumann-x06-info | fafnir-v01-phalanx | A | 500 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `728b948e68bb569ecb26dd667b1da981b7b5be42a01ef1e70900a04437f45aa4`.
