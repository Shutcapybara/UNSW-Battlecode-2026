# C2-0 — fight anatomy: is coordinated fighting worth building?

Generated 2026-09-29T12:22:41Z from the public corpus (ranked completed games; both sides pooled; no submission ids — pooled by team). 182788 contact events over 10331 games; side-game universe per cohort in the JSON `_meta.universe`. Definitions as in `tools/analysis/features/fights.py` (Manhattan contact <= 4, window 6, group >= 3, 5-round closure, adjacency-based initiator, deaths to last contact + 5).

## Pooled, group-class fights per cohort

| cohort | side-games | fights/game | initiator share ±ci | trades | kill-for | kill-against | disengage | own deaths/fight | own len lost/fight | trade ahead share | conv ratio | conv>=2 share | synced entries | rays/head pre | pearl Δ next10 | bed flip |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| top 10 | 1910 | 8.97 | 53.6% ±2.1% | 35.6% | 14.4% | 10.9% | 39.2% | 6.42 | 18.2 | 55.1% | 0.29 | 83.6% | 22.8% | 2.66 | 1.08 | 34.5% |
| ranks 11-30 | 3101 | 9.41 | 49.4% ±1.7% | 33.6% | 12.8% | 14.6% | 39.1% | 7.18 | 19.0 | 46.5% | 0.26 | 80.7% | 22.5% | 2.76 | 2.77 | 31.2% |
| band 55-85 | 6534 | 8.59 | 49.9% ±1.2% | 33.0% | 12.9% | 13.3% | 40.8% | 6.84 | 18.9 | 44.2% | 0.27 | 80.6% | 23.8% | 2.48 | -0.81 | 34.8% |
| team 7 | 114 | 7.55 | 48.3% ±10.5% | 30.9% | 13.8% | 12.3% | 43.0% | 11.6 | 32.9 | 42.5% | 0.18 | 81.9% | 26.2% | 2.66 | 4.01 | 29.2% |

## Contact classes per side-game

| cohort | group | 2v1 | 1v1 | 2v2 | pair | 1v1 initiator share |
|---|---|---|---|---|---|---|
| top 10 | 8.97 | 0.36 | 8.85 | 0.06 | 0.00 | 51.3% |
| ranks 11-30 | 9.41 | 0.34 | 8.41 | 0.06 | 0.00 | 48.3% |
| band 55-85 | 8.59 | 0.35 | 8.63 | 0.06 | 0.00 | 50.8% |
| team 7 | 7.55 | 0.30 | 8.86 | 0.04 | 0.00 | 47.1% |

## Win rate conditional on group-fight outcome (per side-game)

- **top 10**: net_even: 65.5% (n=759); net_kill+: 66.8% (n=621); net_kill-: 58.1% (n=454); no_group_fight: 72.4% (n=76)
- **ranks 11-30**: net_even: 53.4% (n=1155); net_kill+: 52.3% (n=864); net_kill-: 57.0% (n=949); no_group_fight: 54.9% (n=133)
- **band 55-85**: net_even: 47.3% (n=2433); net_kill+: 47.3% (n=1873); net_kill-: 47.6% (n=1981); no_group_fight: 44.9% (n=247)
- **team 7**: net_even: 68.6% (n=51); net_kill+: 54.8% (n=31); net_kill-: 66.7% (n=30); no_group_fight: 50.0% (n=2)

## Era split (group fights)

| era | cohort | n | share | initiator | trades | conv ratio |
|---|---|---|---|---|---|---|
| early | top 10 | 6335 | 37.0% | 52.2% | 46.5% | 0.16 |
| early | ranks 11-30 | 9705 | 33.3% | 49.0% | 42.6% | 0.13 |
| early | band 55-85 | 18471 | 32.9% | 49.4% | 41.5% | 0.13 |
| early | team 7 | 287 | 33.3% | 42.9% | 41.5% | 0.08 |
| mid | top 10 | 6135 | 35.8% | 53.4% | 30.4% | 0.52 |
| mid | ranks 11-30 | 10382 | 35.6% | 50.0% | 28.9% | 0.46 |
| mid | band 55-85 | 20515 | 36.6% | 50.1% | 29.4% | 0.46 |
| mid | team 7 | 312 | 36.2% | 48.0% | 26.3% | 0.48 |
| late | top 10 | 4665 | 27.2% | 57.5% | 27.6% | 0.67 |
| late | ranks 11-30 | 9078 | 31.1% | 49.5% | 29.4% | 0.61 |
| late | band 55-85 | 17113 | 30.5% | 50.5% | 28.0% | 0.64 |
| late | team 7 | 262 | 30.4% | 69.2% | 24.8% | 0.68 |

