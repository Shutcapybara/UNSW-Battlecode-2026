# bokuto-47-precious vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 36 | 30 |
| L | 32 | 38 |
| D | 0 | 0 |
| win | 0.5294 | 0.4412 |
| reached | 52 | 48 |
| q_cond | 0.4423 | 0.3542 |
| q_joint | 0.3382 | 0.2500 |
| q_dec_W | 14 | 9 |
| q_dec_L | 16 | 14 |
| conv | 0.4615 | 0.4583 |
| pearls@50 | 37.7647 | 38.9412 |
| pearls@100 | 105.7647 | 106.6324 |
| pearls@150 | 199.7206 | 186.1765 |
| pearls@250 | 405.5147 | 370.7941 |
| units@100 | 25.2353 | 24.3235 |
| total@100 | 62.6324 | 59.1765 |

| Δ | point [90 %] |
|---|---|
| win | +8.82 [-7.35, +25.00] |
| econ | +22.34 [+2.73, +45.53] |
| econ_med | +4.73 [-3.44, +12.68] |
| units@100 | -1.59 [-5.40, +10.71] |
| total@100 | +7.64 [+1.12, +13.70] |
| q_joint | +8.82 [-2.94, +20.59] |
| q_cond | +8.81 [-5.06, +22.01] |
| conv | +0.32 [-17.03, +19.06] |
| death_wall_per1k | +0.74 [-0.07, +1.58] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win +8.82 [-5.88, +23.53], econ~ +4.73 [-2.01, +11.55], units@100 -1.59 [-5.71, +7.70], total@100 +7.64 [+2.38, +11.51].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.361 | 6.102 | +13.8% | **yes** |
| death_self_per1k | 3.676 | 5.990 | +62.9% | **yes** |
| death_ally_body_per1k | 1.225 | 1.993 | +62.7% | **yes** |
| death_h2h_ally_per1k | 1.243 | 1.271 | +2.2% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | +42.86 | +72.98 | +14.29 | +1.712 |
| B | 20 | -10.00 | -13.16 | +25.00 | +0.684 |
| C | 12 | +0.00 | -15.07 | -33.33 | -0.215 |
| D | 4 | -50.00 | +13.54 | +25.00 | +4.212 |
| E | 4 | -50.00 | -33.52 | +0.00 | -6.373 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 1-3 | +0.00 | +5.72 | 3/4 vs 0/4 | +1.305 |
| live/autarky | A | 4 | 2-2 | +0.00 | +30.36 | 0/4 vs 0/4 | -1.682 |
| live/default | A | 4 | 2-2 | +50.00 | +8.59 | 0/0 vs 2/4 | +0.128 |
| live/devil | A | 4 | 4-0 | +100.00 | +284.97 | 0/0 vs 0/0 | +6.223 |
| live/dilemma | C | 4 | 4-0 | +50.00 | -23.02 | 0/0 vs 2/4 | -2.869 |
| live/islands | B | 4 | 1-3 | -25.00 | -2.30 | 1/4 vs 1/4 | +3.259 |
| live/maze | B | 4 | 4-0 | +75.00 | +18.43 | 2/4 vs 0/4 | +2.036 |
| live/portals | E | 4 | 2-2 | -50.00 | -33.52 | 2/4 vs 2/4 | -6.373 |
| live/queen_of_spades | A | 4 | 2-2 | +50.00 | +103.53 | 2/4 vs 0/2 | +2.962 |
| live/schooltime | B | 4 | 0-4 | -50.00 | -83.12 | 4/4 vs 4/4 | -3.445 |
| live/slithery_fight | D | 4 | 1-3 | -50.00 | +13.54 | 2/4 vs 1/4 | +4.212 |
| live/stripes | A | 4 | 0-4 | -50.00 | -10.63 | 0/2 vs 0/0 | +1.020 |
| live/tower_defense | A | 4 | 4-0 | +100.00 | +88.67 | 2/4 vs 0/2 | +2.490 |
| live/trauma | C | 4 | 0-4 | -50.00 | -27.29 | 2/4 vs 4/4 | -1.952 |
| live/trophy | A | 4 | 4-0 | +50.00 | +5.35 | 2/4 vs 0/0 | +0.841 |
| live/unsw | B | 4 | 1-3 | -50.00 | -4.55 | 1/4 vs 1/4 | +0.265 |
| live/weakhold | C | 4 | 4-0 | +0.00 | +5.09 | 0/2 vs 0/0 | +4.175 |

Runtime / fingerprint: cand `unswbc 1.2.3` `7322520f4e61` panel `28a92b488185`; parent `unswbc 1.2.3` `fa93106401b1` panel `28a92b488185`.

