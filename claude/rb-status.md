# rb lane status — Aline lineage (R-2b open exploration, blind)

Opus 5.5, desktop, Claude Code. Branch `r/rb`, worktree `../wt-rb`, bots `bots/aline-<nn>-<slug>/`, tools `tools/rb/`.
Lineage name: **Aline** (the user renamed the prompt's "Basquiat" lineage; everything else as specified).

## Blindness log

Not opened: `docs/hub/HYPOTHESES.md`, `docs/findings/`, `claude/*-status.md` (other than this file), `docs/TEAM-SUMMARY-*`,
other lanes' reports or bot READMEs. Read: game docs (game.battlecode.au/docs), `docs/analysis/BENCHMARKS.md`, the
base source, harness tool source (`tools/ra`, `tools/lune`, `tools/cx`, `tools/analysis/features/frame.py`), own replays.
Incidental: directory listings of `docs/` and `claude/` show file names only; base's CANDIDATE.toml (copied, not
kept) names a findings file, not opened.

## Setup

- `aline-00-base` = verbatim `lune-r1-07-latecap8x-only` (from origin/main 98202b51). Golden harness
  (`tools/cx/golden.py replay --all`), 4 fixtures (schooltime A s1, devil B s2, portals A s3, new/mc26_crossroads B s1,
  vs fenrir-v18): 40,100 turns, **0 divergent**.
- `aline-01-nodevil` = one switch `Params::map_identity_terms = false` gating the three `W==32 && H==16` terms.
  The atlas (`world.hpp atlas_try`) is never called; the `2*NC <= 8192` checks are size caps (measured), kept.
