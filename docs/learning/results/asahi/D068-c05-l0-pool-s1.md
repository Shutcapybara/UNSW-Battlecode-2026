# asahi-12-c05-lambda0 vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 190 | 226 |
| L | 81 | 46 |
| D | 1 | 0 |
| win | 0.7004 | 0.8309 |
| reached | 163 | 146 |
| q_cond | 0.0000 | 0.0000 |
| q_joint | 0.0000 | 0.0000 |
| q_dec_W | 0 | 0 |
| q_dec_L | 7 | 5 |
| conv | 0.7331 | 0.8082 |
| pearls@50 | 37.0993 | 42.3088 |
| pearls@100 | 111.4228 | 126.0441 |
| pearls@150 | 200.7353 | 215.8162 |
| pearls@250 | 394.8824 | 395.0735 |
| units@100 | 23.7279 | 28.4816 |
| total@100 | 57.6654 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -13.05 [-18.38, -7.35] |
| econ | -4.01 [-10.10, +2.01] |
| econ_med | -7.88 [-12.02, -3.48] |
| units@100 | -14.06 [-17.53, -9.38] |
| total@100 | -15.97 [-17.64, -10.26] |
| q_joint | +0.00 [+0.00, +0.00] |
| q_cond | +0.00 [+0.00, +0.00] |
| conv | -7.51 [-14.87, +0.01] |
| death_wall_per1k | -0.25 [-1.45, +0.75] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -13.05 [-18.20, -7.90], econ~ -7.88 [-11.19, -4.06], units@100 -14.06 [-16.65, -9.45], total@100 -15.97 [-17.61, -10.41].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 6.965 | -3.4% |  |
| death_self_per1k | 3.585 | 4.282 | +19.5% | **yes** |
| death_ally_body_per1k | 1.563 | 2.254 | +44.2% | **yes** |
| death_h2h_ally_per1k | 1.238 | 1.573 | +27.1% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -20.54 | -4.56 | +0.00 | +0.925 |
| B | 80 | -7.50 | -11.89 | +0.00 | +0.567 |
| C | 48 | -8.33 | -1.82 | +0.00 | -7.672 |
| D | 16 | +0.00 | +21.50 | +0.00 | +5.863 |
| E | 16 | -15.62 | +7.09 | +0.00 | +3.625 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 14-2 | +0.00 | -10.28 | 0/16 vs 0/16 | +0.577 |
| live/autarky | A | 16 | 13-3 | -18.75 | -15.21 | 0/8 vs 0/3 | +1.978 |
| live/default | A | 16 | 12-4 | -6.25 | -12.17 | 0/9 vs 0/5 | +0.479 |
| live/devil | A | 16 | 5-11 | -62.50 | -41.40 | 0/0 vs 0/0 | -1.317 |
| live/dilemma | C | 16 | 10-6 | -31.25 | -13.72 | 0/6 vs 0/2 | +0.370 |
| live/islands | B | 16 | 12-4 | -25.00 | -6.48 | 0/14 vs 0/12 | +0.888 |
| live/maze | B | 16 | 13-3 | -12.50 | -25.29 | 0/14 vs 0/15 | -0.383 |
| live/portals | E | 16 | 9-6 | -15.62 | +7.09 | 0/16 vs 0/14 | +3.625 |
| live/queen_of_spades | A | 16 | 9-7 | -43.75 | -21.15 | 0/2 vs 0/3 | +1.962 |
| live/schooltime | B | 16 | 13-3 | -6.25 | -9.60 | 0/14 vs 0/16 | +0.763 |
| live/slithery_fight | D | 16 | 10-6 | +0.00 | +21.50 | 0/16 vs 0/16 | +5.863 |
| live/stripes | A | 16 | 10-6 | +31.25 | +89.31 | 0/2 vs 0/2 | +2.380 |
| live/tower_defense | A | 16 | 14-2 | -6.25 | -4.45 | 0/3 vs 0/3 | +1.062 |
| live/trauma | C | 16 | 9-7 | -25.00 | +65.57 | 0/15 vs 0/16 | +1.759 |
| live/trophy | A | 16 | 9-7 | -37.50 | -26.83 | 0/0 vs 0/0 | -0.067 |
| live/unsw | B | 16 | 15-1 | +6.25 | -7.81 | 0/16 vs 0/16 | +0.988 |
| live/weakhold | C | 16 | 13-3 | +31.25 | -57.32 | 0/12 vs 0/7 | -25.146 |

Runtime / fingerprint: cand `unswbc 1.2.3` `8ea849968b74` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

