# Ring promenade
**REUSED PRIOR SYNTHETIC · plausibility 0.87 · sampling weight 6.0000%**

[Map](../md26_promenade_ring_s0.map) · [Preview](../previews/md26_promenade_ring_s0.png) · [Full suite](../EXPLAINER.md)

Structurally and visually vetted distinct ring grammar. No competitive games or outcomes read. Play behavior unverified.

Plausibility rationale: Four openings connect an inner market with an outside route and distributed supply.
Limitation: This extends familiar ring geometry; its training value is not independently established.

Family: `md26_promenade`. Conservative split group: `loops_and_detours`. Related designs must remain in the same dataset partition.

Structure: 34×28; 50 active beds; 0 portal pairs; 4 starting dragons, lengths [3, 3, 3, 3]. Nearest opposing heads: 27 terrain steps, not combat time.

Renewal bounds (min:max → number of beds): `{'4:16': 8, '8:24': 42}`. Expected scheduled attempts by tick 500: 1691.74; occupancy and uncollected pearls suppress actual supply.

Validated by the installed engine. Every dragon has at least two initially unoccupied moves; all active beds are reachable from either team through the complete terrain/portal graph. Inaccessible empty reef cells: 0.

Gameplay: 2 fixtures (2 new, 0 reused), 303–345 rounds. Median combined bed harvest 466.5; median splits 249.5; total portal crossings 0.

Both teams harvested bed pearls in every fixture: True. Same-side sweep pairs: `[]`. These are diagnostics, not statistical proof of bias.

Prior disposition: `untouched_reserve`. Prior balance notes: Structurally and visually vetted distinct ring grammar. No competitive games or outcomes read. Play behavior unverified.

| Fixture | A | B | Winner side | Rounds | Conservative usable |
|---|---|---|---|---:|---|
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_01_md26_promenade_ring_s0_fafnir-v01-phalanx_vs_ouroboros-v13-ladder.json`) | fafnir-v01-phalanx | ouroboros-v13-ladder | A | 345 | True |
| Evidence (`../../../experiment_data/map_coverage_20260927_091715/games/new_01_md26_promenade_ring_s0_ouroboros-v13-ladder_vs_fafnir-v01-phalanx.json`) | ouroboros-v13-ladder | fafnir-v01-phalanx | B | 303 | True |

The plausibility score is frozen before this batch’s smoke outcomes. Prior results were already known for the six reused primary maps; this is not a blinded reassessment. Scores are judgments, not calibrated probabilities of fairness or finals selection. No-action deaths can be deliberate feeding, so they are separated from runtime faults. The optional conservative game weights exclude ambiguous fixtures; the map weight remains positive.

Map SHA-256: `847a085fc3c58c7b13f5f5c6426071ccbedfd55ec331e6c62f8dae3946da33ff`.
