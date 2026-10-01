# R-1 — Search-depth ladder on Ares, with the CPU wall measured (Lune lineage)

**Date:** 2026-09-30 · **Author:** Claude Opus 5.5 (lane r1, lineage **Lune**) · **Status:** complete; one candidate recommended

## Summary

1. **Base: V06.** V06 − V05 is flat on the live pool at both seeds but large off-pool: +0.067 expected score, +7.3 %
   economy, +13 % dragons and +14 % length at r100 on the 29-map generalisation panel. The V06 finding's "+12.9 %
   dragons at r100" does **not** reproduce on the pool with this scorecard (+0.011 at seed 1, −0.025 at seed 2),
   although the seed-1 games are identical (same W–L, 122–38). It does appear, at the same size, on the unseen maps.
2. **The CPU wall is not reachable by this search design.** The worst turn is 8.5 M points at L0 and 9.3 M at L3 (8×).
   Even with every cap unbounded (whole-map target search, unbounded flood, frontier depth 1000) it is **22.4 M**
   (Big Empty, seat B). The 100 M cap and the 60 M screening wall are not constraints on Ares's search. Most of each
   turn's points is the judge's fixed write cost.
3. **The slope is not "more is better".**
   - The ladder raises the late economy at every level: pearls at r250 are +0.11 to +0.13 of the field median, and
     most of that is already there at 2×.
   - It lowers the win rate at every level: −0.106, −0.087 and −0.037 expected score at 2×, 4× and 8×.
   - From 4× it also costs the opening.
   - None of the ladder levels passes the gate.
4. **One knob carries the whole effect, and it depends on the phase of the game.**
   - The target-search node cap alone at 8× reproduces L3 to within 0.005 on every tier 1 metric. The flood caps and
     the sprint threshold are inert at this scale.
   - The damage comes from searching wide in the first 40 rounds; the gain comes from searching wide after them.
   - **`lune-r1-07-latecap8x-only`** raises only the cap after round 40, from 48 to 384. Its opening is unchanged,
     and it keeps most of the late gain. Over seeds 1+2 on the pool: economy +0.026, dragons@100 +0.053, length@100
     +0.046, all four death rates −2 %, win rate −0.016 (n.s.).
   - On the generalisation panel: economy +2.5 %, dragons +2.7 %, length +3.3 %, identical W–L.
   - This is the recommended level.
5. **Next lever:** not depth. What the search evaluates (R-5), and *when* it searches wide. Ares already has
   phase guards; the result argues for a phase schedule, and later a continuous selector, over its budgets.

## Method

- **Bots.** `bots/lune-r1-*`, each a params-only copy of V06 with its own `CANDIDATE.toml`.
- **Panels.**
  - z1: the ten live maps against the eight `run_panel.ZOO` opponents, both seats, 160 games per arm per seed.
  - Generalisation panel: `maps/new/*` (20 maps) and `maps/var/*_tr` (9 maps), same eight opponents, both seats,
    464 games.
- **Toolkit.** unswbc 1.2.2, native engine, in the cloud container. The Mac-side VM was OOM-killed under other
  sessions' load, so it ran only the sandbox probes.
- **Scoring.** `tools/lune/score.py` on rows from `tools/lune/run.py`, which uses a copy of the cx arena that also
  emits pearls at r50, r150 and r250 (the cx arena computes them but drops them).
  - Live pool: each side-game is divided by its map's field median in `field_references.json` and then averaged; the
    three-number form comes from the same file and `field_distributions.json`.
  - Generalisation maps have no field reference, so they are divided by the base arm's per-map mean (BENCHMARKS
    §"maps without a reference").
- **Tier 2.** Deaths per 1,000 dragon-turns. `body` is ally + enemy body, because the arena does not split them.
- **Paired tests.** Paired sign tests are on identical (map, seat, seed, opponent) fixtures.
- **Atlas.** `atlas_try()` (`world.hpp:276`) is defined but **never called** in V05 or V06, so the atlas is dead
  code. Both bots as shipped are atlas-off on every map; no switch was needed and none was added.
- **Absolute levels.** The absolute normalised levels here are higher than the V06 finding's (V05 dragons@100 1.28 vs
  1.071) on identical games. The two pipelines count or normalise differently, most likely the replay-snapshot
  extractor against arena reply counts. This is a job for R-4, and deltas are only compared within one pipeline.

## Step 0 — base

