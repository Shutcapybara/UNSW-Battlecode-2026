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

- **Part 3 done: two mechanisms, four versions, one LOCAL HOLD.**
  - **starve-wait (bed anticipation gated on the dragon's own food knowledge):** v02 REJECT
    (pooled −0.024, Trophy leak — gate bug: stale-ripe beds invisible to the gate); v03 fixed the
    gate (trauma_tr +0.31 win transfer, win +0.62pp, paired −0.0041 [−0.025,+0.017]); v03b
    min_age 12→24: **LOCAL HOLD at seeds 1–3** — paired Δecon +0.0018 [−0.0024, +0.0062], win
    +1.0pp, Trauma +6pp win, Dilemma +2pp/+11 p@250, Devil/Portals bit-identical, off-cluster
    silent. Next parameter: min_age 16–18 (the Trauma r50 opening gain lives in r12–24).
  - **crit-enclosure split (V19 port):** REJECT at panel scale with clean attribution — Slithery
    trapped −19 %/newborn −28 % (the mechanism works there) but pooled trapped ROSE 37→39.7,
    own-body +24 %, econ −0.035. It is a Slithery-shaped mechanism; a churn-profile-gated form is
    queued.
  - Ledger rows proposed: **L31 new** (starved openings, weight 0.5, evidence 02/03/03b),
    **L24 → 0.35** (V19 panel-scale), L28/L29 annotated (Portals is also 32x16; Slithery churn is
    load-bearing).
  - Map × mechanism table and all per-map reads in
    `docs/findings/2026-10-01-esquie-map-anatomy.md`. Raw: game_stats/runs/esquie-*.
  - Not registered (no candidate passes the accept gate; 03b is the hold the director can promote
    or hand to the structure-gated-switch test).
