# bokuto-17-atlas vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 28 | 21 |
| L | 40 | 47 |
| D | 0 | 0 |
| win | 0.4118 | 0.3088 |
| reached | 44 | 50 |
| q_cond | 0.3636 | 0.0000 |
| q_joint | 0.2353 | 0.0000 |
| q_dec_W | 6 | 0 |
| q_dec_L | 17 | 27 |
| conv | 0.3636 | 0.3000 |
| pearls@50 | 43.8529 | 38.2353 |
| pearls@100 | 128.1912 | 109.0735 |
| pearls@150 | 221.4118 | 190.5588 |
| pearls@250 | 424.7941 | 371.1029 |
| units@100 | 27.3824 | 24.2206 |
| total@100 | 66.7794 | 59.0588 |

| Δ | point [90 %] |
|---|---|
| win | +10.29 [-1.47, +22.06] |
| econ | +61.57 [+11.57, +117.23] |
| econ_med | +6.29 [-3.38, +25.94] |
| units@100 | +7.29 [-13.64, +29.79] |
| total@100 | +4.00 [-13.91, +27.12] |
| q_joint | +23.53 [+13.24, +32.35] |
| q_cond | +36.36 [+22.50, +48.94] |
| conv | +6.36 [-7.63, +19.86] |
| death_wall_per1k | -3.05 [-6.84, +0.12] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win +10.29 [-1.47, +22.06], econ~ +6.29 [-1.12, +19.60], units@100 +7.29 [-8.73, +27.66], total@100 +4.00 [-12.66, +21.45].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 8.088 | 5.038 | -37.7% |  |
| death_self_per1k | 3.520 | 3.983 | +13.1% | **yes** |
| death_ally_body_per1k | 1.257 | 1.615 | +28.5% | **yes** |
| death_h2h_ally_per1k | 1.293 | 2.269 | +75.6% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | +0.00 | +18.60 | +7.14 | +0.179 |
| B | 20 | +15.00 | +16.97 | +50.00 | +0.838 |
| C | 12 | +50.00 | +246.58 | +33.33 | -15.775 |
| D | 4 | +0.00 | +10.25 | +0.00 | +2.889 |
| E | 4 | -50.00 | +81.67 | +0.00 | -12.851 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 2-2 | +25.00 | +27.21 | 3/4 vs 0/4 | +0.769 |
| live/autarky | A | 4 | 0-4 | -50.00 | -31.22 | 0/2 vs 0/2 | -0.510 |
| live/default | A | 4 | 0-4 | -50.00 | +16.24 | 2/4 vs 0/2 | -0.106 |
| live/devil | A | 4 | 2-2 | +50.00 | +116.56 | 0/2 vs 0/0 | +0.673 |
| live/dilemma | C | 4 | 4-0 | +50.00 | -39.31 | 2/2 vs 0/4 | -1.887 |
| live/islands | B | 4 | 1-3 | -25.00 | -0.72 | 0/4 vs 0/4 | +0.000 |
| live/maze | B | 4 | 3-1 | +25.00 | +34.24 | 1/4 vs 0/4 | +1.250 |
| live/portals | E | 4 | 0-4 | -50.00 | +81.67 | 0/4 vs 0/4 | -12.851 |
| live/queen_of_spades | A | 4 | 2-2 | +0.00 | +39.23 | 0/0 vs 0/4 | +0.249 |
| live/schooltime | B | 4 | 2-2 | +50.00 | +8.29 | 4/4 vs 0/4 | +0.910 |
| live/slithery_fight | D | 4 | 1-3 | +0.00 | +10.25 | 0/4 vs 0/4 | +2.889 |
| live/stripes | A | 4 | 0-4 | +0.00 | -70.64 | 0/0 vs 0/0 | +0.362 |
| live/tower_defense | A | 4 | 2-2 | +0.00 | +11.73 | 0/0 vs 0/2 | +0.944 |
| live/trauma | C | 4 | 0-4 | +0.00 | +821.21 | 2/4 vs 0/4 | +4.380 |
| live/trophy | A | 4 | 4-0 | +50.00 | +48.30 | 0/0 vs 0/0 | -0.356 |
| live/unsw | B | 4 | 1-3 | +0.00 | +15.85 | 2/4 vs 0/4 | +1.259 |
| live/weakhold | C | 4 | 4-0 | +100.00 | -42.17 | 0/2 vs 0/4 | -49.817 |

Runtime / fingerprint: cand `unswbc 1.2.3` `caf30880252c` panel `28a92b488185`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `28a92b488185`.

