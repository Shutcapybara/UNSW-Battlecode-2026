# avery-v11-maze-sweep

**Lineage:** Avery · **Parent:** `bots/avery-v08-crown-race` ·
**Status:** measured, **rejected** (net-negative on shared maps).

## Hypothesis and change vs v08

v09 showed frontier exploration fixes trauma (+3) but regresses open maps
(−8) when it *replaces* the zone waypoint. v11 keeps v08's waypoint first
and fires the frontier sweep only when the waypoint is **BFS-unreachable**
(the actual maze condition): idle fallback order is waypoint-if-reachable →
best exploration cell (staleness + full `w_frontier` per unknown side +
0.3 distance + jitter) → old manhattan gradient.

## Measured results

Native gauntlet, **13 maps** (autarky + dilemma appeared in `maps/` mid-cycle;
156 games): `experiment_data/avery-v11-maze-sweep_20260925134937530609`
(run id `a9abf9c3e6884926b9ddc7f34f4302fc`). **105–50–1**, runtime_faults=0.

On the 11 maps shared with v08's run: **94–37–1** vs v08's 100–31–1 —
rejected.

| Map | v11 | v08 |
|---|---|---|
| trauma | **8–4** | 5–7 (fix confirmed again) |
| trophy | 8–4 | 7–5 |
| devil | 8–4 | 11–1 |
| queen_of_spades | 10–2 | 12–0 |
| schooltime | 10–2 | 12–0 |
| big_empty | 7–5 | 9–3 |
| default | 11–1 | 12–0 |
| autarky (new) | 9–3 | — |
| dilemma (new) | 2–10 | — |

## Why rejected

"Waypoint unreachable" is not maze-specific: the 160-cell forward BFS
regularly misses distant zone centres on big maps (qos 875, big_empty 4096
cells), so the sweep preempted the waypoint exactly where v08's
gradient-following worked. The sweep's gain is real but confined to trauma;
its cost is diffuse. v12 tries gating the sweep by starvation instead.
