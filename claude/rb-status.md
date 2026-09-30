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
| 13-symmetry | infer map symmetry from observed edges / bed countdowns; mirror terrain, bed timings, portal pairs; sonar type 8 | + econ on gated maps | +0.074 [+0.039, +0.111] (s1) | +0.021 [−0.003, +0.045] (s1) | pending | screen passed; full gate running | s1: pool units +0.056, length +0.043, win +0.087 [+0.025, +0.144]; gen units +0.145, length +0.141, win +0.052; only flag gen wall +11 % (2.44 → 2.70 /1k). Pocket deaths not reduced (replays): gain is bed timing / routes |
