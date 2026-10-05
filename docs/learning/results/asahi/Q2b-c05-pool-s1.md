# asahi-25-q2bcrown-c05 vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 219 | 226 |
| L | 52 | 46 |
| D | 1 | 0 |
| win | 0.8070 | 0.8309 |
| reached | 149 | 146 |
| q_cond | 0.1141 | 0.0000 |
| q_joint | 0.0625 | 0.0000 |
| q_dec_W | 16 | 0 |
| q_dec_L | 5 | 5 |
| conv | 0.7752 | 0.8082 |
| pearls@50 | 41.8419 | 42.3088 |
| pearls@100 | 122.4449 | 126.0441 |
| pearls@150 | 209.0919 | 215.8162 |
| pearls@250 | 387.9338 | 395.0735 |
| units@100 | 27.7279 | 28.4816 |
| total@100 | 70.0515 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -2.39 [-5.89, +0.92] |
| econ | -3.19 [-4.73, -1.65] |
| econ_med | -1.16 [-2.65, -0.45] |
| units@100 | -3.35 [-4.76, -0.42] |
| total@100 | +0.00 [-2.36, +0.00] |
| q_joint | +6.25 [+3.31, +9.93] |
| q_cond | +11.41 [+5.93, +17.88] |
| conv | -3.31 [-9.49, +2.60] |
| death_wall_per1k | +0.12 [-0.02, +0.27] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -2.39 [-6.07, +1.10], econ~ -1.16 [-2.53, -0.47], units@100 -3.35 [-4.76, -0.84], total@100 +0.00 [-2.35, +0.00].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 7.331 | +1.6% |  |
| death_self_per1k | 3.585 | 3.517 | -1.9% |  |
| death_ally_body_per1k | 1.563 | 1.509 | -3.4% |  |
| death_h2h_ally_per1k | 1.238 | 1.183 | -4.4% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -2.68 | -3.80 | +0.00 | +0.156 |
| B | 80 | -2.50 | -0.40 | +2.50 | -0.060 |
| C | 48 | +2.08 | -2.00 | +31.25 | +0.276 |
| D | 16 | +0.00 | -0.02 | +0.00 | -0.038 |
| E | 16 | -15.62 | -19.62 | +0.00 | +0.426 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 16-0 | +12.50 | -1.64 | 1/16 vs 0/16 | +0.123 |
| live/autarky | A | 16 | 15-1 | -6.25 | -2.74 | 0/1 vs 0/3 | -0.317 |
| live/default | A | 16 | 13-3 | +0.00 | -5.47 | 0/6 vs 0/5 | -0.029 |
| live/devil | A | 16 | 15-1 | +0.00 | -0.20 | 0/0 vs 0/0 | -0.411 |
| live/dilemma | C | 16 | 14-2 | -6.25 | -1.22 | 0/3 vs 0/2 | +0.316 |
| live/islands | B | 16 | 16-0 | +0.00 | +0.81 | 0/13 vs 0/12 | -0.298 |
| live/maze | B | 16 | 9-7 | -37.50 | -0.20 | 0/16 vs 0/15 | -0.312 |
| live/portals | E | 16 | 9-6 | -15.62 | -19.62 | 0/16 vs 0/14 | +0.426 |
| live/queen_of_spades | A | 16 | 15-1 | -6.25 | -5.98 | 0/4 vs 0/3 | +0.135 |
| live/schooltime | B | 16 | 14-2 | +0.00 | +0.00 | 0/16 vs 0/16 | +0.000 |
| live/slithery_fight | D | 16 | 10-6 | +0.00 | -0.02 | 0/16 vs 0/16 | -0.038 |
| live/stripes | A | 16 | 5-11 | +0.00 | -1.94 | 0/1 vs 0/2 | +1.238 |
| live/tower_defense | A | 16 | 14-2 | -6.25 | -0.94 | 0/2 vs 0/3 | +0.490 |
| live/trauma | C | 16 | 15-1 | +12.50 | -4.78 | 15/16 vs 0/16 | +0.512 |
| live/trophy | A | 16 | 15-1 | +0.00 | -9.31 | 0/0 vs 0/0 | -0.017 |
| live/unsw | B | 16 | 16-0 | +12.50 | -0.95 | 1/16 vs 0/16 | +0.188 |
| live/weakhold | C | 16 | 8-8 | +0.00 | +0.00 | 0/7 vs 0/7 | +0.000 |

Runtime / fingerprint: cand `unswbc 1.2.3` `3959d1c5f000` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