| Panel | V06 − V05: exp. score | Econ mean | p@50 | p@100 | p@250 | Dragons@100 | Length@100 | Births@100 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| z1 seed 1 (122–38 vs 118–41–1) | +0.022 | +0.029 | +0.086 | +0.054 | −0.044 | +0.011 | +0.020 | +0.053 |
| z1 seed 2 (122–38 vs 122–38) | +0.000 | −0.002 | +0.016 | −0.022 | −0.003 | −0.025 | −0.013 | −0.015 |
| Generalisation (293–171 vs 262–202) | **+0.067** | **+0.073** | +0.028 | +0.072 | +0.095 | **+0.130** | **+0.138** | +0.082 |

- No tier 2 rate rises (wall −0 to −6 %, self −4 to −5 %, h2h −1 to −4 %). The generalisation-panel length pairs are
  231 better / 191 worse (p = 0.058).
- In three-number form on the pool, V06 sits at roughly the top-ten level: p@100 0.94–1.03 of the top-ten median at
  field percentile 0.55–0.60; dragons@100 0.96–1.04 at percentile 0.59–0.66.
- The retention gain survives off-pool and the economy is not down, so **V06 is the base (`lune-r1-00-base`)**.

## The ladder (z1 seed 1, deltas against L0)

The ladder moves the **target-search node cap** family (`search_cap`, `_saturated`, `_born`, and the late and sparse
guards scaled by the same factor), the room-flood caps and `sprint3_limit` as the table in the prompt specifies.
Two related knobs stay fixed:

- `search_depth1` is declared but unused (dead).
- `frontier_search_depth` (4) only gates the value-bound early exit.

The BFS therefore has one budget knob: the node cap.

| Arm | W–L | Exp. score | Econ mean | p@50 | p@100 | p@150 | p@250 | Dragons@100 | Length@100 | Births@100 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| L0 (V06) | 122–38 | 0.762 | 1.240 | 1.084 | 1.261 | 1.302 | 1.314 | 1.293 | 1.224 | 1.271 |
| L1 ×2 | 105–55 | −0.106 | +0.027 | −0.028 | +0.012 | +0.018 | +0.107 | +0.017 | +0.006 | +0.015 |
| L2 ×4 | 108–52 | −0.087 | +0.006 | −0.051 | −0.037 | −0.004 | +0.116 | −0.040 | −0.047 | −0.040 |
| L3 ×8 | 116–44 | −0.037 | +0.007 | −0.050 | −0.045 | −0.009 | +0.133 | −0.025 | −0.030 | −0.047 |
| cap ×8 only | 116–44 | −0.037 | +0.009 | −0.050 | −0.045 | −0.008 | +0.138 | −0.026 | −0.030 | −0.047 |
| **late cap ×8 only** | 115–45 | −0.044 | **+0.031** | +0.002 | −0.002 | +0.024 | +0.099 | **+0.050** | **+0.050** | −0.004 |

Tier 2 per 1,000 dragon-turns (change against L0):

| Arm | Wall | Self | Body | h2h | Dragons@100 pairs (better/same/worse) | Length@100 pairs |
|---|---:|---:|---:|---:|---|---|
| L0 | 9.54 | 6.64 | 3.59 | 6.02 | – | – |
| L1 | −5 % | +3 % | −1 % | −2 % | 74/16/70 | 80/5/75 |
| L2 | −2 % | +6 % | +4 % | −8 % | 74/18/68 | 77/8/75 |
| L3 | −8 % | +4 % | −1 % | −8 % | 69/19/72 | 73/7/80 |
| cap ×8 only | −5 % | +4 % | +3 % | −7 % | 68/19/73 | 74/7/79 |
| late cap ×8 only | −2 % | +2 % | −3 % | −3 % | 75/27/58 (p = 0.17) | **88/11/61 (p = 0.033)** |

The flood-only, sprint-only and whole-map late-search arms are in §Addendum.

### Why wide search hurts the opening and helps later

- **Cap-binding rate.** An instrumented copy logged why the target BFS stopped (Schooltime + Big Empty vs Fenrir, about
  33 k decisions per level). It stopped on the node cap in **79 % of decisions at L0**, 67 % at L1, 52 % at L2 and
  17 % at L3; the rest stopped on the value bound (`vmax·γ^t ≤ best`).
- **V06's 160-node cap only applies in the first 40 rounds.** After that `search_cap_late = 48` binds (80 % of late
  decisions). Late in the game the nearby pearls are gone; with a 48-cell horizon a dragon falls back to a remembered
  pearl or a sector heuristic, while with 384 it finds a real target.
