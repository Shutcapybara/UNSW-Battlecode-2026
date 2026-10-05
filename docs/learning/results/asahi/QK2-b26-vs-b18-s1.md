# bokuto-26-hunt vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 27 | 30 |
| L | 41 | 38 |
| D | 0 | 0 |
| win | 0.3971 | 0.4412 |
| reached | 48 | 48 |
| q_cond | 0.2917 | 0.3542 |
| q_joint | 0.2059 | 0.2500 |
| q_dec_W | 7 | 9 |
| q_dec_L | 9 | 14 |
| conv | 0.4375 | 0.4583 |
| pearls@50 | 39.1471 | 38.9412 |
| pearls@100 | 105.1029 | 106.6324 |
| pearls@150 | 184.1176 | 186.1765 |
| pearls@250 | 370.1471 | 370.7941 |
| units@100 | 24.3529 | 24.3235 |
| total@100 | 58.6176 | 59.1765 |

| Δ | point [90 %] |
|---|---|
| win | -4.41 [-14.71, +5.88] |
| econ | -1.38 [-3.40, +0.48] |
| econ_med | -0.45 [-2.38, +1.86] |
| units@100 | -3.03 [-4.48, +0.00] |
| total@100 | -5.21 [-9.44, -1.97] |
| q_joint | -4.41 [-11.76, +2.94] |
| q_cond | -6.25 [-17.18, +3.44] |
| conv | -2.08 [-17.45, +13.54] |
| death_wall_per1k | -0.24 [-0.41, -0.07] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win -4.41 [-14.71, +5.96], econ~ -0.45 [-2.27, +1.78], units@100 -3.03 [-5.56, +0.00], total@100 -5.21 [-9.44, -1.88].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.361 | 5.125 | -4.4% |  |
| death_self_per1k | 3.676 | 3.785 | +3.0% |  |
| death_ally_body_per1k | 1.225 | 1.261 | +2.9% |  |
| death_h2h_ally_per1k | 1.243 | 1.157 | -6.9% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | +0.00 | -0.59 | -7.14 | -0.020 |
| B | 20 | +5.00 | +1.23 | +0.00 | -0.484 |
| C | 12 | +0.00 | -7.28 | +0.00 | -0.658 |
| D | 4 | -50.00 | -0.82 | +25.00 | +1.076 |
| E | 4 | -50.00 | -2.89 | -50.00 | -0.559 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 4-0 | +75.00 | -2.03 | 2/4 vs 0/4 | -0.240 |
| live/autarky | A | 4 | 0-4 | -50.00 | -3.09 | 0/4 vs 0/4 | +0.051 |
| live/default | A | 4 | 2-2 | +50.00 | +12.88 | 0/4 vs 2/4 | -0.003 |
| live/devil | A | 4 | 0-4 | +0.00 | +3.38 | 0/0 vs 0/0 | +0.460 |
| live/dilemma | C | 4 | 2-2 | +0.00 | -20.19 | 2/4 vs 2/4 | -0.813 |
| live/islands | B | 4 | 3-1 | +25.00 | +2.64 | 0/4 vs 1/4 | -0.488 |
| live/maze | B | 4 | 0-4 | -25.00 | +0.36 | 0/4 vs 0/4 | -1.386 |
| live/portals | E | 4 | 2-2 | -50.00 | -2.89 | 0/4 vs 2/4 | -0.559 |
| live/queen_of_spades | A | 4 | 0-4 | +0.00 | +1.24 | 0/2 vs 0/2 | -0.247 |
| live/schooltime | B | 4 | 2-2 | +0.00 | +5.59 | 4/4 vs 4/4 | -0.201 |
| live/slithery_fight | D | 4 | 1-3 | -50.00 | -0.82 | 2/4 vs 1/4 | +1.076 |
| live/stripes | A | 4 | 2-2 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/tower_defense | A | 4 | 0-4 | +0.00 | -10.90 | 0/0 vs 0/2 | -0.518 |
| live/trauma | C | 4 | 2-2 | +0.00 | -0.23 | 4/4 vs 4/4 | -0.105 |
| live/trophy | A | 4 | 2-2 | +0.00 | -7.61 | 0/0 vs 0/0 | +0.114 |
| live/unsw | B | 4 | 1-3 | -50.00 | -0.42 | 0/4 vs 1/4 | -0.104 |
| live/weakhold | C | 4 | 4-0 | +0.00 | -1.43 | 0/2 vs 0/0 | -1.057 |

Runtime / fingerprint: cand `unswbc 1.2.3` `c4bbe1c87566` panel `28a92b488185`; parent `unswbc 1.2.3` `fa93106401b1` panel `28a92b488185`.

