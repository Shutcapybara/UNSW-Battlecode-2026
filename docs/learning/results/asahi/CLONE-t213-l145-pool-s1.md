# asahi-15-t213-l145 vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 191 | 226 |
| L | 80 | 46 |
| D | 1 | 0 |
| win | 0.7040 | 0.8309 |
| reached | 157 | 146 |
| q_cond | 0.0064 | 0.0000 |
| q_joint | 0.0037 | 0.0000 |
| q_dec_W | 1 | 0 |
| q_dec_L | 9 | 5 |
| conv | 0.7166 | 0.8082 |
| pearls@50 | 32.4706 | 42.3088 |
| pearls@100 | 101.4816 | 126.0441 |
| pearls@150 | 179.2794 | 215.8162 |
| pearls@250 | 347.0147 | 395.0735 |
| units@100 | 26.1618 | 28.4816 |
| total@100 | 64.3346 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -12.68 [-17.83, -7.54] |
| econ | -12.75 [-17.37, -8.40] |
| econ_med | -13.79 [-16.96, -10.59] |
| units@100 | -4.05 [-7.69, -1.56] |
| total@100 | -7.20 [-11.11, -2.40] |
| q_joint | +0.37 [+0.00, +1.10] |
| q_cond | +0.64 [+0.00, +1.94] |
| conv | -9.17 [-16.68, -0.81] |
| death_wall_per1k | -2.18 [-3.32, -1.17] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -12.68 [-17.65, -7.72], econ~ -13.79 [-16.92, -10.87], units@100 -4.05 [-7.69, -1.56], total@100 -7.20 [-11.11, -2.44].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.031 | -30.3% |  |
| death_self_per1k | 3.585 | 3.298 | -8.0% |  |
| death_ally_body_per1k | 1.563 | 1.451 | -7.2% |  |
| death_h2h_ally_per1k | 1.238 | 0.956 | -22.7% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -19.64 | -12.77 | +0.00 | +0.002 |
| B | 80 | -10.00 | -4.56 | +0.00 | -0.342 |
| C | 48 | -13.54 | -28.34 | +0.00 | -9.272 |
| D | 16 | +18.75 | -31.56 | +6.25 | -1.804 |
| E | 16 | -6.25 | +11.93 | +0.00 | -5.794 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 11-5 | -18.75 | +28.73 | 0/16 vs 0/16 | +0.026 |
| live/autarky | A | 16 | 14-2 | -12.50 | -11.64 | 0/5 vs 0/3 | +0.961 |
| live/default | A | 16 | 12-4 | -6.25 | -14.03 | 0/3 vs 0/5 | +0.356 |
| live/devil | A | 16 | 10-6 | -31.25 | -23.98 | 0/0 vs 0/0 | -2.134 |
| live/dilemma | C | 16 | 14-2 | -6.25 | -6.30 | 0/6 vs 0/2 | -0.481 |
| live/islands | B | 16 | 16-0 | +0.00 | -7.48 | 0/14 vs 0/12 | -0.044 |
| live/maze | B | 16 | 11-5 | -25.00 | -20.41 | 0/16 vs 0/15 | -1.287 |
| live/portals | E | 16 | 11-5 | -6.25 | +11.93 | 0/15 vs 0/14 | -5.794 |
| live/queen_of_spades | A | 16 | 13-3 | -18.75 | -9.66 | 0/3 vs 0/3 | +0.384 |
| live/schooltime | B | 16 | 13-3 | -6.25 | -9.57 | 0/14 vs 0/16 | -0.039 |
| live/slithery_fight | D | 16 | 13-3 | +18.75 | -31.56 | 1/16 vs 0/16 | -1.804 |
| live/stripes | A | 16 | 6-10 | +6.25 | +34.06 | 0/1 vs 0/2 | +1.031 |
| live/tower_defense | A | 16 | 9-7 | -37.50 | -43.08 | 0/6 vs 0/3 | -0.562 |
| live/trauma | C | 16 | 10-6 | -18.75 | +0.56 | 0/16 vs 0/16 | -0.420 |
| live/trophy | A | 16 | 9-7 | -37.50 | -21.06 | 0/0 vs 0/0 | -0.021 |
| live/unsw | B | 16 | 14-2 | +0.00 | -14.07 | 0/16 vs 0/16 | -0.364 |
| live/weakhold | C | 16 | 5-10 | -15.62 | -79.30 | 0/10 vs 0/7 | -26.915 |

Runtime / fingerprint: cand `unswbc 1.2.3` `8c4ec413e575` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

