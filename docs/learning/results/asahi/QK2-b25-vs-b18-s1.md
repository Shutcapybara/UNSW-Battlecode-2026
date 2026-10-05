# bokuto-25-reserve4 vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 33 | 30 |
| L | 35 | 38 |
| D | 0 | 0 |
| win | 0.4853 | 0.4412 |
| reached | 50 | 48 |
| q_cond | 0.4400 | 0.3542 |
| q_joint | 0.3235 | 0.2500 |
| q_dec_W | 14 | 9 |
| q_dec_L | 16 | 14 |
| conv | 0.5400 | 0.4583 |
| pearls@50 | 38.9412 | 38.9412 |
| pearls@100 | 107.3676 | 106.6324 |
| pearls@150 | 185.7500 | 186.1765 |
| pearls@250 | 364.5882 | 370.7941 |
| units@100 | 24.1471 | 24.3235 |
| total@100 | 59.5147 | 59.1765 |

| Δ | point [90 %] |
|---|---|
| win | +4.41 [-2.94, +10.37] |
| econ | -0.22 [-0.44, +0.00] |
| econ_med | -0.82 [-1.69, -0.08] |
| units@100 | -0.79 [-2.41, +0.00] |
| total@100 | +0.00 [-0.64, +3.64] |
| q_joint | +7.35 [+1.47, +14.71] |
| q_cond | +8.58 [+0.28, +18.13] |
| conv | +8.17 [-2.13, +17.32] |
| death_wall_per1k | +0.04 [-0.02, +0.09] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win +4.41 [-2.94, +13.24], econ~ -0.82 [-1.64, +0.05], units@100 -0.79 [-2.46, +0.00], total@100 +0.00 [-1.25, +2.81].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.361 | 5.399 | +0.7% |  |
| death_self_per1k | 3.676 | 3.945 | +7.3% |  |
| death_ally_body_per1k | 1.225 | 1.369 | +11.8% | **yes** |
| death_h2h_ally_per1k | 1.243 | 1.264 | +1.6% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | +0.00 | +0.01 | +7.14 | +0.012 |
| B | 20 | +10.00 | -0.78 | +10.00 | +0.023 |
| C | 12 | +0.00 | +0.00 | +0.00 | +0.000 |
| D | 4 | +25.00 | +0.10 | +25.00 | +0.434 |
| E | 4 | +0.00 | +0.00 | +0.00 | +0.000 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 2-2 | +25.00 | -0.90 | 2/4 vs 0/4 | -0.121 |
| live/autarky | A | 4 | 2-2 | +0.00 | +0.00 | 0/4 vs 0/4 | +0.000 |
| live/default | A | 4 | 0-4 | +0.00 | +0.00 | 2/4 vs 2/4 | +0.000 |
| live/devil | A | 4 | 0-4 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/dilemma | C | 4 | 2-2 | +0.00 | +0.00 | 2/4 vs 2/4 | +0.000 |
| live/islands | B | 4 | 4-0 | +50.00 | -0.97 | 1/4 vs 1/4 | +0.458 |
| live/maze | B | 4 | 1-3 | +0.00 | -0.53 | 0/4 vs 0/4 | -0.258 |
| live/portals | E | 4 | 4-0 | +0.00 | +0.00 | 2/4 vs 2/4 | +0.000 |
| live/queen_of_spades | A | 4 | 0-4 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |
| live/schooltime | B | 4 | 2-2 | +0.00 | +0.59 | 4/4 vs 4/4 | -0.022 |
| live/slithery_fight | D | 4 | 4-0 | +25.00 | +0.10 | 2/4 vs 1/4 | +0.434 |
| live/stripes | A | 4 | 2-2 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/tower_defense | A | 4 | 0-4 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |
| live/trauma | C | 4 | 2-2 | +0.00 | +0.00 | 4/4 vs 4/4 | +0.000 |
| live/trophy | A | 4 | 2-2 | +0.00 | +0.08 | 2/2 vs 0/0 | +0.087 |
| live/unsw | B | 4 | 2-2 | -25.00 | -2.08 | 1/4 vs 1/4 | +0.057 |
| live/weakhold | C | 4 | 4-0 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |

Runtime / fingerprint: cand `unswbc 1.2.3` `cf6433c16114` panel `28a92b488185`; parent `unswbc 1.2.3` `fa93106401b1` panel `28a92b488185`.

