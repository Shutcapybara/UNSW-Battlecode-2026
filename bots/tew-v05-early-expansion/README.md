# tew-v05-early-expansion

Lineage: Tew. Parent: `tew-v04-route-hunter`; based on the Python Hunter v11 policy.

Hypothesis: the v04 arena losses came partly from slow population growth (21 enemy units versus Tew's elimination by round 35) and crowding deaths. On small maps, producing a distributed team of up to 12 units before reserving a growth crown should improve early contest strength. On medium/large maps the target is 40/60, capped by the engine limit.

Change: in `body()`, before crown growth and attack decisions, split any length-4+ dragon into two length-2 dragons while team units remain below the area-based target. Existing policy handles movement, attacks, sonar, portals and post-target crown growth.

Comparison: native on `default_small` and `arena` against tew-v04, ouroboros-v10 and hunter-v20, both sides. Pending. No judge CPU validation.


## Measured results

Native comparison, `experiment_data/tew-v05-early-expansion_20260925044406391757`: 6–0–6 across 12 games, no runtime faults. It scored 2–2 versus v04, 3–1 versus ouroboros-v10 and 1–3 versus hunter-v20 on `default_small` and `arena`, both sides. The small-map target of 12 did not resolve Arena losses. No sandbox checks.
