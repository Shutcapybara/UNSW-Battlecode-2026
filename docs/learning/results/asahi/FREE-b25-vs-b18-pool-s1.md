# bokuto-25-reserve4 vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 242 | 237 |
| L | 30 | 35 |
| D | 0 | 0 |
| win | 0.8897 | 0.8713 |
| reached | 175 | 171 |
| q_cond | 0.4571 | 0.4854 |
| q_joint | 0.2941 | 0.3051 |
| q_dec_W | 77 | 80 |
| q_dec_L | 1 | 2 |
| conv | 0.9029 | 0.8713 |
| pearls@50 | 42.5110 | 42.4485 |
| pearls@100 | 121.8824 | 123.4228 |
| pearls@150 | 212.1949 | 214.8824 |
| pearls@250 | 397.3824 | 406.7574 |
| units@100 | 28.2463 | 28.6324 |
| total@100 | 73.8015 | 72.7647 |

| Δ | point [90 %] |
|---|---|
| win | +1.84 [-0.37, +3.68] |
| econ | -0.48 [-0.72, -0.26] |
| econ_med | -0.62 [-1.41, -0.21] |
| units@100 | +0.00 [-2.94, +0.00] |
| total@100 | +0.70 [+0.00, +1.88] |
| q_joint | -1.10 [-5.15, +2.94] |
| q_cond | -2.82 [-8.84, +3.21] |
| conv | +3.15 [-0.17, +6.19] |
| death_wall_per1k | +0.03 [-0.02, +0.08] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +1.84 [+0.00, +4.04], econ~ -0.62 [-1.32, -0.25], units@100 +0.00 [-1.90, +0.00], total@100 +0.70 [+0.00, +1.85].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.579 | 5.610 | +0.5% |  |
| death_self_per1k | 4.816 | 4.680 | -2.8% |  |
| death_ally_body_per1k | 1.663 | 1.779 | +7.0% |  |
| death_h2h_ally_per1k | 1.146 | 1.142 | -0.3% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +0.00 | +0.09 | +0.89 | +0.024 |
| B | 80 | +5.00 | -1.23 | +1.25 | +0.061 |
| C | 48 | +0.00 | +0.00 | -2.08 | +0.018 |
| D | 16 | +6.25 | -2.72 | -25.00 | -0.017 |
| E | 16 | +0.00 | +0.00 | +0.00 | +0.000 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | +0.00 | +0.53 | 8/16 vs 5/16 | +0.176 |
| live/autarky | A | 16 | 15-1 | +0.00 | +0.00 | 5/6 vs 5/6 | -0.001 |
| live/default | A | 16 | 11-5 | +0.00 | +0.31 | 7/12 vs 6/11 | +0.017 |
| live/devil | A | 16 | 16-0 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.195 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +0.00 | 7/8 vs 7/8 | +0.000 |
| live/islands | B | 16 | 16-0 | +0.00 | -3.01 | 2/13 vs 3/10 | -0.159 |
| live/maze | B | 16 | 16-0 | +6.25 | -0.52 | 3/16 vs 1/16 | -0.279 |
| live/portals | E | 16 | 11-5 | +0.00 | +0.00 | 0/16 vs 0/16 | +0.000 |
| live/queen_of_spades | A | 16 | 15-1 | +0.00 | +0.00 | 5/7 vs 5/7 | +0.000 |
| live/schooltime | B | 16 | 16-0 | +0.00 | -1.41 | 15/15 vs 14/14 | +0.523 |
| live/slithery_fight | D | 16 | 16-0 | +6.25 | -2.72 | 5/16 vs 9/16 | -0.017 |
| live/stripes | A | 16 | 5-11 | +0.00 | +0.00 | 1/2 vs 1/2 | +0.000 |
| live/tower_defense | A | 16 | 13-3 | +0.00 | +0.00 | 2/7 vs 2/7 | +0.000 |
| live/trauma | C | 16 | 16-0 | +0.00 | +0.00 | 14/14 vs 15/15 | +0.055 |
| live/trophy | A | 16 | 16-0 | +0.00 | +0.33 | 0/0 vs 0/0 | -0.042 |
| live/unsw | B | 16 | 16-0 | +18.75 | -1.74 | 3/16 vs 7/16 | +0.047 |
| live/weakhold | C | 16 | 16-0 | +0.00 | +0.00 | 3/11 vs 3/11 | +0.000 |

Runtime / fingerprint: cand `unswbc 1.2.3` `cf6433c16114` panel `39961c55d0e6`; parent `unswbc 1.2.3` `fa93106401b1` panel `39961c55d0e6`.

