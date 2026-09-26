# tew-v06-safe-fallback

Lineage: Tew. Parent: `tew-v05-early-expansion`; same hunter-v11 base.

Hypothesis: v05 arena losses still included wall-edge deaths. Its no-target fallback explicitly moved toward an unknown edge (or defaulted north), which can select a blocked tile. Replacing that probe with the policy's simulated safe escape should reduce avoidable wall deaths.

Change: `forage()` now delegates its exhausted-target fallback to `escape()` rather than moving into an unknown direction. Early expansion from v05 is retained.

Comparison: native on `default_small` and `arena` against tew-v05, ouroboros-v10 and hunter-v20, both sides. Pending. No judge CPU validation.


## Measured results

Native comparison, `experiment_data/tew-v06-safe-fallback_20260925044612627797`: 6–0–6 across 12 games, no runtime faults. It scored 2–2 versus v05, 3–1 versus ouroboros-v10 and 1–3 versus hunter-v20 on `default_small` and `arena`, both sides. The safe fallback change did not move aggregate results. No sandbox checks.
