# bokuto-18-queenfeed vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 30 | 21 |
| L | 38 | 47 |
| D | 0 | 0 |
| win | 0.4412 | 0.3088 |
| reached | 48 | 50 |
| q_cond | 0.3542 | 0.0000 |
| q_joint | 0.2500 | 0.0000 |
| q_dec_W | 9 | 0 |
| q_dec_L | 14 | 27 |
| conv | 0.4583 | 0.3000 |
| pearls@50 | 38.9412 | 38.2353 |
| pearls@100 | 106.6324 | 109.0735 |
| pearls@150 | 186.1765 | 190.5588 |
| pearls@250 | 370.7941 | 371.1029 |
| units@100 | 24.3235 | 24.2206 |
| total@100 | 59.1765 | 59.0588 |

| Δ | point [90 %] |
|---|---|
| win | +13.24 [+0.00, +26.47] |
| econ | +3.12 [-5.54, +11.94] |
| econ_med | -4.42 [-9.65, +1.81] |
| units@100 | -0.39 [-4.50, +5.30] |
| total@100 | -4.22 [-11.60, +8.98] |
| q_joint | +25.00 [+16.18, +35.29] |
| q_cond | +35.42 [+23.40, +47.73] |
| conv | +15.83 [+1.28, +30.00] |
| death_wall_per1k | -2.73 [-6.26, +0.23] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win +13.24 [-1.54, +27.94], econ~ -4.42 [-8.42, +0.42], units@100 -0.39 [-4.50, +5.26], total@100 -4.22 [-11.60, +8.00].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 8.088 | 5.361 | -33.7% |  |
| death_self_per1k | 3.520 | 3.676 | +4.4% |  |
| death_ally_body_per1k | 1.257 | 1.225 | -2.6% |  |
| death_h2h_ally_per1k | 1.293 | 1.243 | -3.8% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | -14.29 | +1.43 | +7.14 | -0.359 |
| B | 20 | +15.00 | +5.41 | +30.00 | +0.489 |
| C | 12 | +50.00 | -4.39 | +50.00 | -14.798 |
| D | 4 | +50.00 | -0.03 | +25.00 | -1.965 |
| E | 4 | +50.00 | +29.27 | +50.00 | +0.081 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 1-3 | +0.00 | -12.44 | 0/4 vs 0/4 | -0.596 |
| live/autarky | A | 4 | 2-2 | +0.00 | -29.37 | 0/4 vs 0/2 | -2.307 |
| live/default | A | 4 | 0-4 | -50.00 | -21.89 | 2/4 vs 0/2 | -0.141 |
| live/devil | A | 4 | 0-4 | +0.00 | +43.15 | 0/0 vs 0/0 | +0.146 |
| live/dilemma | C | 4 | 2-2 | +0.00 | -10.13 | 2/4 vs 0/4 | +0.636 |
| live/islands | B | 4 | 2-2 | +0.00 | -6.86 | 1/4 vs 0/4 | -0.629 |
| live/maze | B | 4 | 1-3 | -25.00 | +25.77 | 0/4 vs 0/4 | +1.726 |
| live/portals | E | 4 | 4-0 | +50.00 | +29.27 | 2/4 vs 0/4 | +0.081 |
| live/queen_of_spades | A | 4 | 0-4 | -50.00 | -26.96 | 0/2 vs 0/4 | -1.195 |
| live/schooltime | B | 4 | 2-2 | +50.00 | +7.08 | 4/4 vs 0/4 | +1.115 |
| live/slithery_fight | D | 4 | 3-1 | +50.00 | -0.03 | 1/4 vs 0/4 | -1.965 |
| live/stripes | A | 4 | 2-2 | +50.00 | +63.48 | 0/0 vs 0/0 | +2.184 |
| live/tower_defense | A | 4 | 0-4 | -50.00 | -29.54 | 0/2 vs 0/2 | -0.930 |
| live/trauma | C | 4 | 2-2 | +50.00 | +50.00 | 4/4 vs 0/4 | +3.938 |
| live/trophy | A | 4 | 2-2 | +0.00 | +11.12 | 0/0 vs 0/0 | -0.271 |
| live/unsw | B | 4 | 3-1 | +50.00 | +13.52 | 1/4 vs 0/4 | +0.830 |
| live/weakhold | C | 4 | 4-0 | +100.00 | -53.04 | 0/0 vs 0/4 | -48.968 |

Runtime / fingerprint: cand `unswbc 1.2.3` `fa93106401b1` panel `28a92b488185`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `28a92b488185`.

