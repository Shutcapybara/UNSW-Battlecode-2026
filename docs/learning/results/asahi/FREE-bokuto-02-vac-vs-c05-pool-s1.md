# bokuto-02-vac vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 195 | 226 |
| L | 77 | 46 |
| D | 0 | 0 |
| win | 0.7169 | 0.8309 |
| reached | 195 | 146 |
| q_cond | 0.1385 | 0.0000 |
| q_joint | 0.0993 | 0.0000 |
| q_dec_W | 25 | 0 |
| q_dec_L | 9 | 5 |
| conv | 0.7077 | 0.8082 |
| pearls@50 | 30.9963 | 42.3088 |
| pearls@100 | 97.0000 | 126.0441 |
| pearls@150 | 173.6544 | 215.8162 |
| pearls@250 | 350.4412 | 395.0735 |
| units@100 | 27.8971 | 28.4816 |
| total@100 | 68.6801 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -11.40 [-16.91, -5.51] |
| econ | -16.86 [-20.72, -13.34] |
| econ_med | -18.11 [-24.97, -12.87] |
| units@100 | -1.56 [-3.87, -1.56] |
| total@100 | -3.13 [-5.62, +0.00] |
| q_joint | +9.93 [+6.25, +13.60] |
| q_cond | +13.85 [+8.78, +19.10] |
| conv | -10.05 [-17.42, -2.21] |
| death_wall_per1k | -2.97 [-4.27, -1.79] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -11.40 [-16.54, -6.62], econ~ -18.11 [-23.58, -14.01], units@100 -1.56 [-3.51, -1.56], total@100 -3.13 [-5.22, -0.32].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 4.247 | -41.1% |  |
| death_self_per1k | 3.585 | 3.366 | -6.1% |  |
| death_ally_body_per1k | 1.563 | 1.401 | -10.4% |  |
| death_h2h_ally_per1k | 1.238 | 1.423 | +15.0% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -16.07 | -15.59 | +1.79 | -1.508 |
| B | 80 | -11.25 | -7.36 | +23.75 | -0.107 |
| C | 48 | -8.33 | -32.19 | +10.42 | -12.309 |
| D | 16 | +0.00 | -42.80 | +6.25 | -2.246 |
| E | 16 | +0.00 | -1.28 | +0.00 | -0.165 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 12-4 | -12.50 | -7.74 | 0/16 vs 0/16 | +0.360 |
| live/autarky | A | 16 | 9-7 | -43.75 | -69.66 | 1/11 vs 0/3 | -8.616 |
| live/default | A | 16 | 11-5 | -12.50 | -23.28 | 0/14 vs 0/5 | -0.042 |
| live/devil | A | 16 | 16-0 | +6.25 | +18.98 | 0/0 vs 0/0 | -0.428 |
| live/dilemma | C | 16 | 10-6 | -31.25 | -15.88 | 0/9 vs 0/2 | -1.415 |
| live/islands | B | 16 | 11-5 | -31.25 | -21.01 | 1/16 vs 0/12 | -0.944 |
| live/maze | B | 16 | 16-0 | +6.25 | -1.96 | 0/16 vs 0/15 | -0.862 |
| live/portals | E | 16 | 12-4 | +0.00 | -1.28 | 0/16 vs 0/14 | -0.165 |
| live/queen_of_spades | A | 16 | 13-3 | -18.75 | -1.04 | 0/5 vs 0/3 | -1.097 |
| live/schooltime | B | 16 | 16-0 | +12.50 | -0.13 | 16/16 vs 0/16 | +0.122 |
| live/slithery_fight | D | 16 | 10-6 | +0.00 | -42.80 | 1/16 vs 0/16 | -2.246 |
| live/stripes | A | 16 | 5-11 | +0.00 | -2.90 | 0/3 vs 0/2 | +0.196 |
| live/tower_defense | A | 16 | 11-5 | -25.00 | -41.91 | 1/10 vs 0/3 | -1.425 |
| live/trauma | C | 16 | 6-10 | -43.75 | -21.21 | 1/16 vs 0/16 | -2.541 |
| live/trophy | A | 16 | 12-4 | -18.75 | +10.71 | 0/2 vs 0/0 | +0.859 |
| live/unsw | B | 16 | 9-7 | -31.25 | -5.99 | 2/16 vs 0/16 | +0.788 |
| live/weakhold | C | 16 | 16-0 | +50.00 | -59.48 | 4/13 vs 0/7 | -32.972 |

Runtime / fingerprint: cand `unswbc 1.2.3` `4d0f4b80cd7b` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