## Geometry (top 10 vs band, group fights; no map identity)

- **corridor_degree**: open>0.75: top10 init 54.8% conv 0.34 (n=11957) vs band init 49.5% conv 0.30 (n=38293); tight<=0.75: top10 init 50.2% conv 0.22 (n=5178) vs band init 50.7% conv 0.22 (n=17806)
- **open_ratio**: open>=0.75: top10 init 51.5% conv 0.33 (n=3600) vs band init 51.7% conv 0.30 (n=10559); tight<0.75: top10 init 54.4% conv 0.28 (n=13535) vs band init 49.2% conv 0.26 (n=45540)
- **bed_dist**: bed3-6: top10 init 54.0% conv 0.36 (n=3834) vs band init 50.1% conv 0.36 (n=12137); bed<=2: top10 init 53.6% conv 0.28 (n=12739) vs band init 49.8% conv 0.25 (n=42103); bed>6: top10 init 38.5% conv 0.39 (n=562) vs band init 54.8% conv 0.36 (n=1859)
- **portal3**: no_portal: top10 init 54.4% conv 0.30 (n=12319) vs band init 49.5% conv 0.27 (n=41014); portal<=3: top10 init 51.6% conv 0.28 (n=4816) vs band init 50.7% conv 0.28 (n=15085)

## Map class (descriptive only)

- compact / top 10: n=4335, 2.27/game, initiator 51.2%, trades 44.4%, conv 0.26
- compact / band 55-85: n=15312, 2.34/game, initiator 49.4%, trades 35.8%, conv 0.22
- compact / team 7: n=196, 1.72/game, initiator 36.8%, trades 31.1%, conv 0.12
- open / top 10: n=12800, 6.70/game, initiator 54.3%, trades 32.6%, conv 0.30
- open / band 55-85: n=40787, 6.24/game, initiator 50.0%, trades 31.9%, conv 0.29
- open / team 7: n=665, 5.83/game, initiator 51.5%, trades 30.8%, conv 0.20

## The S-3 comparisons

### top 10 − band 55-85

| metric | top 10 | ±ci | band 55-85 | ±ci | delta |
|---|---|---|---|---|---|
| initiator_share | 53.6% | 2.1% | 49.9% | 1.2% | 3.7% |
| conv_ge2_share | 83.6% | 0.6% | 80.6% | 0.4% | 3.0% |
| trade_share | 35.6% | 0.7% | 33.0% | 0.4% | 2.6% |
| kill_for_share | 14.4% | 0.5% | 12.9% | 0.3% | 1.5% |
| disengage_share | 39.2% | 0.7% | 40.8% | 0.4% | -1.6% |
| group_events_per_game | 8.97 | — | 8.59 | — | 0.39 |
| trade_ahead_share | 0.55 | — | 0.44 | — | 0.11 |
| conv_ratio | 0.29 | — | 0.27 | — | 0.02 |

### team 7 − band 55-85

| metric | team 7 | ±ci | band 55-85 | ±ci | delta |
|---|---|---|---|---|---|
| initiator_share | 48.3% | 10.5% | 49.9% | 1.2% | -1.6% |
| conv_ge2_share | 81.9% | 2.8% | 80.6% | 0.4% | 1.3% |
| trade_share | 30.9% | 3.1% | 33.0% | 0.4% | -2.1% |
| kill_for_share | 13.8% | 2.3% | 12.9% | 0.3% | 0.9% |
| disengage_share | 43.0% | 3.3% | 40.8% | 0.4% | 2.1% |
| group_events_per_game | 7.55 | — | 8.59 | — | -1.03 |
| trade_ahead_share | 0.42 | — | 0.44 | — | -0.02 |
| conv_ratio | 0.18 | — | 0.27 | — | -0.09 |

## Reading

(written at the end of the run — see the JSON for every number behind these lines.)

