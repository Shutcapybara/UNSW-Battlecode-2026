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

Seed 1 of both panels first (160 + 232 games); a candidate whose pool Δecon point estimate is ≤ 0 stops there
(logged as REJECT at screen). Otherwise the full D-032 gate (seeds 1–3, both panels) decides.

## Versions

| version | mechanism | expected | pool Δecon [90 %] | gen Δecon [90 %] | CPU max | verdict | why |
|---|---|---|---|---|---|---|---|
| 00-base | verbatim copy | = | — | — | — | control | golden parity 0 divergent |
| 01-nodevil | devil terms off (map identity) | ≤ 0 on devil only | (vs 00 pending) | — | — | parent (forced) | lane rule |
| 02-bedwait | bed_wait 0 → 6 (value beds spawning ≤ 6 rounds after arrival) | + on fast-bed maps | −0.032 [−0.073, +0.010] (s1) | −0.033 [−0.086, +0.022] (s1, partial) | — (params) | REJECT at screen | gen p@50 −0.057 [−0.092, −0.023]; hovering at beds costs exploration |