- **The r250 gain and the fall in wall and h2h deaths** come from that late reach.
- **In the opening**, a wide horizon lets several dragons lock onto the same distant high-value pearl or bed and
  travel further. The "an ally head is nearer, yield" rule only applies to visible pearls. Newborns (cap 60 → 480)
  wander instead of eating nearby, so p@50 and p@100 and births drop.
- **Late cap ×8 only removes the opening change.** p@50 and p@100 are within ±0.002 and every hygiene rate falls,
  which confirms that phase split.

### Seat and map-family asymmetry (late cap ×8 only)

- **Seat.** Seat B carries the pool gain at seed 1: dragons@100 +0.106 and length +0.101, with length pairs 51/5/24
  (p = 0.002). Seat A is flat on retention but still gains p@250 (+0.145).
- **Map family on the pool.**
  - It helps on small and medium maps: Trophy dragons@100 19.2 → 23.0; Dilemma 22 → 29 wins over two seeds; Trauma,
    Queen and Devil p@250 up.
  - It costs on the two largest, densest maps: Schooltime (60×40, dragons 47 → 43, p@250 −7 %) and Slithery Fight
    (63×27, p@250 −4 %, 26 → 18 wins).
- **Off-pool the size signal vanishes.** Pearson correlations over the 29 per-map deltas are corr(tiles, Δp@250)
  −0.06, corr(units@100, Δp@250) +0.14, corr(units@100, Δdragons) −0.06. The two largest unseen maps (relay_depots
  1536 tiles, far_harbors 1728) are neutral to positive.
- **So no structure-keyed rule is warranted.** A tile- or unit-count gate fitted to Schooltime and Slithery would be a
  pool fit, which the OOS rule forbids.

## CPU (sandbox judge pricing, vs V06, both seats)

Fixtures: Schooltime, Portals, Trauma, Big Empty, and the three densest `maps/new` maps by units at r100 (far_harbors
78.5, relay_depots 74.8, equatorial_belt 56.8) — 14 games per level, judge points per turn:

| Level | p50 (median of games) | p99 (max over games) | Max turn | Boot-turn max | Worst fixture | Timeouts/crashes |
|---|---:|---:|---:|---:|---|---:|
| L0 | 4.60 M | 7.54 M | 8.52 M | 8.52 M | Schooltime A | 0 |
| L1 | 4.67 M | 7.56 M | 8.62 M | 8.45 M | Schooltime A | 0 |
| L2 | 4.80 M | 7.69 M | 8.71 M | 8.66 M | Schooltime A | 0 |
| L3 | 4.97 M | 7.80 M | 9.31 M | 9.05 M | Schooltime A | 0 |
| All caps unbounded (probe `lune-r1-09-cpu-maxsearch`) | 7.44 M | 18.32 M | **22.42 M** | 12.50 M | Big Empty B | 0 |

- **The wall.** The 60 M wall is not reached, and the design's ceiling is ~22 M, because the search is bounded by the
  map and by the value-bound prune, not by the budget.
