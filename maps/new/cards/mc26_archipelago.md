# Reef archipelago
**NEW THIS EXPANSION · plausibility 0.84 · sampling weight 5.7931%**

[Map](../mc26_archipelago.map) · [Preview](../previews/mc26_archipelago.png) · [Full suite](../EXPLAINER.md)

Route around four deliberate sealed reefs to reach several harbors; interiors contain neither resources nor spawns.

Plausibility rationale: Four sealed reefs create understandable detours between accessible harbor resources.
Limitation: Sealed interiors are intentional empty terrain; they must not be mistaken for missing rewards.

Family: `mc26_archipelago`. Conservative split group: `open_navigation`. Related designs must remain in the same dataset partition.

Structure: 36×28; 60 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 29 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'10:30': 24, '4:16': 12, '6:22': 24}`. Expected scheduled attempts by tick 500: 2032.61; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 70.

Gameplay: 2 fixtures (2 new, 0 reused), 183–294 rounds. Median combined bed harvest 390.5; median splits 179.5; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'valjean-v01-portal-memory', 'side': 'A'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_02_mc26_archipelago_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json`) | fafnir-v01-phalanx | valjean-v01-portal-memory | A | 183 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_02_mc26_archipelago_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json`) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 294 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `b73c5a110ff7a69acd8c96e68107ba187280bdd2431fbc09d0a86fd4e4efe2a3`.
