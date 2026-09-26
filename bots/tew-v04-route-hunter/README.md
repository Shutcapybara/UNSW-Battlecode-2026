# tew-v04-route-hunter

Lineage: Tew. Strategic parent: `tew-v03-cautious-forager`; independent strategy branch based on `bots/hunter-v11-route-distance-exploration`.

Borrowed complete Python hunter policy, protocol adapter, and route/team-state logic from Hunter v11. This branch tests a proven alternative with explicit reachable attacks and route-aware pearl/exploration selection after Tew v02/v03's passive survival policy lost all completed matches to two strong references. Parameters and policy remain as in the borrowed source for this first control comparison.

Hypothesis: actively exploiting reachable attacks while retaining pearl routing yields better elimination outcomes than a gather-only posture.

Comparison: native quick set on `default_small`, `arena`, and `big_empty` against tew-v01, tew-v02, ouroboros-v10, and hunter-v20, both sides. Pending. No sandbox checks yet.


## Measured results

The first 24-game native run (`experiment_data/tew-v04-route-hunter_20260925043610487193`) was interrupted after 14 completed games to bound 500-round big-map runtime; the partial 13–1 result is not treated as a complete estimate. A complete 16-game small-map run, `experiment_data/tew-v04-route-hunter_20260925044139826303`, scored 12–0–4 with no runtime faults: v01/v02 8–0, ouroboros-v10 3–1, hunter-v20 1–3. It won all four on `arena` versus these baselines, while losing three of four on `default_small`. Native only; no sandbox checks.
