# Delayed commons
**NEW THIS EXPANSION · plausibility 0.83 · sampling weight 5.7241%**

[Map](../mc26_delayed_commons.map) · [Preview](../previews/mc26_delayed_commons.png) · [Full suite](../EXPLAINER.md)

Small near-side farms supply the opening; the rich interior first becomes available after 70–110 ticks and keeps that renewal range.

Plausibility rationale: Opening farms sustain play before the large interior supply begins renewing.
Limitation: The 70–110 gap applies to every renewal, not a scripted phase change; late supply may be underused.

Family: `mc26_delayed_commons`. Conservative split group: `resource_geography_timing`. Related designs must remain in the same dataset partition.

Structure: 24×22; 92 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 17 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'4:12': 12, '70:110': 80}`. Expected scheduled attempts by tick 500: 1150.29; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 154–206 rounds. Median combined bed harvest 184.5; median splits 106.0; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'ouroboros-v13-ladder', 'side': 'B'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_09_mc26_delayed_commons_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json) | fafnir-v01-phalanx | ouroboros-v13-ladder | B | 154 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_09_mc26_delayed_commons_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json) | ouroboros-v13-ladder | fafnir-v01-phalanx | B | 206 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `176b9b5a606397f24f93eaf0dcbf517abc9e1b411ef2b61e067462080dc821d4`.
