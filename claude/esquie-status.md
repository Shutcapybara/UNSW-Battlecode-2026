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

- **Part 1 done (base panels + brick list + clusters).** z1 seeds 1+2 (320 games), gen seed 1
  (464). Pooled base: econ 1.1276, win 70.9 % / gen 63.4 %. The brick list inverts part of the
  expectation: **Schooltime is our best map** (econ percentile 0.790), the economy bricks are
  **Trauma 0.375 / Dilemma 0.413 / Portals 0.506** — three different kinds (starved opening /
  churn-without-growth / transit+collision leak). Devil win 0.500 = the D-033 identity cost
  (classified, not fixable). Gen bricks are mostly *fight-loss* maps (pinwheel 0.31, seam_market
  0.38, commons 0.50: deaths 63–100 % enemy-caused) plus the identity pair devil_tr/trophy_tr.
  Signature clusters: every _tr twin clusters with its original; **maps/new has no member of the
  corridor/kelp or portal-heavy clusters** — transfer tests for those motifs rely on the _tr
  twins. Tooling: `tools/esquie/signature.py` (21 features incl. spawn-supply), 
  `tools/esquie/bricklist.py` (per-map three-number form + paired deltas).
- **Part 2 anatomies done** (finding `docs/findings/2026-10-01-esquie-map-anatomy.md`): Trauma =
  starved opening (supply8 = 3 beds in 8 steps of spawn, supply50 = 0.75; r50 = 1 pearl; replay:
  beds in view with countdowns 32–154, nothing targeted, dragons cruise); Dilemma = children
  born into bed-deserts (countdowns 426–438 on a 393-round game; 38 % of children die <10
  rounds; swarm is length-2 dust); Portals = trapped 81.9 / portal 74.6 / h2h-ally 13.1/1k
  (16x zoo), same-pair doubles 85/game, cramped SPLIT into enemy contact seen in the replay.
- **esquie-02-starve-wait built** (M-1 Part 3, first mechanism): bed anticipation gated on the
  starved observable (no food known: no visible/remembered pearl, no seen bed ripening within 8
  rounds; age >= 12). Switch-off 0 divergent / 19,403 turns; acts only where designed (trauma 35,
  dilemma 30 divergent turns; **portals 0**, schooltime 26/13,578). z1 s1+2 and gen s1 panels
  running.
