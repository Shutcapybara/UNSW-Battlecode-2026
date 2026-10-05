# kenma-28-harvest-reserve vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 241 | 226 |
| L | 31 | 46 |
| D | 0 | 0 |
| win | 0.8860 | 0.8309 |
| reached | 166 | 146 |
| q_cond | 0.5723 | 0.0000 |
| q_joint | 0.3493 | 0.0000 |
| q_dec_W | 93 | 0 |
| q_dec_L | 2 | 5 |
| conv | 0.9337 | 0.8082 |
| pearls@50 | 42.0846 | 42.3088 |
| pearls@100 | 121.9559 | 126.0441 |
| pearls@150 | 213.4485 | 215.8162 |
| pearls@250 | 401.6875 | 395.0735 |
| units@100 | 28.8676 | 28.4816 |
| total@100 | 73.0441 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +5.51 [+1.82, +9.56] |
| econ | +1.34 [-3.05, +6.12] |
| econ_med | -2.20 [-4.59, +0.24] |
| units@100 | +0.00 [-1.56, +0.00] |
| total@100 | +0.00 [+0.00, +2.58] |
| q_joint | +34.93 [+28.68, +40.81] |
| q_cond | +57.23 [+48.78, +64.85] |
| conv | +12.55 [+6.58, +19.37] |
| death_wall_per1k | -1.33 [-2.44, -0.41] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +5.51 [+1.84, +9.56], econ~ -2.20 [-4.18, +0.19], units@100 +0.00 [-1.56, +0.00], total@100 +0.00 [+0.00, +1.99].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.883 | -18.4% |  |
| death_self_per1k | 3.585 | 3.915 | +9.2% |  |
| death_ally_body_per1k | 1.563 | 1.539 | -1.5% |  |
| death_h2h_ally_per1k | 1.238 | 1.337 | +8.0% |  |
| death_invalid_per1k | 0.000 | 0.005 | — | **yes** |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -1.79 | -3.33 | +16.07 | +0.145 |
| B | 80 | +7.50 | +7.38 | +56.25 | +0.262 |
| C | 48 | +16.67 | +5.86 | +45.83 | -7.841 |
| D | 16 | +31.25 | -6.26 | +62.50 | -1.746 |
| E | 16 | -12.50 | -2.11 | +0.00 | +0.317 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 16-0 | +12.50 | -2.39 | 12/16 vs 0/16 | -0.022 |
| live/autarky | A | 16 | 14-2 | -12.50 | -13.40 | 3/6 vs 0/3 | -0.872 |
| live/default | A | 16 | 14-2 | +6.25 | -14.00 | 9/11 vs 0/5 | -0.095 |
| live/devil | A | 16 | 16-0 | +6.25 | -0.97 | 1/1 vs 0/0 | -0.123 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +1.33 | 4/4 vs 0/2 | +0.487 |
| live/islands | B | 16 | 16-0 | +0.00 | +5.24 | 4/15 vs 0/12 | -0.705 |
| live/maze | B | 16 | 16-0 | +6.25 | +8.12 | 5/16 vs 0/15 | +0.529 |
| live/portals | E | 16 | 10-6 | -12.50 | -2.11 | 0/15 vs 0/14 | +0.317 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | -2.44 | 5/5 vs 0/3 | -0.383 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +8.96 | 16/16 vs 0/16 | +0.809 |
| live/slithery_fight | D | 16 | 15-1 | +31.25 | -6.26 | 10/16 vs 0/16 | -1.746 |
| live/stripes | A | 16 | 4-12 | -6.25 | +15.50 | 0/0 vs 0/2 | +1.227 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | -2.93 | 0/3 vs 0/3 | +1.131 |
| live/trauma | C | 16 | 16-0 | +18.75 | +73.36 | 16/16 vs 0/16 | +1.529 |
| live/trophy | A | 16 | 14-2 | -6.25 | -5.08 | 0/0 vs 0/0 | +0.133 |
| live/unsw | B | 16 | 15-1 | +6.25 | +16.97 | 8/16 vs 0/16 | +0.701 |
| live/weakhold | C | 16 | 13-3 | +31.25 | -57.09 | 2/10 vs 0/7 | -25.538 |

Runtime / fingerprint: cand `unswbc 1.2.3
installed the replay viewer into /usr/local/bin/code` `73f60fe2664c` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

