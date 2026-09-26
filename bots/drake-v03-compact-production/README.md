# drake-v03-compact-production

**Lineage**: Drake. **Parent**: `bots/drake-v02-hunt-feed/`.
**Borrowed**: v02's credits apply. New: the compact-map doctrine
(unconditional split / nearest-food / supported strikes) follows
ouroboros-v13-ladder's published compact ladder and tew-v12's
support-count attack gate; fast-bed learning is Drake's own.

## Hypothesis

The expanded-roster losses are concentrated on compact maps
(arena/default_small/Colosseum/devil), where the winners run 2-4x more
dragings than v02's 12-unit cap, claim food faster per dragon-turn, and
attack with local support.  Fix production tempo, food claiming and
supported aggression on compact maps; keep big-map behavior.

## Changes from v02

- **Five team-size tiers** (tiny 16 / small 18 / compact 28 / mid 36 /
  big 56 by cell count).
- **Compact doctrine** (NC <= 650): unconditional split at len >= 4 while
  below target (danger/crowd gates bypassed; legality kept), nearest-food
  target override, support-gated strike bonus (ally heads >= enemy heads
  within 4 tiles, tew's gate), wider strike-candidate horizon, 4x ally
  repulsion.
- **Fast-bed learning**: beds with countdown <= 40 are marked productive
  (maps are bimodal: default_small's median bed period is ~528 rounds) and
  radioed; `nearest_food()` only chases pearls and fast beds; camping
  bonus beside a fast bed about to spawn; anti-dither visit penalty
  capped at 8.
- **Dispersion**: children get a colonisation mission (stalest
  de-congested zone) with a 40-round committed goal, not the parent's
  local food target.
- Nearest-food override also on mid maps (NC <= 1300) with a <= 10 tile
  distance gate.

## Measured results

Full shared roster (242 games):
run `experiment_data/drake-v03-compact-production_20260925071822661087`.

**Total: 80 W - 1 D - 161 L, score 0.333** (v02: 0.205 on the same roster).

| Opponent | W-D-L | vs v02 |
| --- | --- | --- |
| ouroboros-v10-beacon | 6-0-16 | +3 |
| hunter-v14-cpp-hybrid-route-spacing | 14-0-8 | +5 |
| hunter-v20-portal-scouts | 11-0-11 | +2 |
| fry-v14-stateful-size-aware-3 | 16-0-6 | +7 |
| kraken-v04-eval | 12-1-9 | = |
| tew-v07...v12 (6 versions) | 21-1-100 combined | +14 |

Map swings: queen_of_spades 20-0-2, default_small 11-0-11 (was 4-18),
devil 4-0-18 -> fry there 2-0; big_empty 3-0-19 stays the weak map -
every loss is a round-500 crown race vs ouroboros-class endgames
(my longest 33-37 vs their 49-68).  All six tew versions play
action-identical to ouroboros-v10 on open maps, so those 12 losses are
the same phenomenon.

Compact mini-screen vs fry-v14/hunter-v20/tew-v12 on 4 compact maps:
7-17 (fry 4-4, hunter-v20 1-7, tew-v12 1-7).

Direct v03-vs-v02: wins on big_empty and schooltime.

## Diagnostics that drove the changes

- devil v02 loss: 43 splits in 340 rounds vs hunter-v14's 531 - a
  production deficit, not combat (deaths were even).
- default_small probe: beds bimodal (min 5 / median 528 / max 980 rounds),
  so "every tile is a bed" is false economy; only fast beds matter.
- Trace of v02 on default_small: founders saw zero pearls for 9 rounds
  and clustered in the spawn corner; dispersion missions + fast-bed
  knowledge came from that evidence.

## Sandbox / judge checks

Not yet re-run (compute deltas: fastbed bytearray, small dict scans; the
compact nearest_food scan is bounded by known beds).  v01's headroom
stands as the reference; re-check before submission.