- Gate: `tools/rb/gate.py` (runs `tools/rb/run.py` = lune arena rows; scores with a paired fixture bootstrap, 90 %).
  Pool = ZOO(8) x 10 live maps x 2 seats x seeds 1-3 = 480; gen = 4 fixed opps x 29 maps (maps/new/*, maps/var/*_tr)
  x 2 seats x seeds 1-3 = 696. Pool economy / field per-map median; gen economy / parent per-map mean.
- Host shared with another lane (hb1), so a full gate takes ~1.5 h rather than ~25 min.

## Screening rule

Seed 1 of both panels first (160 + 232 games); a candidate stops there (REJECT at screen) when its pool Δecon
point estimate is ≤ 0, or (from 04 on) when units@100, length@100 or win has a point estimate below −0.03.
Otherwise the full D-032 gate (seeds 1–3, both panels) decides. Null mechanisms may be rejected on a direct
replay check (counting the targeted event) without a screen.

Report 1: `docs/findings/2026-09-30-rb-lane.md` (versions 01–06).

## Versions

| version | mechanism | expected | pool Δecon [90 %] | gen Δecon [90 %] | CPU max | verdict | why |
|---|---|---|---|---|---|---|---|
| 00-base | verbatim copy | = | — | — | — | control | golden parity 0 divergent |
| 01-nodevil | devil terms off (map identity) | ≤ 0 on devil only | (vs 00 pending) | — | — | parent (forced) | lane rule |
| 02-bedwait | bed_wait 0 → 6 (value beds spawning ≤ 6 rounds after arrival) | + on fast-bed maps | −0.032 [−0.073, +0.010] (s1) | −0.033 [−0.086, +0.022] (s1, partial) | — (params) | REJECT at screen | gen p@50 −0.057 [−0.092, −0.023]; hovering at beds costs exploration |
| 03-nofarm | trap_farm_factor 0.15 → 1.0 (no pocket-farm discount) | hygiene ↓, econ ? | −0.068 [−0.099, −0.037] (s1) | not run | — (params) | REJECT at screen | every checkpoint down; wall deaths only −6 %: the split-out pocket farm pays |
| 04-dive5 | dive_value 3 → 5 (unpaired portal = unseen cell as a target) | + p@50 on portal-gated maps | +0.191 [+0.134, +0.252] (s1) | +0.119 [+0.075, +0.167] (s1) | — (params) | REJECT (full pool, s1–3: +0.169 [+0.135, +0.203]) | eats more but dies more: units@100 −0.079 [−0.127, −0.030], length@100 −0.060 [−0.100, −0.019], pool win −0.069 [−0.108, −0.029], tier-2 +13–24 %; part of the pearl gain is corpse recycling. Gen s2–3 stopped (verdict fixed by pool guards) |
| 05-portalyield | crosser yields: blind landing near a fresh ally density report scored as occupied | ally head-on ↓ on portal maps | −0.004 [−0.016, +0.008] (s1) | skipped | 8.67 M (parent 8.53 M) | REJECT (null) | ally collisions per 100 crossings 9.78 vs 9.78 on 8 portals replays: crossings are mostly dives (landing unknown), so the crosser-side check never applies; 10 (stack on 04) dropped |
| 06-exitavoid | exit side: ending on a portal exit costs 0.03 × value (0.3 with an ally report near the entry) | ally head-on ↓ | not screened | — | 8.68 M | REJECT (null, replay check) | 8 portals replays: 10.50 vs 9.78 collisions per 100 crossings; base term ~0.15 is below a pearl, ally term needs a known pair (dives lack one); expected loss of an exit step ~0.3, so the collisions are the pod-harvest price (~5–8 % of portals economy); 11 (stack on 04) dropped |
| 12-dive4 | dive_value 3 → 4 (dose between 01 and 04) | most of 04's gain, less damage | +0.089 [+0.053, +0.128] (s1) | +0.006 [−0.007, +0.019] (s1) | — (params) | REJECT at screen | pool guards flat, but gen units@100 −0.034 [−0.051, −0.017], length@100 −0.031; pool h2h +12 %. Dives stay costly while blind: retest on top of 13 |
| 13-symmetry | infer map symmetry from observed edges / bed countdowns; mirror terrain, bed timings, portal pairs; sonar type 8 | + econ on gated maps | +0.038 [+0.019, +0.059] (s1–3; cluster [+0.014, +0.062]) | +0.012 [−0.001, +0.026] (s1–3) | 8.72 M | REJECT (near miss) | pool passes everything: units +0.036, length +0.033, win +0.054 [+0.019, +0.090], tier-2 ≤ +7 %. Gen fails narrowly: wall +10.3 % (2.63 → 2.90 /1k, on transposed live maps where the economy rose) and win lo −0.032 (point −0.005); gen units +0.027, length +0.025 significant. Ablation 15 drops the bed channel. 14 (sym + dive4) withdrawn: parent not accepted |
| 15-sym-nobeds | 13 without bed-countdown mirroring (terrain + portal pairs only) | wall back to parent, most of the gain kept | +0.010 [−0.005, +0.026] (s1–3) | +0.009 [−0.004, +0.022] (s1) | ≈ 13 | REJECT | ablation: the bed channel carries 13's economy (+0.038 → +0.010); terrain/pairs carry the wins (pool win +0.037 [+0.002, +0.073], gen s1 +0.065) and the gen wall rise (s1 +12 %). Hypothesis (beds cause the wall rise) wrong |

Note (13/15): on trauma_tr replays the extra wall deaths with symmetry are pocket-farm sacrifices (doomed after split 118 → 153 in 8 games), not crossings; known terrain shows the planner more pearl pockets. 13 is kept as the stacking candidate once a hygiene lever (07 allyseal, 16 farm25) is found.
| 07-allyseal | ally right-of-way seal convention (user suggestion): longer dragon has the contested cell; equal → greater x, then y | fewer ally-sealed deaths | −0.020 [−0.035, −0.007] (s1) | −0.006 [−0.021, +0.010] (s1) | 8.65 M | REJECT at screen alone; stacking lever | pool tier-2 wall −4 %, self −7 %, body −9 %; gen win +0.060 [+0.022, +0.103], self −7 %, body −11 %, h2h −8 %. Stacked with 13 as 17 |
| 16-farm25 | trap_farm_factor 0.15 → 0.25 | wall ↓ few %, econ slightly ↓ | −0.074 [−0.105, −0.042] (s1) | skipped | — (params) | REJECT at screen | a cliff, not a slope: as bad as 03 (1.0: −0.068), p@250 −0.129; wall only −4 % |
| **17-sym-seal** | **stack: 13 symmetry inference + 07 ally right-of-way seal (identical change sets) vs 01** | econ +, wins +, tier-2 inside +10 % | **+0.025 [+0.005, +0.045]** (s1–3; cluster [−0.000, +0.049]) | **+0.012 [−0.003, +0.027]** (s1–3) | 9.08 M | **ACCEPT** | pool units +0.052, length +0.048, win +0.061 [+0.025, +0.096]; gen units +0.076, length +0.071, win +0.029 [−0.001, +0.058]; tier-2 pool wall −1 % self −3 % body −5 % h2h +7 %, gen wall +8.7 % self −6 % body −13 % h2h −2 %. Checkpoints: p@50/p@100 up on both panels, p@250 flat. New parent |
| 18-farm05 | trap_farm_factor 0.15 → 0.05 on 17 | small + econ, wall ↑ | +0.048 [+0.025, +0.073] (s1) | +0.005 [−0.006, +0.016] (s1) | — (params) | REJECT at screen | pool wall +25 %, self +19 %; units/length flat, win −0.022: the extra pearls are paid in dead dragons. The farm discount is a two-sided cliff at 0.15 |
| 19-dive4 | dive_value 3 → 4 on 17 | + p@50, units flat | +0.077 [+0.041, +0.114] (s1) | −0.002 [−0.014, +0.009] (s1) | — (params) | REJECT at screen | gen win −0.043 [−0.078, −0.013], gen units −0.028, length −0.025: symmetry does not make dives safe on unseen maps |
| 20-spread | density_ally_weight 0.10 → 0.40 on 17 | + p@50 on open maps | +0.018 [−0.016, +0.055] (s1) | +0.009 [−0.024, +0.042] (s1) | — (params) | screen passed (borderline); full gate queued | pool units +0.034, length +0.035, win +0.034; gen h2h +14 %, gen units −0.017 |
