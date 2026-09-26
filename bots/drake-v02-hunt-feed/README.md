# drake-v02-hunt-feed

**Lineage**: Drake. **Parent**: `bots/drake-v01-survive-forage/`.
**Borrowed**: v01's credits still apply (ouroboros-v05 world model). New in
this version: endgame feeding mechanics and parameters from
`bots/ouroboros-v09-feed` (no-action death beside the crown, corpse =
`ceil(len/2)` pearls); hunter role weights patterned on ouroboros-v05's
HUNT role.

## Hypothesis

v01's 66 losses split into 36 eliminations by aggressive swarms (no answer
to head-hunters) and 30 round-500 length races (no dragon concentrates
length).  Hunters that trade up and chase radioed enemies blunt the swarms;
small dragons feeding their corpse to the crown turn survival into
length-race wins.

## Changes from v01

- **HUNT role** (FORAGE/HUNT/CROWN) with deficit-based `child_role()` mixes
  by phase and map size; hunters get `w_enemy` target pulls toward radioed
  enemy sightings, `trade_margin=0`, `strike_bonus`, negative danger-zone
  aversion (they patrol hot zones), hot-zone waypoints.
- **Role handoff**: split packets carry (role, target); newborns without a
  handoff default to HUNT.
- **Endgame feeding** (ouroboros-v09 mechanics): from `feed_start=430`, a
  non-crown dragon of length <= 10 that knows a longer crown within 16
  tiles heads for it and at <= 2 tiles emits **no action** (protocol.py
  gained a None-command guard) - the corpse pearls feed the crown.
- Crown minimum length 5 -> 4.

## Measured results

Full shared roster (11 opponents x 11 maps x 2 sides = 242 games; the
roster grew mid-session when the tew lineage joined `comparison.toml`):
run `experiment_data/drake-v02-hunt-feed_20260925065735080044`.

**Total: 49 W - 1 D - 192 L, score 0.205.**

| Opponent | W-D-L |
| --- | --- |
| ouroboros-v10-beacon | 3-0-19 |
| hunter-v14-cpp-hybrid-route-spacing | 9-0-13 |
| hunter-v20-portal-scouts | 9-0-13 |
| fry-v14-stateful-size-aware-3 | 9-0-13 |
| kraken-v04-eval | 12-1-9 |
| tew-v07...v12 (6 versions) | 7-0-115 combined |

On the original 5-opponent subset this is a **wash vs v01** (42-1-67 vs
43-1-66): individual games flipped (big_empty length losses became wins,
arena eliminations got 3x faster) without moving the aggregate.  The newly
added tew lineage (ouroboros-v13-ladder-based compact specialists) beat
v02 1-21 per version and now defines the compact-map problem.

## What this version established

- Feeding works: round-limit losses on big maps flipped to wins
  (big_empty vs fry-v06: loss -> win on length).
- Hunters speed up swarm eliminations (arena vs fry-v06: 156 -> 52 rounds).
- Neither lever fixes compact maps, where production tempo and supported
  attacks decide games (see drake-v03).

## Sandbox / judge checks

Not separately re-run for v02 (compute delta vs v01 is small: one enemies
scan and a few dict lookups per turn; feeding turns are cheaper than full
turns).  v01's measured headroom (max 57.3M of 100M pts/turn) stands.
