# ouroboros-v10-beacon  (champion)

v09-feed plus **one crown, and everyone knows where it is**.

v09 autopsies (stronghold_T vs kraken-v04) showed five "crowns" of length
2-6 at round 480: a dragon became crown when it had not *heard* of one, and
rays rarely cross a walled map; emergency splits also left 2-segment
crowns behind. Changes:

- Crowns broadcast a relayed position beacon (`K_CROWN`: cell, length,
  round; `beacon_ttl` 3 hops) every other turn from `crown_start`.
- Crown selection counts beacons as well as direct self-reports; a crown
  that learns of one `crown_demote` (3) longer stands down to gatherer.
- An emergency split by a crown hands the crown role to the newborn (it
  carries all but 2 segments).
- Feeding (v09) uses beacons too and is stronger: from round 400, any
  non-crown up to length 20 within 30 tiles of the crown (screen on the
  length-race maps vs kraken-v04 + hydra-v10: 24-8 -> 28-4).

## Results

widefast x cross-series, 261 common matchups: **238-23** (v09 234-27,
v08 219-42, v05 219-42). Per opponent: hydra-v09 56-10, hydra-v10 60-6,
kraken-v04 60-3, leviathan-v07 62-4.

widefast x C++ swarms (fry-v12, fry-v14, hunter-v04), 198 matchups:
161-37 (v09 164-34, v08 156-42, v05 141-57).

64x64 maps vs hydra-v09/v10: 8-0 (help: our crown 186-195 vs 97-111).

Judge CPU (sandbox, big_empty): p50 29M, p99 48M, max 69M points/turn.
