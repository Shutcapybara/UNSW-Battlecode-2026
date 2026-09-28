# Pulse farms
**NEW THIS EXPANSION · plausibility 0.79 · sampling weight 5.4483%**

[Map](../mc26_pulse_farms.map) · [Preview](../previews/mc26_pulse_farms.png) · [Full suite](../EXPLAINER.md)

Fixed 12- and 36-tick bed schedules create predictable harvest pulses around porous shelves. These are recurring waves, not depleting food.

Plausibility rationale: Two fixed schedules create legible recurring harvest opportunities around porous shelves.
Limitation: Synchronized timing is deliberately stylized and unusually sensitive to harvesting and occupancy.

Family: `mc26_pulse_farms`. Conservative split group: `resource_geography_timing`. Related designs must remain in the same dataset partition.

Structure: 22×18; 34 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 15 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'12:12': 18, '36:36': 16}`. Expected scheduled attempts by tick 500: 946.0; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 219–252 rounds. Median combined bed harvest 216.0; median splits 123.0; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `None`. Prior balance notes: No previous competitive outcomes.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_10_mc26_pulse_farms_fafnir-v01-phalanx_vs_valjean-v01-portal-memory.json`) | fafnir-v01-phalanx | valjean-v01-portal-memory | A | 252 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_10_mc26_pulse_farms_valjean-v01-portal-memory_vs_fafnir-v01-phalanx.json`) | valjean-v01-portal-memory | fafnir-v01-phalanx | B | 219 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `6d50d460f95527c2625e2df811daeef77593b0aa08913ea69da0a58f1b8eec21`.
