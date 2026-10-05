# bokuto-46-regions vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 38 | 30 |
| L | 30 | 38 |
| D | 0 | 0 |
| win | 0.5588 | 0.4412 |
| reached | 50 | 48 |
| q_cond | 0.3800 | 0.3542 |
| q_joint | 0.2794 | 0.2500 |
| q_dec_W | 12 | 9 |
| q_dec_L | 17 | 14 |
| conv | 0.4800 | 0.4583 |
| pearls@50 | 37.7647 | 38.9412 |
| pearls@100 | 105.7647 | 106.6324 |
| pearls@150 | 199.7206 | 186.1765 |
| pearls@250 | 405.5441 | 370.7941 |
| units@100 | 25.2353 | 24.3235 |
| total@100 | 62.6324 | 59.1765 |

| Δ | point [90 %] |
|---|---|
| win | +11.76 [-2.94, +27.94] |
| econ | +22.34 [+2.73, +45.53] |
| econ_med | +4.73 [-3.44, +12.69] |
| units@100 | -1.59 [-5.40, +10.71] |
| total@100 | +7.64 [+1.12, +13.70] |
| q_joint | +2.94 [-5.88, +11.76] |
| q_cond | +2.58 [-8.62, +13.54] |
| conv | +2.17 [-15.28, +20.80] |
| death_wall_per1k | +0.87 [+0.04, +1.71] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win +11.76 [-2.94, +27.94], econ~ +4.73 [-2.01, +11.55], units@100 -1.59 [-5.71, +7.70], total@100 +7.64 [+2.38, +11.51].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.361 | 6.228 | +16.2% | **yes** |
| death_self_per1k | 3.676 | 5.893 | +60.3% | **yes** |
| death_ally_body_per1k | 1.225 | 1.991 | +62.6% | **yes** |
| death_h2h_ally_per1k | 1.243 | 1.321 | +6.2% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | +50.00 | +72.98 | +7.14 | +1.809 |
| B | 20 | -10.00 | -13.16 | +10.00 | +0.916 |
| C | 12 | +0.00 | -15.07 | -16.67 | -0.153 |
| D | 4 | -50.00 | +13.55 | +0.00 | +4.170 |
| E | 4 | -50.00 | -33.52 | +0.00 | -6.225 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 1-3 | +0.00 | +5.72 | 1/4 vs 0/4 | +1.315 |
| live/autarky | A | 4 | 4-0 | +50.00 | +30.36 | 0/4 vs 0/4 | -1.763 |
| live/default | A | 4 | 2-2 | +50.00 | +8.59 | 2/2 vs 2/4 | +0.085 |
| live/devil | A | 4 | 4-0 | +100.00 | +284.97 | 0/0 vs 0/0 | +6.237 |
| live/dilemma | C | 4 | 4-0 | +50.00 | -23.02 | 0/0 vs 2/4 | -2.869 |
| live/islands | B | 4 | 0-4 | -50.00 | -2.30 | 0/4 vs 1/4 | +3.179 |
| live/maze | B | 4 | 4-0 | +75.00 | +18.43 | 2/4 vs 0/4 | +3.358 |
| live/portals | E | 4 | 2-2 | -50.00 | -33.52 | 2/4 vs 2/4 | -6.225 |
| live/queen_of_spades | A | 4 | 2-2 | +50.00 | +103.53 | 0/2 vs 0/2 | +3.172 |
| live/schooltime | B | 4 | 0-4 | -50.00 | -83.12 | 4/4 vs 4/4 | -3.227 |
| live/slithery_fight | D | 4 | 1-3 | -50.00 | +13.55 | 1/4 vs 1/4 | +4.170 |
| live/stripes | A | 4 | 2-2 | +0.00 | -10.63 | 0/2 vs 0/0 | +1.254 |
| live/tower_defense | A | 4 | 4-0 | +100.00 | +88.67 | 2/4 vs 0/2 | +2.673 |
| live/trauma | C | 4 | 0-4 | -50.00 | -27.29 | 2/4 vs 4/4 | -1.845 |
| live/trophy | A | 4 | 2-2 | +0.00 | +5.35 | 0/2 vs 0/0 | +1.003 |
| live/unsw | B | 4 | 2-2 | -25.00 | -4.55 | 1/4 vs 1/4 | -0.043 |
| live/weakhold | C | 4 | 4-0 | +0.00 | +5.09 | 2/2 vs 0/0 | +4.255 |

Runtime / fingerprint: cand `unswbc 1.2.3
installed the replay viewer into /usr/local/bin/code` `2c2027132789` panel `28a92b488185`; parent `unswbc 1.2.3` `fa93106401b1` panel `28a92b488185`.

