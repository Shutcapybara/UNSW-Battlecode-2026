# tools/analysis — handoff A1 one-off analyses (2026-09-28)

Author `glm/analysis/a1`. Recurring statistics live in `tools/hub/{analysis,calibration}.py`
(recomputed every hub cycle); this directory holds the one-off scripts and evidence for the
findings in `docs/findings/2026-09-28-analysis-*.md` and the atlas `docs/analysis/ATLAS.md`.

## Shared loader

- `live_load.py` — loads `LIVE/state/state.json` (path overridable via `JKS_LIVE_STATE`),
  annotates each verified game with `_block/_experiment/_phase/_arm` from the blocks list,
  and exposes stage accessors (`stage`, `per_1k`, `map_class`, `field_controlled`).

## Scripts (stdout = markdown evidence; rerun to refresh)

| script | finding | what it prints |
|---|---|---|
| `a1_loss_anatomy.py` | loss-anatomy | per-source loss tables: reason splits, map classes, win/loss stage medians, deaths/1k, first-trailing stage, opponent cells |
| `a2_paired_contrasts.py` | paired-contrasts | per-block exact-pair score/length/stage deltas for the four screen experiments; flipped-vs-held summary |
| `a3_layout_assignment.py` | layout-id-parity | layouts per map, seed-reuse check, covariate purity, within-block arm matching, adjacency/alternation tests |
| `a6_a7_runtime_sonar.py` | runtime-sonar | cpu_max tables by source/pool, stage-window cpu, near-cap context; sonar rates with within-line median splits; opponent sonar |
| `rating_evidence.py` | rating-minimum-evidence | minimum-evidence rule + shrinkage (library; used by the patch below) |
| `patches/benchmark_ratings_min_evidence.patch` | rating-minimum-evidence | applies the rule to `tools/benchmark_ratings.py` (verified against 2026-09-28 latest.json; reapply after regenerating) |

## Notes

- All scripts read only; none touch the API, uploads, or the live executor.
- `LIVE/state/state.json` is 7–10 MB — always via `live_load` (key-selecting), never dumped.
- The hub-side equivalents of these statistics are `tools/hub/analysis.py::layout_parity /
first_trailing / trailing_profile / runtime_table / sonar_table / elo_trajectory` and
`tools/hub/calibration.py::opponent_fingerprints / local_priority_ok`, tested in
`tests/test_hub_analysis_a1_stats.py`.
