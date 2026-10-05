# asahi-27-b13-reserve vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 237 | 226 |
| L | 35 | 46 |
| D | 0 | 0 |
| win | 0.8713 | 0.8309 |
| reached | 162 | 146 |
| q_cond | 0.5926 | 0.0000 |
| q_joint | 0.3529 | 0.0000 |
| q_dec_W | 94 | 0 |
| q_dec_L | 2 | 5 |
| conv | 0.9074 | 0.8082 |
| pearls@50 | 42.0809 | 42.3088 |
| pearls@100 | 121.5184 | 126.0441 |
| pearls@150 | 211.8493 | 215.8162 |
| pearls@250 | 401.2279 | 395.0735 |
| units@100 | 28.7132 | 28.4816 |
| total@100 | 72.8897 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +4.04 [+0.37, +8.09] |
| econ | +1.33 [-3.05, +6.14] |
| econ_med | -1.73 [-4.53, +0.79] |
| units@100 | -1.56 [-2.22, +0.00] |
| total@100 | +0.00 [+0.00, +1.50] |
| q_joint | +35.29 [+29.41, +41.18] |
| q_cond | +59.26 [+51.20, +67.03] |
| conv | +9.92 [+3.73, +16.62] |
| death_wall_per1k | -1.39 [-2.49, -0.44] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +4.04 [+0.37, +7.72], econ~ -1.73 [-4.05, +0.52], units@100 -1.56 [-1.85, +0.00], total@100 +0.00 [+0.00, +1.41].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.828 | -19.2% |  |
| death_self_per1k | 3.585 | 3.936 | +9.8% |  |
| death_ally_body_per1k | 1.563 | 1.534 | -1.9% |  |
| death_h2h_ally_per1k | 1.238 | 1.304 | +5.3% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -1.79 | -3.05 | +16.07 | +0.145 |
| B | 80 | +3.75 | +7.29 | +58.75 | +0.081 |
| C | 48 | +16.67 | +5.87 | +45.83 | -7.855 |
| D | 16 | +25.00 | -7.96 | +56.25 | -1.723 |
| E | 16 | -12.50 | -2.11 | +0.00 | +0.317 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 14-2 | +0.00 | -1.89 | 13/16 vs 0/16 | +0.094 |
| live/autarky | A | 16 | 14-2 | -12.50 | -13.40 | 3/6 vs 0/3 | -0.872 |
| live/default | A | 16 | 14-2 | +6.25 | -14.00 | 9/11 vs 0/5 | -0.079 |
| live/devil | A | 16 | 16-0 | +6.25 | +0.47 | 1/1 vs 0/0 | -0.206 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +1.33 | 4/4 vs 0/2 | +0.487 |
| live/islands | B | 16 | 16-0 | +0.00 | +5.21 | 5/14 vs 0/12 | -0.576 |
| live/maze | B | 16 | 15-1 | +0.00 | +8.38 | 3/14 vs 0/15 | +0.421 |
| live/portals | E | 16 | 10-6 | -12.50 | -2.11 | 0/15 vs 0/14 | +0.317 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | -2.44 | 5/5 vs 0/3 | -0.383 |
| live/schooltime | B | 16 | 15-1 | +6.25 | +8.06 | 15/15 vs 0/16 | -0.247 |
| live/slithery_fight | D | 16 | 14-2 | +25.00 | -7.96 | 9/16 vs 0/16 | -1.723 |
| live/stripes | A | 16 | 4-12 | -6.25 | +15.50 | 0/0 vs 0/2 | +1.227 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | -2.93 | 0/3 vs 0/3 | +1.131 |
| live/trauma | C | 16 | 16-0 | +18.75 | +73.37 | 16/16 vs 0/16 | +1.485 |
| live/trophy | A | 16 | 14-2 | -6.25 | -4.53 | 0/0 vs 0/0 | +0.199 |
| live/unsw | B | 16 | 16-0 | +12.50 | +16.68 | 11/16 vs 0/16 | +0.714 |
| live/weakhold | C | 16 | 13-3 | +31.25 | -57.09 | 2/10 vs 0/7 | -25.538 |

Runtime / fingerprint: cand `unswbc 1.2.3` `16ceecff52c5` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

