# yeji-s06-onlinebeds

**Lineage:** Yeji. **Parent:** `yeji-s05-young`. **Status:** frozen, **not evaluated** — superseded by the host decision below.

Map prior off (`map_prior` 0, no `mapprior.py`): tournament maps are out of sample. Adds online fast-bed learning (`online_beds`): the largest countdown a dragon has seen at a bed bounds its gap; beds whose bound stays ≤ `online_fast_max` (40) feed the same target (`w_bed_prior`) and waypoint (`w_zone_bed`) terms the prior fed. No map data.

Not panelled: the held-out panel (10 synthetic maps in `maps/new/`, 5 references) showed the whole v10 family at 0.18–0.23 against `yuna-v03-core` 0.42, so iteration moved to the yuna host. See `docs/findings/2026-09-29-yeji-s01-swarm-dissolve.md` (addendum 2).
