**Prefer the package:** `unswbc` ≥ 1.2.6 ships these maps in `unswbc/templates/maps/` (1.2.9 adds the seven
non-ladder maps; the engine is byte-identical to 1.2.3). These extractions are a cross-check.

# Live map versions (post 2 Oct 03:49Z), extracted from corpus replays by Shenzhen

The server replaced six maps on 2 Oct 2026 between 03:45:52Z and 03:49:02Z. The repo's `maps/*.map` are the **old**
versions. These files are the map text embedded in live replays (the engine's own map), one per `map_hash` (two seat
orientations per map; PD and Schooltime have four), with `END` appended to match the repo format.

| file stem | what changed vs maps/ |
|---|---|
| autarky__* | dragon order: queens (ids 0/1) are now 3-long open dragons, not the 14-long pocket column |
| slithery_fight__* | dragon order: queens are now the 25-long coils, not the 7-long dragons |
| dilemma__* | dragon order (queens 3-long, not 11-long) and two dragons removed |
| trophy__* | queen spawns moved (y 2 → 9); four edges |
| schooltime__* | 20 edges: each queen spawns 4-long inside a closed 2×2 cage |
| default__* | four edges |

Devil, Portals, Queen Of Spades and Trauma did not change. Before using these in a panel, confirm the local `unswbc`
loads and runs them (`unswbc` map parser); they parse with `tools/hub/vendor/*/mapview.load_map`.
Source: `docs/findings/2026-10-04-shenzhen-live-queen-and-map-swap.md` §1.
