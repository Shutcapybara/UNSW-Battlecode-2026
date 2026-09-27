# Spring wells
**NEW THIS EXPANSION · plausibility 0.85 · sampling weight 5.8621%**

[Map](../mc26_spring_wells.map) · [Preview](../previews/mc26_spring_wells.png) · [Full suite](../EXPLAINER.md)

A few every-round wells compete with slower fallback farms; open approaches make occupation and collector throughput important.

Plausibility rationale: A few rapid wells and slower fallback farms support a clear occupation-versus-coverage choice.
Limitation: A small number of wells may concentrate conflict; nominal output can greatly exceed realized income.

Family: `mc26_spring_wells`. Conservative split group: `resource_geography_timing`. Related designs must remain in the same dataset partition.

Structure: 26×22; 22 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 19 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'1:1': 4, '20:60': 18}`. Expected scheduled attempts by tick 500: 2217.01; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 67–122 rounds. Median combined bed harvest 72.5; median splits 33.0; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'ouroboros-v13-ladder', 'side': 'A'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_11_mc26_spring_wells_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json) | fafnir-v01-phalanx | ouroboros-v13-ladder | A | 67 | True |
| [Evidence](../../../experiment_data/map_coverage_20260927_091715/games/new_11_mc26_spring_wells_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json) | ouroboros-v13-ladder | fafnir-v01-phalanx | A | 122 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `b111c668c781cbb3c63c89b49fbc6489b1120a059410960cc425ab8a26ddf6d4`.
