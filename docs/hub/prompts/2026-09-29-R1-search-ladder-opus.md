# R-1 — Search-depth ladder on Ares, with the CPU wall measured (Opus 5.5)

Branch `r/r1`, worktree `../wt-r1`. Bots under `bots/r1-<nn>-<slug>/`. Read first: `docs/hub/prompts/2026-09-29-R-index.md`
(rules), `docs/findings/2026-09-29-ares-v06-expanded-search-support.md`, `docs/ares-family.md`,
`docs/analysis/BENCHMARKS.md` §"How to use it", `tools/cx/README.md`.

## Question

Ares V06 raised the bounded search from V05's profile to 160 target nodes (64 saturated, 60 at birth), room flood
24/40, three-step horizon 12, and gained +12.9 % dragons at r100 and +3.5 expected-score points, at p99 7.4 M /
max 8.6 M points per turn against a 100 M cap. That is the only lever in the programme with a measured positive
slope, and it has used under a tenth of the budget. **How far does the slope go, and where does the CPU wall
actually sit?**

## Step 0 — fix the base (half a day)

V06 has one seed on the ten live maps and no generalisation run. Before laddering:

1. Add an atlas switch to a copy of V06 if `atlas.hpp` has none (`params.hpp: ATLAS_ENABLED`, default off for
   every measurement in this task). If V06's atlas is inert for unseen maps already, say so with the code line.
2. Run V06 (atlas off) and V05 (atlas off) on: the z1 panel at seed 2; the generalisation panel (`maps/new/` all 20,
   `maps/var/*_tr.map`) at seed 1, same eight opponents, both seats. Score with `tools.analysis.features.benchmarks`.
3. Report V06 − V05 on both panels as the BENCHMARKS three-number form. If the r100 dragons gain survives off-pool
   and the economy is not down, V06 is the base (`r1-00-base`). If it does not, V05 is the base and the finding
   says why. The `+0.05` gate not being met on seed 1 is known; the question here is generalisation, not the gate.

## The ladder

Vary **only** the search budget, everything else at base. Levels, each a directory `r1-0k-…` with a one-line
`CANDIDATE.toml` mechanism:

| Level | `search_cap` (normal / saturated / born) | room flood | `sprint3_limit` | expected points |
|---|---|---|---|---|
| L0 (base) | 160 / 64 / 60 | 24/40 | 12 | ~5–9 M |
| L1 | 320 / 128 / 120 | 32/56 | 16 | ~2× |
| L2 | 640 / 256 / 240 | 48/80 | 24 | ~4× |
| L3 | 1280 / 512 / 480 | 64/112 | 32 | ~8× |

Keep the late/sparse guards (`search_cap_late*`, `search_cap_sparse*`) scaled by the same factor, so late-game
behaviour is not a separate change. If the search is not bounded by a single knob — if depth 1 (`search_depth1`)
and the frontier depth (`frontier_search_depth`) interact — say which knob the ladder moves and why, and keep the
others fixed.

For each level:

1. **CPU probe first.** `tools/cx/arena.py --sandbox` (judge pricing) on the densest fixtures: Schooltime,
   Portals, Trauma, Big Empty, both seats, plus the three densest `maps/new/` maps by unit count at r100 from
   step 0. Record p50, p99 and max points per turn, and the per-turn maximum over the *worst* turn of the game (the
   cap is per turn, not per game). A level whose max exceeds 60 M on any fixture is over the wall: report it and
   do not panel it. The wall is a number to publish, not a guess.
2. **Panel.** z1 seed 1, both seats, atlas off (160 games). Score. Then the generalisation panel seed 1.
3. **Table.** Per level: the tier-1 economy checkpoints, dragons/length/births at r100, the five tier-2 rates, panel
   win–loss–draw, and the CPU numbers, on both panels. One row per level, deltas against L0.

## What to read from it

- The slope: gain per doubling on each metric, on the pool and off it. If it flattens before the wall, the next
  lever is not depth, it is what the search evaluates (R-5). If it is still rising at the wall, the next lever is
  search efficiency (move ordering, incremental state, cheaper flood) — say which, with the meter breakdown from
  `tools/cx/meter.py`.
- Whether the gain is retention (dragons at r100) or economy. V06's was retention; if the ladder is all retention
  and no pearls, say so — BENCHMARKS gates on economy and the finding must say whether the gate is the wrong shape
  for a search gain (it may be: the chart's retention gap is the thing the search closes).
- Seat asymmetry and map-family asymmetry (tiny maps vs Schooltime-class): search may pay on one and not the
  other, and the OOS rule says the response must key on observable structure (unit count, tile count), never
  the map.

## Deliverables

`docs/findings/2026-09-3x-r1-search-ladder.md` (tables above; the wall; the slope; the recommended level and the
structure-keyed rule if one is needed), `claude/r1-status.md`, `game_stats/runs/r1-*.json`, bots `r1-00…03`.
For the recommended level: a `CANDIDATE.toml` (`language = "c++"`, lineage `ares`, `lineage_parent` = the base)
and a line in the finding saying it is ready for `register.json`. Do not register it yourself.

Budget: step 0 ~340 games, the ladder ~4 × 400 games plus probes. Report interrupted levels as interrupted.
