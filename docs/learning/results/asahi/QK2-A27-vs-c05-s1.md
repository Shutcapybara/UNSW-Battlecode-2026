# asahi-27-b13-reserve vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 33 | 21 |
| L | 35 | 47 |
| D | 0 | 0 |
| win | 0.4853 | 0.3088 |
| reached | 52 | 50 |
| q_cond | 0.4231 | 0.0000 |
| q_joint | 0.3235 | 0.0000 |
| q_dec_W | 14 | 0 |
| q_dec_L | 12 | 27 |
| conv | 0.4808 | 0.3000 |
| pearls@50 | 39.4118 | 38.2353 |
| pearls@100 | 106.4265 | 109.0735 |
| pearls@150 | 184.6618 | 190.5588 |
| pearls@250 | 371.5147 | 371.1029 |
| units@100 | 25.1618 | 24.2206 |
| total@100 | 61.5147 | 59.0588 |

| Δ | point [90 %] |
|---|---|
| win | +17.65 [+10.29, +25.00] |
| econ | +9.45 [-1.74, +21.94] |
| econ_med | -4.70 [-10.50, +3.68] |
| units@100 | -0.84 [-8.66, +6.03] |
| total@100 | -6.05 [-11.05, +9.54] |
| q_joint | +32.35 [+20.59, +44.12] |
| q_cond | +42.31 [+28.57, +55.56] |
| conv | +18.08 [+8.65, +28.27] |
| death_wall_per1k | -2.51 [-5.95, +0.37] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win +17.65 [+4.34, +30.88], econ~ -4.70 [-9.36, +2.61], units@100 -0.84 [-8.11, +5.59], total@100 -6.05 [-11.05, +8.44].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 8.088 | 5.579 | -31.0% |  |
| death_self_per1k | 3.520 | 3.614 | +2.7% |  |
| death_ally_body_per1k | 1.257 | 1.585 | +26.1% | **yes** |
| death_h2h_ally_per1k | 1.293 | 1.041 | -19.5% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | +14.29 | +16.65 | +28.57 | +0.061 |
| B | 20 | +20.00 | +6.58 | +35.00 | +0.243 |
| C | 12 | +33.33 | +9.92 | +50.00 | -13.907 |
| D | 4 | +0.00 | -1.14 | +25.00 | -2.449 |
| E | 4 | +0.00 | -17.36 | +0.00 | -0.118 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 1-3 | +0.00 | -15.23 | 0/4 vs 0/4 | -0.304 |
| live/autarky | A | 4 | 2-2 | +0.00 | -20.73 | 4/4 vs 0/2 | -1.253 |
| live/default | A | 4 | 2-2 | +0.00 | -23.39 | 2/4 vs 0/2 | -0.047 |
| live/devil | A | 4 | 2-2 | +50.00 | +85.78 | 0/0 vs 0/0 | +1.069 |
| live/dilemma | C | 4 | 2-2 | +0.00 | -11.19 | 0/0 vs 0/4 | +1.273 |
| live/islands | B | 4 | 2-2 | +0.00 | -4.15 | 0/4 vs 0/4 | -0.297 |
| live/maze | B | 4 | 2-2 | +0.00 | +20.11 | 0/4 vs 0/4 | +0.960 |
| live/portals | E | 4 | 2-2 | +0.00 | -17.36 | 0/4 vs 0/4 | -0.118 |
| live/queen_of_spades | A | 4 | 2-2 | +0.00 | +2.71 | 2/4 vs 0/4 | -1.346 |
| live/schooltime | B | 4 | 2-2 | +50.00 | +15.07 | 4/4 vs 0/4 | +0.297 |
| live/slithery_fight | D | 4 | 1-3 | +0.00 | -1.14 | 1/4 vs 0/4 | -2.449 |
| live/stripes | A | 4 | 2-2 | +50.00 | +83.90 | 0/0 vs 0/0 | +2.521 |
| live/tower_defense | A | 4 | 2-2 | +0.00 | -4.43 | 0/4 vs 0/2 | -0.818 |
| live/trauma | C | 4 | 2-2 | +50.00 | +102.47 | 4/4 vs 0/4 | +4.316 |
| live/trophy | A | 4 | 2-2 | +0.00 | -7.33 | 0/0 vs 0/0 | +0.301 |
| live/unsw | B | 4 | 3-1 | +50.00 | +17.09 | 3/4 vs 0/4 | +0.559 |
| live/weakhold | C | 4 | 2-2 | +50.00 | -61.53 | 2/4 vs 0/4 | -47.308 |

Runtime / fingerprint: cand `unswbc 1.2.3` `16ceecff52c5` panel `28a92b488185`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `28a92b488185`.

