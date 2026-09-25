# avery-v03-swarm-spacing

**Lineage:** avery · **Parent:** avery-v02-id-order-corridors.

## Hypothesis

v02's replays showed many dragons converging on the same pearls/rooms:
target selection is near-deterministic, so equidistant allies pile into the
same pocket; growth and traffic then seal it — the dominant
team_kill/self-collision engine. Decisive pearl de-confliction plus a soft
spread drive should cut convergence without hurting foraging.

## Changes vs v02

- `own_disc` 0.3 → 0.1: a pearl an ally head is clearly closer to is almost
  worthless to us.
- New spread term: reward distance from the nearest recent ally self-report
  (≤ 3 rounds, ≤ 12 tiles), `w_spread=0.25`, capped at 8 tiles.
- `w_crowd` 0.20 → 0.30.

## Results

Gauntlet run `experiment_data/avery-v03-swarm-spacing_20260925052848926144`
(native, both sides, 11 maps; the shared `comparison.toml` had been extended
by the tew line to 8 opponents, 176 games — tew rows excluded below for
v01/v02 comparability).

| Opponent | W–L–D | v02 | v01 |
|---|---|---|---|
| ouroboros-v10-beacon | **16–6** | 11–11 | 8–11 (+3 TO) |
| hunter-v14-cpp | 12–10 | 16–6 | 14–8 |
| hunter-v20-portal-scouts | 13–9 | 12–10 | 11–11 |
| fry-v14 | 15–7 | 15–7 | 17–5 |
| kraken-v04-eval | 18–3–1 | 16–5–1 | 16–5–1 |
| **gauntlet-5 total** | **74–35–1 (67.7%)** | 70–39–1 (64%) | 66–40–1 (62%) |
| tew-v07/v08/v09 | 9–13 each | — | — |

Death attribution vs v02 (same 110 games): team kills 5939 → 5456,
self-collisions 1813 → 1691, total deaths 12183 → 11700, pearls ~flat,
splits 14032 → 13698. Convergence reduced but not eliminated.

**Loss profile:** 20 of 36 losses were round-500 rulings; 19 of those 20 on
the longest-dragon tiebreak (13 by ≤ 6 segments). This motivated v04's
crown/endgame module. The tew line beats v03 13–9 consistently — open
question for v05+ (likely early-economy/hunting differences; not yet
diagnosed with replays).
