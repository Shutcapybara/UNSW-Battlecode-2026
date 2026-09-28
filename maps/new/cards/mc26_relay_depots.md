# Relay depots
**NEW THIS EXPANSION · plausibility 0.82 · sampling weight 5.6552%**

[Map](../mc26_relay_depots.map) · [Preview](../previews/mc26_relay_depots.png) · [Full suite](../EXPLAINER.md)

Four paired horizontal and vertical links shorten travel between remote depots, with open-water alternatives everywhere.

Plausibility rationale: Multiple shortcuts connect remote food depots while ordinary travel remains possible.
Limitation: Four portal pairs add complexity; useful memory or calibrated risk-taking is not proven by crossing counts.

Family: `mc26_relay_depots`. Conservative split group: `portal_shortcuts_and_dividers`. Related designs must remain in the same dataset partition.

Structure: 48×32; 80 active beds; 4 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 20 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'4:20': 24, '6:22': 24, '8:24': 32}`. Expected scheduled attempts by tick 500: 2824.97; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 251–373 rounds. Median combined bed harvest 745.0; median splits 383.5; total portal crossings 176.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_08_mc26_relay_depots_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json`) | fafnir-v01-phalanx | valjean-v01-portal-memory | B | 251 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_08_mc26_relay_depots_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json`) | valjean-v01-portal-memory | fafnir-v01-phalanx | A | 373 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `7b836c08dad32761befa7bb2533402c4833a2fd54e72a47ff75bccc77ecdeb01`.
