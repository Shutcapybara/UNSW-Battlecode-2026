# Portal quartet
**NEW THIS EXPANSION · plausibility 0.76 · sampling weight 5.2414%**

[Map](../mc26_portal_quartet.map) · [Preview](../previews/mc26_portal_quartet.png) · [Full suite](../EXPLAINER.md)

Four sealed districts connect in a portal ring; each district has two separate portal links. All productive regions are portal-reachable.

Plausibility rationale: A four-room ring has two distinct links per room and no unreachable active resources.
Limitation: Mandatory portals are the strongest extrapolation here and can magnify policy paralysis or congestion.

Family: `mc26_portal_quartet`. Conservative split group: `portal_dependency`. Related designs must remain in the same dataset partition.

Structure: 32×28; 48 active beds; 4 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 15 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'5:19': 24, '9:27': 24}`. Expected scheduled attempts by tick 500: 1647.0; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 471–500 rounds. Median combined bed harvest 690.0; median splits 391.5; total portal crossings 364.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_07_mc26_portal_quartet_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json`) | fafnir-v01-phalanx | ouroboros-v13-ladder | A | 500 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_07_mc26_portal_quartet_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json`) | ouroboros-v13-ladder | fafnir-v01-phalanx | B | 471 | False |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `07b5250b909049739643f34977e6e09e408c03f5b6a67a13f6347e215bb160df`.
