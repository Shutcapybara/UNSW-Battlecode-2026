# bokuto-25-reserve4 vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 242 | 226 |
| L | 30 | 46 |
| D | 0 | 0 |
| win | 0.8897 | 0.8309 |
| reached | 175 | 146 |
| q_cond | 0.4571 | 0.0000 |
| q_joint | 0.2941 | 0.0000 |
| q_dec_W | 77 | 0 |
| q_dec_L | 1 | 5 |
| conv | 0.9029 | 0.8082 |
| pearls@50 | 42.5110 | 42.3088 |
| pearls@100 | 121.8824 | 126.0441 |
| pearls@150 | 212.1949 | 215.8162 |
| pearls@250 | 397.3824 | 395.0735 |
| units@100 | 28.2463 | 28.4816 |
| total@100 | 73.8015 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +5.88 [+1.47, +10.29] |
| econ | -3.37 [-7.53, +0.36] |
| econ_med | -1.58 [-5.34, +0.15] |
| units@100 | -3.12 [-5.88, +0.00] |
| total@100 | +0.00 [-2.48, +3.13] |
| q_joint | +29.41 [+24.26, +34.93] |
| q_cond | +45.71 [+38.73, +53.27] |
| conv | +9.46 [+3.02, +16.39] |
| death_wall_per1k | -1.60 [-2.87, -0.52] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +5.88 [+1.84, +10.29], econ~ -1.58 [-4.53, -0.12], units@100 -3.12 [-4.76, +0.00], total@100 +0.00 [-2.01, +2.12].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.610 | -22.2% |  |
| death_self_per1k | 3.585 | 4.680 | +30.6% | **yes** |
| death_ally_body_per1k | 1.563 | 1.779 | +13.8% | **yes** |
| death_h2h_ally_per1k | 1.238 | 1.142 | -7.7% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -3.57 | -11.45 | +17.86 | +0.120 |
| B | 80 | +5.00 | +5.76 | +38.75 | +0.171 |
| C | 48 | +22.92 | -9.20 | +50.00 | -9.313 |
| D | 16 | +37.50 | -9.51 | +31.25 | -0.652 |
| E | 16 | -6.25 | +31.21 | +0.00 | -0.371 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -6.25 | -1.39 | 8/16 vs 0/16 | +0.419 |
| live/autarky | A | 16 | 15-1 | -6.25 | -12.17 | 5/6 vs 0/3 | -0.113 |
| live/default | A | 16 | 11-5 | -12.50 | -13.92 | 7/12 vs 0/5 | -0.009 |
| live/devil | A | 16 | 16-0 | +6.25 | +9.65 | 0/0 vs 0/0 | +1.362 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +1.46 | 7/8 vs 0/2 | +0.258 |
| live/islands | B | 16 | 16-0 | +0.00 | +1.89 | 2/13 vs 0/12 | -1.088 |
| live/maze | B | 16 | 16-0 | +6.25 | +9.26 | 3/16 vs 0/15 | +0.529 |
| live/portals | E | 16 | 11-5 | -6.25 | +31.21 | 0/16 vs 0/14 | -0.371 |
| live/queen_of_spades | A | 16 | 15-1 | -6.25 | -12.18 | 5/7 vs 0/3 | -1.206 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +5.12 | 15/15 vs 0/16 | +0.282 |
| live/slithery_fight | D | 16 | 16-0 | +37.50 | -9.51 | 5/16 vs 0/16 | -0.652 |
| live/stripes | A | 16 | 5-11 | +0.00 | -42.88 | 1/2 vs 0/2 | +0.737 |
| live/tower_defense | A | 16 | 13-3 | -12.50 | -12.79 | 2/7 vs 0/3 | -0.094 |
| live/trauma | C | 16 | 16-0 | +18.75 | +27.45 | 14/14 vs 0/16 | +1.349 |
| live/trophy | A | 16 | 16-0 | +6.25 | +4.17 | 0/0 vs 0/0 | +0.166 |
| live/unsw | B | 16 | 16-0 | +12.50 | +13.95 | 3/16 vs 0/16 | +0.714 |
| live/weakhold | C | 16 | 16-0 | +50.00 | -56.52 | 3/11 vs 0/7 | -29.546 |

Runtime / fingerprint: cand `unswbc 1.2.3` `cf6433c16114` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

