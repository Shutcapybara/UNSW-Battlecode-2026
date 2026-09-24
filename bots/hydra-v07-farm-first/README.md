# hydra-v07-farm-first

hydra-v06-echo with one change: **gossip chases are gated on strength**
(`units >= 6 && length >= 4`). A short or lone dragon farms and splits
instead of converging on stale sonar sightings; the pack hunts only once
the swarm has numbers and the hunter has breeding length.

## Why

Autopsy of the v06 field run vs fry-v14 (26 games, 11-2-13) and verbose
Colloseum replays:

- Losses are a pure **numbers war**: head-to-head kills are symmetric
  (12 vs 12), but fry split 28 times while hydra split 9. fry compounds,
  hydra flatlines at 3-5 dragons and dies by elimination around r60.
- hydra's gossip chase sits *before* the SPLIT branch in `body()`, so on a
  small arena (everything within 6 path steps of a sighting) dragons are in
  attack mode nearly every turn, never farm, and die at length 2-3. fry has
  no gossip layer, so between rare visible-bigger-head attacks it farms.
- On maps where hydra's economy did run (devil as A: 54 units), v06 won.
  The chase itself bought no extra kills: fry's death count was identical
  with and without hydra pack-hunting.

Expected effect: when outnumbered, hydra behaves like fry (farm, split,
replace) until it reaches parity, then re-enables coordinated hunting.

## Lineage

- hydra-v06-echo: parent (hunter-v03 + protocol 3 sonar layer).
