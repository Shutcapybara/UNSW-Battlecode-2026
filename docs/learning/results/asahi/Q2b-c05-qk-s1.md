# asahi-25-q2bcrown-c05 vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (qk only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 27 | 32 |
| L | 41 | 36 |
| D | 0 | 0 |
| win | 0.3971 | 0.4706 |
| reached | 47 | 47 |
| q_cond | 0.1064 | 0.0000 |
| q_joint | 0.0735 | 0.0000 |
| q_dec_W | 5 | 0 |
| q_dec_L | 7 | 6 |
| conv | 0.4043 | 0.4681 |
| pearls@50 | 37.9118 | 37.8676 |
| pearls@100 | 107.9559 | 108.6618 |
| pearls@150 | 185.5588 | 187.7353 |
| pearls@250 | 356.2206 | 362.8824 |
| units@100 | 23.3235 | 24.0294 |
| total@100 | 57.5735 | 58.6912 |

| Δ | point [90 %] |
|---|---|
| win | -7.35 [-16.18, +2.94] |
| econ | -1.40 [-3.45, +0.76] |
| econ_med | -0.71 [-2.08, +0.75] |
| units@100 | -0.80 [-5.71, +0.00] |
| total@100 | -2.79 [-5.53, +0.12] |
| q_joint | +7.35 [+1.47, +13.24] |
| q_cond | +10.64 [+2.33, +20.00] |
| conv | -6.38 [-20.02, +8.44] |
| death_wall_per1k | +0.08 [-0.16, +0.33] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win -7.35 [-17.65, +2.94], econ~ -0.71 [-2.32, +0.88], units@100 -0.80 [-5.26, +0.00], total@100 -2.79 [-5.10, +0.00].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 8.791 | 8.868 | +0.9% |  |
| death_self_per1k | 3.399 | 3.244 | -4.6% |  |
| death_ally_body_per1k | 1.285 | 1.275 | -0.8% |  |
| death_h2h_ally_per1k | 1.244 | 1.181 | -5.1% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | -3.57 | -0.09 | +3.57 | +0.041 |
| B | 20 | -5.00 | -0.58 | +5.00 | +0.169 |
| C | 12 | +8.33 | -3.59 | +25.00 | -0.084 |
| D | 4 | -50.00 | +1.66 | +0.00 | -0.723 |
| E | 4 | -50.00 | -11.14 | +0.00 | +1.164 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 2-2 | +0.00 | -5.24 | 1/4 vs 0/4 | +0.338 |
| live/autarky | A | 4 | 2-2 | -25.00 | +1.11 | 0/2 vs 0/4 | +2.049 |
| live/default | A | 4 | 3-1 | +25.00 | +10.96 | 1/3 vs 0/4 | -0.202 |
| live/devil | A | 4 | 2-2 | +0.00 | -1.81 | 0/0 vs 0/0 | -0.084 |
| live/dilemma | C | 4 | 1-3 | +0.00 | -3.64 | 0/3 vs 0/1 | -1.220 |
| live/islands | B | 4 | 1-3 | -50.00 | -0.29 | 0/4 vs 0/4 | -0.025 |
| live/maze | B | 4 | 3-1 | +0.00 | +2.13 | 0/4 vs 0/4 | +0.628 |
| live/portals | E | 4 | 1-3 | -50.00 | -11.14 | 0/4 vs 0/4 | +1.164 |
| live/queen_of_spades | A | 4 | 1-3 | +0.00 | -2.23 | 0/3 vs 0/3 | -0.436 |
| live/schooltime | B | 4 | 0-4 | +0.00 | +0.00 | 0/4 vs 0/4 | +0.000 |
| live/slithery_fight | D | 4 | 0-4 | -50.00 | +1.66 | 0/4 vs 0/4 | -0.723 |
| live/stripes | A | 4 | 3-1 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/tower_defense | A | 4 | 1-3 | -25.00 | -11.02 | 0/2 vs 0/1 | -0.518 |
| live/trauma | C | 4 | 3-1 | +25.00 | -7.13 | 3/4 vs 0/4 | +0.969 |
| live/trophy | A | 4 | 2-2 | +0.00 | +2.37 | 0/0 vs 0/0 | -0.522 |
| live/unsw | B | 4 | 1-3 | +25.00 | +0.48 | 0/4 vs 0/4 | -0.095 |
| live/weakhold | C | 4 | 1-3 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |

Runtime / fingerprint: cand `unswbc 1.2.3` `3959d1c5f000` panel `e116a1dcc99b`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `e116a1dcc99b`.

