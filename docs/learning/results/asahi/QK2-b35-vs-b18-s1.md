# bokuto-35-knownbeds vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 32 | 30 |
| L | 36 | 38 |
| D | 0 | 0 |
| win | 0.4706 | 0.4412 |
| reached | 50 | 48 |
| q_cond | 0.3400 | 0.3542 |
| q_joint | 0.2500 | 0.2500 |
| q_dec_W | 11 | 9 |
| q_dec_L | 14 | 14 |
| conv | 0.4400 | 0.4583 |
| pearls@50 | 41.1176 | 38.9412 |
| pearls@100 | 113.3088 | 106.6324 |
| pearls@150 | 202.7353 | 186.1765 |
| pearls@250 | 402.1471 | 370.7941 |
| units@100 | 26.1029 | 24.3235 |
| total@100 | 64.8088 | 59.1765 |

| Δ | point [90 %] |
|---|---|
| win | +2.94 [-8.82, +14.71] |
| econ | +55.62 [+9.19, +107.17] |
| econ_med | +3.79 [-3.57, +13.56] |
| units@100 | -1.27 [-4.53, +7.37] |
| total@100 | +2.46 [-1.49, +13.20] |
| q_joint | +0.00 [-10.29, +10.29] |
| q_cond | -1.42 [-15.35, +13.06] |
| conv | -1.83 [-15.66, +12.42] |
| death_wall_per1k | -0.65 [-1.53, +0.10] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win +2.94 [-10.29, +16.18], econ~ +3.79 [-3.29, +13.28], units@100 -1.27 [-4.49, +6.55], total@100 +2.46 [-2.00, +6.49].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.361 | 4.713 | -12.1% |  |
| death_self_per1k | 3.676 | 4.156 | +13.1% | **yes** |
| death_ally_body_per1k | 1.225 | 1.819 | +48.5% | **yes** |
| death_h2h_ally_per1k | 1.243 | 1.876 | +50.9% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | +14.29 | +26.39 | -7.14 | +0.611 |
| B | 20 | -10.00 | +10.82 | +10.00 | +0.144 |
| C | 12 | +0.00 | +234.08 | +0.00 | -2.010 |
| D | 4 | +0.00 | -1.48 | +50.00 | +1.674 |
| E | 4 | +0.00 | +5.95 | -50.00 | -11.662 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 4-0 | +75.00 | +70.65 | 4/4 vs 0/4 | +1.580 |
| live/autarky | A | 4 | 2-2 | +0.00 | +27.20 | 0/4 vs 0/4 | +1.062 |
| live/default | A | 4 | 0-4 | +0.00 | +50.86 | 0/2 vs 2/4 | +0.115 |
| live/devil | A | 4 | 2-2 | +50.00 | +90.16 | 0/0 vs 0/0 | +1.668 |
| live/dilemma | C | 4 | 4-0 | +50.00 | -37.77 | 2/2 vs 2/4 | -2.796 |
| live/islands | B | 4 | 0-4 | -50.00 | +7.00 | 0/4 vs 1/4 | +1.855 |
| live/maze | B | 4 | 0-4 | -25.00 | -6.06 | 0/4 vs 0/4 | -1.007 |
| live/portals | E | 4 | 4-0 | +0.00 | +5.95 | 0/4 vs 2/4 | -11.662 |
| live/queen_of_spades | A | 4 | 0-4 | +0.00 | +47.42 | 0/4 vs 0/2 | +2.289 |
| live/schooltime | B | 4 | 2-2 | +0.00 | +11.00 | 4/4 vs 4/4 | -0.170 |
| live/slithery_fight | D | 4 | 3-1 | +0.00 | -1.48 | 3/4 vs 1/4 | +1.674 |
| live/stripes | A | 4 | 0-4 | -50.00 | -65.24 | 0/2 vs 0/0 | -1.135 |
| live/tower_defense | A | 4 | 2-2 | +50.00 | +5.12 | 0/0 vs 0/2 | +0.264 |
| live/trauma | C | 4 | 0-4 | -50.00 | +751.73 | 2/4 vs 4/4 | -1.646 |
| live/trophy | A | 4 | 4-0 | +50.00 | +29.20 | 0/0 vs 0/0 | +0.014 |
| live/unsw | B | 4 | 1-3 | -50.00 | -28.47 | 0/4 vs 1/4 | -1.535 |
| live/weakhold | C | 4 | 4-0 | +0.00 | -11.71 | 2/4 vs 0/0 | -1.588 |

Runtime / fingerprint: cand `unswbc 1.2.3` `71021e11586e` panel `28a92b488185`; parent `unswbc 1.2.3` `fa93106401b1` panel `28a92b488185`.

