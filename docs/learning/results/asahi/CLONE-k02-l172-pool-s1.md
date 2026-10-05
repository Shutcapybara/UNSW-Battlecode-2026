# asahi-14-p1hb1-l172 vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 206 | 226 |
| L | 66 | 46 |
| D | 0 | 0 |
| win | 0.7574 | 0.8309 |
| reached | 161 | 146 |
| q_cond | 0.0062 | 0.0000 |
| q_joint | 0.0037 | 0.0000 |
| q_dec_W | 1 | 0 |
| q_dec_L | 7 | 5 |
| conv | 0.7453 | 0.8082 |
| pearls@50 | 37.9265 | 42.3088 |
| pearls@100 | 111.7279 | 126.0441 |
| pearls@150 | 196.0993 | 215.8162 |
| pearls@250 | 379.2610 | 395.0735 |
| units@100 | 26.3897 | 28.4816 |
| total@100 | 64.4485 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -7.35 [-12.15, -2.21] |
| econ | +0.61 [-6.26, +8.14] |
| econ_med | -5.73 [-9.66, -2.62] |
| units@100 | -7.69 [-9.52, -4.72] |
| total@100 | -9.09 [-11.32, -5.81] |
| q_joint | +0.37 [+0.00, +1.10] |
| q_cond | +0.62 [+0.00, +1.88] |
| conv | -6.29 [-13.08, +0.76] |
| death_wall_per1k | -1.29 [-2.32, -0.37] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -7.35 [-12.13, -2.57], econ~ -5.73 [-8.96, -3.01], units@100 -7.69 [-9.45, -5.32], total@100 -9.09 [-11.32, -6.35].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.923 | -17.9% |  |
| death_self_per1k | 3.585 | 3.593 | +0.2% |  |
| death_ally_body_per1k | 1.563 | 1.559 | -0.2% |  |
| death_h2h_ally_per1k | 1.238 | 0.611 | -50.6% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -11.61 | -2.03 | +0.00 | +0.423 |
| B | 80 | -5.00 | -7.90 | +1.25 | +0.016 |
| C | 48 | -4.17 | +30.78 | +0.00 | -5.417 |
| D | 16 | +0.00 | -0.45 | +0.00 | +0.824 |
| E | 16 | -6.25 | -27.85 | +0.00 | -9.552 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 15-1 | +6.25 | -19.60 | 1/16 vs 0/16 | -0.066 |
| live/autarky | A | 16 | 16-0 | +0.00 | -2.51 | 0/4 vs 0/3 | +1.004 |
| live/default | A | 16 | 9-7 | -25.00 | -40.07 | 0/8 vs 0/5 | +0.102 |
| live/devil | A | 16 | 8-8 | -43.75 | -17.16 | 0/1 vs 0/0 | -1.173 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +4.64 | 0/6 vs 0/2 | +1.294 |
| live/islands | B | 16 | 15-1 | -6.25 | -1.08 | 0/16 vs 0/12 | +0.168 |
| live/maze | B | 16 | 13-3 | -12.50 | -17.49 | 0/16 vs 0/15 | -0.317 |
| live/portals | E | 16 | 11-5 | -6.25 | -27.85 | 0/16 vs 0/14 | -9.552 |
| live/queen_of_spades | A | 16 | 14-2 | -12.50 | -7.27 | 0/4 vs 0/3 | -0.535 |
| live/schooltime | B | 16 | 12-4 | -12.50 | +3.29 | 0/12 vs 0/16 | +0.071 |
| live/slithery_fight | D | 16 | 10-6 | +0.00 | -0.45 | 0/16 vs 0/16 | +0.824 |
| live/stripes | A | 16 | 9-7 | +25.00 | +72.30 | 0/1 vs 0/2 | +1.961 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | -4.06 | 0/3 vs 0/3 | +1.635 |
| live/trauma | C | 16 | 11-5 | -12.50 | +137.45 | 0/16 vs 0/16 | +0.849 |
| live/trophy | A | 16 | 11-5 | -25.00 | -15.45 | 0/0 vs 0/0 | -0.029 |
| live/unsw | B | 16 | 14-2 | +0.00 | -4.62 | 0/16 vs 0/16 | +0.226 |
| live/weakhold | C | 16 | 8-8 | +0.00 | -49.75 | 0/10 vs 0/7 | -18.395 |

Runtime / fingerprint: cand `unswbc 1.2.3` `0b0b837f7121` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

