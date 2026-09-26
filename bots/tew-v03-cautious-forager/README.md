# tew-v03-cautious-forager

Lineage: Tew. Parent: `tew-v02-survive-forage`; base `examples/bahamut-scaffold/`.

Borrowed: world model and policy architecture from `bots/drake-v01-survive-forage/main.py` through v02. Hypothesis: stronger avoidance of visible enemy sprint reach, dead ends, and unsafe splitting reduces early elimination against aggressive baselines.

Changes from v02: enemy strike probabilities 0.75/0.35/0.15 → 0.95/0.65/0.35; role risk multipliers 1.3/1.6 → 2.5/2.8; trap penalty 12→20; zero-exit penalty 6→10; split danger gate 0.3→0.1.

Comparison: native quick set on `default_small` and `arena` against v01, ouroboros-v10 and hunter-v20, both sides. Results pending. Judge CPU validation not run.


## Measured results

Native comparison, `experiment_data/tew-v03-cautious-forager_20260925043444319564`: 5–0–11 across 16 games, no runtime faults. Results: v01 4–0, v02 1–3, ouroboros-v10 0–4, hunter-v20 0–4; maps `default_small` and `arena`, both sides. The cautious parameter change did not improve cross-line results. No sandbox checks.
