# bokuto-35-knownbeds vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 225 | 226 |
| L | 47 | 46 |
| D | 0 | 0 |
| win | 0.8272 | 0.8309 |
| reached | 172 | 146 |
| q_cond | 0.5058 | 0.0000 |
| q_joint | 0.3199 | 0.0000 |
| q_dec_W | 85 | 0 |
| q_dec_L | 4 | 5 |
| conv | 0.8547 | 0.8082 |
| pearls@50 | 45.7022 | 42.3088 |
| pearls@100 | 130.8382 | 126.0441 |
| pearls@150 | 227.7574 | 215.8162 |
| pearls@250 | 431.9816 | 395.0735 |
| units@100 | 29.4779 | 28.4816 |
| total@100 | 75.8566 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -0.37 [-5.15, +4.78] |
| econ | +48.70 [+20.95, +78.72] |
| econ_med | +2.15 [-2.52, +7.29] |
| units@100 | -3.90 [-6.25, +0.00] |
| total@100 | +2.00 [-1.10, +4.76] |
| q_joint | +31.99 [+26.82, +37.87] |
| q_cond | +50.58 [+43.20, +58.49] |
| conv | +4.64 [-2.32, +12.19] |
| death_wall_per1k | -2.54 [-3.78, -1.41] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -0.37 [-4.78, +4.41], econ~ +2.15 [-1.23, +6.19], units@100 -3.90 [-5.44, +0.00], total@100 +2.00 [-0.86, +4.17].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 4.677 | -35.2% |  |
| death_self_per1k | 3.585 | 4.623 | +28.9% | **yes** |
| death_ally_body_per1k | 1.563 | 2.210 | +41.4% | **yes** |
| death_h2h_ally_per1k | 1.238 | 2.009 | +62.3% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -6.25 | -7.81 | +16.96 | -0.244 |
| B | 80 | -6.25 | +21.24 | +47.50 | +0.186 |
| C | 48 | +18.75 | +242.06 | +41.67 | -10.358 |
| D | 16 | +31.25 | +1.18 | +62.50 | -0.462 |
| E | 16 | -18.75 | +49.08 | +0.00 | -10.796 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 10-6 | -25.00 | +71.92 | 7/16 vs 0/16 | +1.992 |
| live/autarky | A | 16 | 14-2 | -12.50 | +1.77 | 5/9 vs 0/3 | +0.110 |
| live/default | A | 16 | 13-3 | +0.00 | +28.47 | 7/15 vs 0/5 | +0.072 |
| live/devil | A | 16 | 14-2 | -6.25 | +2.07 | 0/0 vs 0/0 | -0.270 |
| live/dilemma | C | 16 | 15-1 | +0.00 | -48.27 | 3/4 vs 0/2 | -2.155 |
| live/islands | B | 16 | 15-1 | -6.25 | +19.16 | 4/15 vs 0/12 | -0.851 |
| live/maze | B | 16 | 14-2 | -6.25 | +5.81 | 3/16 vs 0/15 | +0.342 |
| live/portals | E | 16 | 9-7 | -18.75 | +49.08 | 0/15 vs 0/14 | -10.796 |
| live/queen_of_spades | A | 16 | 13-3 | -18.75 | -33.66 | 4/5 vs 0/3 | -1.434 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +21.70 | 15/15 vs 0/16 | +0.081 |
| live/slithery_fight | D | 16 | 15-1 | +31.25 | +1.18 | 10/16 vs 0/16 | -0.462 |
| live/stripes | A | 16 | 5-11 | +0.00 | -46.05 | 1/1 vs 0/2 | +1.083 |
| live/tower_defense | A | 16 | 14-2 | -6.25 | -17.89 | 2/3 vs 0/3 | -1.474 |
| live/trauma | C | 16 | 16-0 | +18.75 | +833.60 | 12/15 vs 0/16 | +0.598 |
| live/trophy | A | 16 | 15-1 | +0.00 | +10.61 | 0/0 vs 0/0 | +0.200 |
| live/unsw | B | 16 | 13-3 | -6.25 | -12.41 | 9/16 vs 0/16 | -0.636 |
| live/weakhold | C | 16 | 14-2 | +37.50 | -59.16 | 5/11 vs 0/7 | -29.517 |

Runtime / fingerprint: cand `unswbc 1.2.3` `71021e11586e` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

