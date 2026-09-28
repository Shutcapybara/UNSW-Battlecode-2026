# Nursery bays
**NEW THIS EXPANSION · plausibility 0.84 · sampling weight 5.7931%**

[Map](../mc26_nursery_bays.map) · [Preview](../previews/mc26_nursery_bays.png) · [Full suite](../EXPLAINER.md)

One length-eight dragon per side starts in a spacious two-exit bay, allowing meaningful choices between early division and keeping mass.

Plausibility rationale: Length-eight starts have spacious bays and two broad exits, making early division plausible.
Limitation: Long starts already exist in references; this tests a new deployment/room combination rather than a new rule.

Family: `mc26_nursery_bays`. Conservative split group: `productive_rooms_and_deployment`. Related designs must remain in the same dataset partition.

Structure: 32×24; 24 active beds; 0 portal pairs; 2 starting dragons, lengths [8, 8]. Nearest opposing heads: 22 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'4:16': 8, '6:18': 16}`. Expected scheduled attempts by tick 500: 1057.07; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 224–243 rounds. Median combined bed harvest 205.5; median splits 116.5; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[{'opponent': 'valjean-v01-portal-memory', 'side': 'A'}]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_14_mc26_nursery_bays_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json`) | fafnir-v01-phalanx | valjean-v01-portal-memory | A | 243 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_14_mc26_nursery_bays_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json`) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 224 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `df21e490f0ae8e7eeda160f23ce8a11fc176d795c642b948ff3a5992ac49ec30`.
