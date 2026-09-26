# drake-v07-soft-missions

**Lineage**: Drake. **Parent**: `bots/drake-v06-frontier-push/`
(= v04-beacon + the unit-pressure frontier push).
No new borrowings.

## Hypothesis

v06's fixture analysis showed the ouroboros economy gap is built in
rounds 40-70, not the opening (r0-40 even at 30v33 pearls, then 30->40
vs 33->57 by r50 at equal population).  That is exactly when the first
big child cohort walks its 40-round colonisation missions: on
sparse-pearl maps the forward BFS rarely finds food, so nothing
interrupts the trek and the children do not eat for dozens of rounds.

## Changes from v06

- Birth-mission commitment: 40 rounds -> `mission_life=15`.
- Missions now yield whenever food is known within
  `mission_food_break=10` tiles (pearls or fast beds, via
  `nearest_food()`), not only when the goal cache happens to expire.

## Measured results

big_empty vs ouroboros-v10 (the diagnosis fixture): **round-100 pearls
247 v 246 — the early economy gap is closed** (v04: 203 v 251).  The
game is still lost on length at r500 (1655 v 1949, both teams'
crowns assassinated to length-4; their total-length bank is bigger).

Full frozen-roster screen (11 opponents x 11 maps x 2 sides = 242 games,
`drake-eval.toml`):
run `experiment_data/drake-v07-soft-missions_20260925125609458906`.

**Total: 89 W - 1 D - 152 L, score 0.370** — the new Drake candidate
(v04: 0.366, v03: 0.333, v02: 0.205).

| Opponent | W-D-L |
| --- | --- |
| ouroboros-v10-beacon | 7-0-15 |
| hunter-v14-cpp-hybrid-route-spacing | 14-0-8 |
| hunter-v20-portal-scouts | 12-0-10 |
| fry-v14-stateful-size-aware-3 | 16-0-6 |
| kraken-v04-eval | 13-1-8 |
| tew-v07...v12 (6 versions) | 27-0-105 combined |

Map movers vs v04: queen_of_spades 21-0-1, hunter-v20 and fry +1 each.

## The unit-pressure frontier push (inherited from v06)

Included and active: pressure = UNITS / team_target(), push mode at
>= 0.90 for small non-crown dragons near the frontier (nearest unknown
cell within 12), group cohesion instead of spread, x0.75 risk tolerance,
no voluntary splits while pushing.  On the roster this feature is
aggregate-neutral (v06 partial was level with v04); it is kept because
it is free, verified firing (~40% of turns on big maps at the cap), and
plausibly load-bearing against expansion-style opponents not in this
roster.

## Remaining gap

Still behind ouroboros-v10/tew (7-15 and ~4-5 each): the r100-300
steady-state gather rate is ~15% per-dragon behind (957 v 1126 on
big_empty), and the r500 mutual-crown-kill endgames resolve on total
length.  Next levers: shorten the goal cache (6 rounds) so stale pearl
targets stop costing rounds; endgame feeding down to fewer, longer
survivors.

## Sandbox / judge checks

`--sandbox` vs ouroboros-v10 on big_empty (worst case), drake as team B
over 22,888 turns: **p50 18.5M, p99 43.9M, mean 22.5M, max 59.5M points
per turn** — under the 100M/turn judge limit with headroom (mirrored run:
ouroboros-v10 at max 68.0M).  One batched stdout write per turn; gc
disabled; no runtime faults across all 242 screen games.
