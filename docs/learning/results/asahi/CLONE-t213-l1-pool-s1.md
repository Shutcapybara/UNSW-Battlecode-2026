# kageyama-02-p1-hb1-t213 vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 192 | 226 |
| L | 80 | 46 |
| D | 0 | 0 |
| win | 0.7059 | 0.8309 |
| reached | 161 | 146 |
| q_cond | 0.0124 | 0.0000 |
| q_joint | 0.0074 | 0.0000 |
| q_dec_W | 2 | 0 |
| q_dec_L | 11 | 5 |
| conv | 0.6894 | 0.8082 |
| pearls@50 | 34.0368 | 42.3088 |
| pearls@100 | 104.7610 | 126.0441 |
| pearls@150 | 188.6838 | 215.8162 |
| pearls@250 | 368.6471 | 395.0735 |
| units@100 | 25.9743 | 28.4816 |
| total@100 | 64.9007 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -12.50 [-17.28, -7.35] |
| econ | +9.31 [-4.38, +24.85] |
| econ_med | -9.61 [-12.56, -6.54] |
| units@100 | -6.67 [-9.45, -2.17] |
| total@100 | -5.49 [-8.48, -1.52] |
| q_joint | +0.74 [+0.00, +1.84] |
| q_cond | +1.24 [+0.00, +2.92] |
| conv | -11.88 [-19.78, -3.72] |
| death_wall_per1k | -1.55 [-2.66, -0.60] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -12.50 [-17.65, -7.35], econ~ -9.61 [-12.28, -6.74], units@100 -6.67 [-9.38, -2.22], total@100 -5.49 [-8.36, -3.01].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.664 | -21.5% |  |
| death_self_per1k | 3.585 | 3.599 | +0.4% |  |
| death_ally_body_per1k | 1.563 | 1.624 | +3.9% |  |
| death_h2h_ally_per1k | 1.238 | 1.111 | -10.2% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -15.18 | -5.70 | +0.89 | +0.217 |
| B | 80 | -12.50 | -12.19 | +0.00 | -0.140 |
| C | 48 | -12.50 | +91.85 | +0.00 | -7.367 |
| D | 16 | +12.50 | -22.19 | +6.25 | -0.778 |
| E | 16 | -18.75 | +5.78 | +0.00 | -4.280 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -6.25 | -16.53 | 0/16 vs 0/16 | -0.064 |
| live/autarky | A | 16 | 14-2 | -12.50 | -12.41 | 0/6 vs 0/3 | +1.138 |
| live/default | A | 16 | 11-5 | -12.50 | -17.67 | 0/8 vs 0/5 | +0.170 |
| live/devil | A | 16 | 12-4 | -18.75 | -11.52 | 0/0 vs 0/0 | -0.256 |
| live/dilemma | C | 16 | 10-6 | -31.25 | -17.70 | 0/6 vs 0/2 | +0.909 |
| live/islands | B | 16 | 13-3 | -18.75 | -9.46 | 0/13 vs 0/12 | +0.302 |
| live/maze | B | 16 | 13-3 | -12.50 | -18.44 | 0/16 vs 0/15 | -0.740 |
| live/portals | E | 16 | 9-7 | -18.75 | +5.78 | 0/14 vs 0/14 | -4.280 |
| live/queen_of_spades | A | 16 | 11-5 | -31.25 | -8.31 | 0/5 vs 0/3 | +0.676 |
| live/schooltime | B | 16 | 13-3 | -6.25 | -17.43 | 0/15 vs 0/16 | -0.046 |
| live/slithery_fight | D | 16 | 12-4 | +12.50 | -22.19 | 1/15 vs 0/16 | -0.778 |
| live/stripes | A | 16 | 7-9 | +12.50 | +44.39 | 0/0 vs 0/2 | +0.243 |
| live/tower_defense | A | 16 | 12-4 | -18.75 | -17.04 | 1/5 vs 0/3 | -0.223 |
| live/trauma | C | 16 | 12-4 | -6.25 | +382.73 | 0/15 vs 0/16 | +1.904 |
| live/trophy | A | 16 | 11-5 | -25.00 | -17.37 | 0/0 vs 0/0 | -0.228 |
| live/unsw | B | 16 | 11-5 | -18.75 | +0.90 | 0/16 vs 0/16 | -0.150 |
| live/weakhold | C | 16 | 8-8 | +0.00 | -89.48 | 0/11 vs 0/7 | -24.913 |

Runtime / fingerprint: cand `unswbc 1.2.3` `db2531c5b17b` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

