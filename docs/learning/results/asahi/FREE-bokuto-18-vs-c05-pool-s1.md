# bokuto-18-queenfeed vs carthage-05-free-sprint — seeds 1

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
| reached | 171 | 146 |
| q_cond | 0.4854 | 0.0000 |
| q_joint | 0.3051 | 0.0000 |
| q_dec_W | 80 | 0 |
| q_dec_L | 2 | 5 |
| conv | 0.8713 | 0.8082 |
| pearls@50 | 42.4485 | 42.3088 |
| pearls@100 | 123.4228 | 126.0441 |
| pearls@150 | 214.8824 | 215.8162 |
| pearls@250 | 406.7574 | 395.0735 |
| units@100 | 28.6324 | 28.4816 |
| total@100 | 72.7647 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +4.04 [-0.74, +8.82] |
| econ | -2.86 [-7.06, +0.89] |
| econ_med | -0.94 [-4.56, +1.19] |
| units@100 | -1.56 [-1.56, +0.00] |
| total@100 | -0.82 [-3.03, +0.61] |
| q_joint | +30.51 [+25.37, +36.40] |
| q_cond | +48.54 [+41.56, +55.83] |
| conv | +6.31 [-0.42, +13.44] |
| death_wall_per1k | -1.63 [-2.92, -0.55] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +4.04 [-0.37, +8.82], econ~ -0.94 [-3.85, +0.80], units@100 -1.56 [-1.56, +0.00], total@100 -0.82 [-2.58, +0.00].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.579 | -22.7% |  |
| death_self_per1k | 3.585 | 4.816 | +34.4% | **yes** |
| death_ally_body_per1k | 1.563 | 1.663 | +6.4% |  |
| death_h2h_ally_per1k | 1.238 | 1.146 | -7.4% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -3.57 | -11.54 | +16.96 | +0.096 |
| B | 80 | +0.00 | +7.12 | +37.50 | +0.110 |
| C | 48 | +22.92 | -9.20 | +52.08 | -9.331 |
| D | 16 | +31.25 | -6.98 | +56.25 | -0.635 |
| E | 16 | -6.25 | +31.21 | +0.00 | -0.371 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -6.25 | -1.85 | 5/16 vs 0/16 | +0.242 |
| live/autarky | A | 16 | 15-1 | -6.25 | -12.17 | 5/6 vs 0/3 | -0.113 |
| live/default | A | 16 | 11-5 | -12.50 | -14.21 | 6/11 vs 0/5 | -0.026 |
| live/devil | A | 16 | 16-0 | +6.25 | +9.65 | 0/0 vs 0/0 | +1.167 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +1.46 | 7/8 vs 0/2 | +0.258 |
| live/islands | B | 16 | 16-0 | +0.00 | +5.04 | 3/10 vs 0/12 | -0.929 |
| live/maze | B | 16 | 15-1 | +0.00 | +9.88 | 1/16 vs 0/15 | +0.808 |
| live/portals | E | 16 | 11-5 | -6.25 | +31.21 | 0/16 vs 0/14 | -0.371 |
| live/queen_of_spades | A | 16 | 15-1 | -6.25 | -12.18 | 5/7 vs 0/3 | -1.206 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +6.69 | 14/14 vs 0/16 | -0.241 |
| live/slithery_fight | D | 16 | 15-1 | +31.25 | -6.98 | 9/16 vs 0/16 | -0.635 |
| live/stripes | A | 16 | 5-11 | +0.00 | -42.88 | 1/2 vs 0/2 | +0.737 |
| live/tower_defense | A | 16 | 13-3 | -12.50 | -12.79 | 2/7 vs 0/3 | -0.094 |
| live/trauma | C | 16 | 16-0 | +18.75 | +27.45 | 15/15 vs 0/16 | +1.294 |
| live/trophy | A | 16 | 16-0 | +6.25 | +3.83 | 0/0 vs 0/0 | +0.208 |
| live/unsw | B | 16 | 13-3 | -6.25 | +15.84 | 7/16 vs 0/16 | +0.667 |
| live/weakhold | C | 16 | 16-0 | +50.00 | -56.52 | 3/11 vs 0/7 | -29.546 |

Runtime / fingerprint: cand `unswbc 1.2.3` `fa93106401b1` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

