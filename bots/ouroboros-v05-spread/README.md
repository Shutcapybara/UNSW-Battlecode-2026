# ouroboros-v05-spread

v04-race plus traffic and exploration fixes found by death forensics
(`tools/ouroboros/deaths.py`): most of our non-combat deaths were our own
dragons boxing each other in, and whole bases never leaving through
portals whose far end nobody had seen.

## Changes vs v04

- `w_crowd`: per ally segment within 2 tiles of the new head.
- `split_crowd_max`: no voluntary split with more than 10 ally segments in
  view (a newborn in a packed window is a future traffic death).
- `w_zone_crowd`: waypoints avoid zones full of recent ally reports.
- Unpaired portals: cells beside them are exploration targets
  (`portal_explore`) and stepping through is a candidate action ("dive").
- `w_blind_portal`: any portal step landing outside our 7x7 window
  (default's portal deaths were landings on unseen bodies).
- `w_tunnel_unknown` (a known tunnel running on into unseen tiles) and
  `w_doomed` + the K_DOOM broadcast (a dragon that finds every way forward
  is a dead end tells the team where the corridor starts). Both cost devil
  (4-10 with, 7-7 without: its pearls sit in dead-end corridors) but win
  queen_of_spades/help; net +2 on the bench, so they stay on.
- Tried and reverted: `w_blind_portal` (penalise portal steps onto unseen
  tiles: fewer landing deaths on default, but trauma/stronghold need the
  portals: cross-series 97-15 -> 90-22) and caching the waypoint for 4
  rounds (qos 10-0 -> 3-7).
- CPU: destination cache for every cell (invalidated per edge/portal
  change), zone-danger memo, the dead-end test skipped where the flood found
  room and there are two ways on (`doom_skip`), reverse search cap 260.
  Interpreter lines per turn on big_empty: p50 11k -> 9.6k, max 29k -> 25k.

## Results

Bench pool (7 older bots, 14 maps, both sides): 160-34, level with v02-v04
(~0.82) — that pool is saturated.

Cross-series pool (latest bots of the other AI series, 14 maps, both sides):

| opponent | v04-race | v05 (early) |
| --- | --- | --- |
| kraken-v04-eval | 19-9 | 26-2 |
| leviathan-v07-local-cache | 26-2 | 25-3 |
| hydra-v10-farmclean | 19-9 | 24-4 |
| hydra-v09-lanchester | 21-7 | 22-6 |
| **total** | **85-27** | **97-15** |

Trauma 2-12 (v01) -> 13-0; stronghold/trophy/Colosseum up. Still weak:
arena and devil against the C++ swarms.
