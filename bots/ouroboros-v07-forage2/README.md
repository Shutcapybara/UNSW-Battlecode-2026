# ouroboros-v07-forage2

v05-spread plus:

- **Dead-end farming**: `doom()` now reports the pearls inside an enclosed
  region; a dead end is only penalised fully when length + those pearls
  cannot reach `farm_len` (4). Otherwise it is a farm: go in, grow, split,
  the child walks out (`w_doom_farm`).
- **Emergency split**: when every move is fatal, split all but 2 segments
  off so the tail end lives on (`w_emergency_split`).
- `spawn_window` 12 -> 25 (small-map sweep: 48-24 -> 53-19; 18/35 also
  better than 12, 50 worse).

Devil family (devil + transposed + flipped, 4 C++ swarms): v05 3-21, v07
10-14. But bench totals are flat (142-38 vs v05 143-37 on the same
matchups: stronghold/trophy lose what devil gains) and the cross-series
partial run is 49-14 vs v05 53-10. Not promoted; v05-spread stays champion.
