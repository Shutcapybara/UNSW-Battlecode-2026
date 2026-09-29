# Esquie status (M-1 map anatomy, GLM 5.3)

Branch `r/esquie`, worktree `../wt-esquie`. Host: the Mac (desktop path not reachable from
this session; desktop lanes run separately). Tooling: R-4 scorecard + run_panel grids,
`tools/esquie/signature.py` (structural signature vectors), `tools/esquie/bricklist.py`
(per-map three-number form), `tools/analysis/r3_ledger.py` (death ledger).

## Log

- **2026-09-30 lane launch.** Base `esquie-01-nodevil` built: lune-r1-07-latecap8x-only
  with the three `W==32 && H==16` terms off behind `Params::shape_terms=false` (D-033, the
  renoir-23 ablation form). Golden parity: shape_terms=true variant vs lune-r1-07 recordings
  = **0 divergent / 27,957 turns** (devil-A 5,731 / portals-A 8,648 / schooltime-B 13,578);
  the shipped nodevil bot is 0-divergent on schooltime (terms inert at 60x40) and diverges
  only on the 32x16 maps (devil 335, portals 638 turns) — the ablation acting as designed.
  Note: **Portals is also 32x16** (with Devil and Dilemma), so the terms were live there too.
