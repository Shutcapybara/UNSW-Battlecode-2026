# drake-v04-beacon

**Lineage**: Drake. **Parent**: `bots/drake-v03-compact-production/`.
**Borrowed**: v03's credits apply. New: the crown beacon system (K_CROWN
packet, relay TTL, crown demotion, beacon-guided feeding) is ported from
`bots/ouroboros-v10-beacon` — the strongest roster bot.

## Hypothesis

v03's remaining losses concentrate in round-500 crown races against
ouroboros-class endgames (my longest 33-37 vs their 49-68 on big_empty).
Their advantage is coordination: the crown beacons its position team-wide
(relayed a few hops), so the whole team agrees on ONE crown, feeders find
it from far away (range 30, feeders up to length 20), and an outgrown
crown demotes itself.  Without the beacon, distant drakes each believe "no
crown known" and volunteer competing crowns, fragmenting the length bank.

## Changes from v03

- **K_CROWN packet** (cell, length, round; relay TTL 3, belief 6 rounds):
  crowns beacon every second round from `crown_start`.
- **Crown demotion**: a crown that knows a clearly longer crown
  (`crown_demote=3`) steps down to FORAGE.
- **Beacon-guided feeding**: feeders use the freshest crown beacon in
  addition to direct self-reports; feed range 16 -> 30, feeder length
  cap 10 -> 20 (ouroboros-v10's tuned values).

## Measured results

Direct v04-vs-v03 on the crown-race maps: **4-0** (big_empty and
stronghold, both sides).

Compact mini-screen (fry-v14/hunter-v20/tew-v12 on arena/default_small/
Colosseum/devil): 7-17, equal to v03 (fry improved to 5-3, hunter-v20/tew
unchanged) - no compact regression.

Full frozen-roster screen (11 opponents x 11 maps x 2 sides = 242 games,
`drake-eval.toml`):
run `experiment_data/drake-v04-beacon_20260925120001991479`.

**Total: 88 W - 1 D - 153 L, score 0.366** (v03: 0.333, v02: 0.205 on the
same roster).

| Opponent | W-D-L |
| --- | --- |
| ouroboros-v10-beacon | 7-0-15 |
| hunter-v14-cpp-hybrid-route-spacing | 14-0-8 |
| hunter-v20-portal-scouts | 11-0-11 |
| fry-v14-stateful-size-aware-3 | 15-0-7 |
| kraken-v04-eval | 13-1-8 |
| tew-v07...v12 (6 versions) | 28-0-38 combined |

Map movers vs v03: default 6 -> 15, queen_of_spades 19-0-3, tew maps up
across the board.  big_empty stays 2-20: the beacon wins the team-internal
crown race (4-0 vs v03) but ouroboros' 25% pearl-economy lead is the
binding constraint there, not coordination.

## Sandbox / judge checks

`--sandbox` vs ouroboros-v10 on big_empty (worst case), drake as team B
over 22,877 turns: **p50 17.0M, p99 43.9M, mean 21.0M, max 62.2M points
per turn** - under the 100M/turn judge limit with headroom.  One batched
stdout write per turn; gc disabled; no runtime faults in any screen.