- **Headroom.** Late cap ×8 costs no more than L3 (it is a subset of L3's caps).
- **Search efficiency is not needed.** Move ordering, incremental state and cheaper flood are not the next lever;
  there is no wall to push against.
- **Meter breakdown.** `tools/cx/meter.py` does not apply: Ares's `main.cpp` has no `ANNA_MEASURE` hooks. The L0 →
  unbounded delta (+2.8 M at p50, +14 M at the worst turn) is the upper bound on what the search itself can cost.

## What to read from it

- **Slope.** The slope is phase-dependent, and flat or negative in aggregate. The late economy gain saturates by 2×;
  the opening loss appears at 4× and above.
- **Next lever.** The next lever is not depth but *what and when*:
  - what the target search values (R-5's tuner over the evaluation weights);
  - a phase schedule of the budget. The late cap is one such phase parameter, and the round-40 boundary is itself a
    parameter the tuner should own.
  - The lead's framing — bifurcate performance by phase, then select by a discrete phase or a continuous selector —
    is what these numbers support. The obvious continuous selector is a cap scaled by observed local pearl sparsity
    (pearls seen within the last search's horizon) rather than by the round. It is observable and not keyed to any
    map.
- **Retention or economy.** It is both, and small:
  - V06's own gain is retention and shows up off-pool.
  - Late cap ×8's is retention plus late economy, with p@50 and p@100 untouched.
- **Shape of the gate.** It is partly the wrong shape for a search gain. It averages four checkpoints of which the
  first two cannot move under a late-phase change, so a late-only change has to move p@150 and p@250 by about +0.1
  each to clear +0.05. A phase-aware gate would score the checkpoints in the phase that was changed. That is a
  proposal to the director, not applied here.
- **Seat and family.** The pool gain is seat-B-heavy. The pool's two big dense maps lose, but that does not reproduce
  off-pool, so there is no structure-keyed rule.

## Recommendation

**`lune-r1-07-latecap8x-only`** (parent `lune-r1-00-base` = V06):

- The only change is `search_cap_late` 48 → 384 and `search_cap_sparse` 64 → 512; the opening is unchanged.
- Against the BENCHMARKS gate on the pool over seeds 1+2:
  - economy +0.026, below +0.05;
  - dragons and length at r100 rise (+0.053 / +0.046);
  - no tier 2 rate rises more than 10 % (all within ±2 %);
  - win rate −0.016 (239–81 vs 244–76, n.s.).
- It therefore does **not** formally pass the local gate, the same position as V06. It is the only arm in this task
  that improves every tier 1 checkpoint from r100 on, on both panels, with no hygiene cost and identical off-pool W–L.
- It is **ready for `register.json` as a dev-screen candidate**, with `lineage = "lune"`, `lineage_parent =
  "lune-r1-00-base"` and `CANDIDATE.toml` in the bot directory. It is not registered here.
- It is also the natural host for R-5: the tuner should treat `search_cap_late` and `search_cap_late_from` as two
  more weights.

## Artifacts

| Kind | Where |
|---|---|
| Bots | `bots/lune-r1-00-base` … `lune-r1-08-latecap-wholemap`, plus the probe-only `lune-r1-09-cpu-maxsearch` |
| Raw rows | `game_stats/runs/r1-*.jsonl`: step 0 `r1-step0-*`, ladder `r1-L{0..3}-*`, decomposition `r1-D-*`, CPU `r1-probe-*` |
| Tools | `tools/lune/{run,arena_lune,score}.py` |
| Status | `claude/r1-status.md` |

Superseded partial runs are in `game_stats/runs/stale/`; they lacked the r50, r150 and r250 checkpoints.

## Addendum — remaining decomposition runs (z1 seed 1, deltas against L0)

| Arm | W–L | Econ mean | p@50 | p@100 | p@250 | Dragons@100 | Length@100 | Paired dragons / length@100 | Tier 2 |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| flood ×8 only (`lune-r1-05`) | 122–38 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 | +0.000 | 0/160/0 · 0/160/0 | all within ±1 % |
| sprint ×8 only (`lune-r1-06`) | 120–40 | −0.001 | +0.000 | +0.000 | −0.005 | +0.000 | +0.000 | 0/160/0 · 0/160/0 | all within ±1 % |
| late cap ×8 only (`lune-r1-07`) | 115–45 | +0.031 | +0.002 | −0.002 | +0.099 | +0.050 | +0.050 | 75/27/58 · 88/11/61 | −3 to +2 % |
| late cap whole map (`lune-r1-08`) | 116–44 | +0.031 | +0.002 | −0.002 | +0.099 | +0.050 | +0.050 | 75/27/58 · 88/11/61 | −3 to +2 % |

- **Flood caps.** They are inert at this scale. Every fixture is identical through r100, and only a handful of late
  decisions differ. `flood_need` caps the room requirement at `len + 3 + len/3`, so the 24/40 → 64/112 change binds
  only for dragons longer than about 28, which are rare and late.
- **Sprint threshold.** It is also inert through r100: every fixture is identical. The only differences are after
  r250 (two win flips, p@250 −0.005). This **refutes** the earlier hypothesis that the 3-step sprint threshold
  explains the opening loss. The opening loss is all target-search reach (the "cap ×8 only" row).
- **Late cap saturation.** The late cap saturates by 384. Removing it entirely changes one game's result and no
  tier 1 metric at 3 d.p., so the value-bound prune stops the late search before 384 cells in practice. The late-cap
  slope lies between 48 and 384. The next measurement for R-5 is the small end (96 and 192) and the phase boundary
  (`search_cap_late_from`, now 40), not larger values.
- **Verdict.** The recommendation is unchanged: `lune-r1-07-latecap8x-only`. `lune-r1-08` behaves the same and has no
  cap left to bound it, so 07 is the safer choice.
