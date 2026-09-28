# chaewon-s02-atlas

Parent `chaewon-s01-swarm-dissolve` (same params: prod_on 1, diss_on 1, plus `diss_dist 2`).

- **Atlas** (`atlas_<W>x<H>.py`, built by `tools/chaewon/build_atlas.py` from `maps/*.map`): the terrain of the ten
  public maps ships with the bot. On its first turn each process compares every edge of its 7×7 view with the
  candidates of its map size; a unique exact match loads every edge, portal pair and bed (`LOG ACT:atl`). Unknown or
  transformed maps match nothing and keep s01 behaviour. Consumers: routing, doom/trap tests (Portals' 1-cell portal
  pockets become visible dead ends), no blind dives, bed targets replace frontier targets.
- A dead end counts as a "farm" only if its region has ≥ `farm_min_region` (3) cells.
- Blind portal landings priced `p_blind × V(me)` (+`w_blind_near` if an ally/enemy head was reported near the landing, ×2 for the crown).
- Escorts pay `w_flank` for ending next to the crown's body.

Screen (5 small live maps × 2 sides × {sinbad-v07, yuna-v02}, seed 1, 20 paired fixtures): **+0.150 vs s01**
(4 better / 1 worse), score 0.40 vs 0.25; units r100 18 vs 11.
