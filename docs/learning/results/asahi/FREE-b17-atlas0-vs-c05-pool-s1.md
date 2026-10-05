# asahi-26-b17-atlas0 vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 240 | 226 |
| L | 32 | 46 |
| D | 0 | 0 |
| win | 0.8824 | 0.8309 |
| reached | 160 | 146 |
| q_cond | 0.5000 | 0.0000 |
| q_joint | 0.2941 | 0.0000 |
| q_dec_W | 78 | 0 |
| q_dec_L | 1 | 5 |
| conv | 0.8875 | 0.8082 |
| pearls@50 | 42.0000 | 42.3088 |
| pearls@100 | 124.1949 | 126.0441 |
| pearls@150 | 221.1654 | 215.8162 |
| pearls@250 | 413.0846 | 395.0735 |
| units@100 | 28.7316 | 28.4816 |
| total@100 | 71.6029 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +5.15 [+0.74, +9.56] |
| econ | -0.37 [-4.07, +3.13] |
| econ_med | +2.50 [-0.91, +4.25] |
| units@100 | -1.56 [-1.56, +0.00] |
| total@100 | -0.67 [-3.03, +1.06] |
| q_joint | +29.41 [+24.63, +34.56] |
| q_cond | +50.00 [+42.55, +57.23] |
| conv | +7.93 [+1.00, +15.18] |
| death_wall_per1k | -0.96 [-2.16, +0.06] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +5.15 [+1.10, +9.19], econ~ +2.50 [-0.30, +4.06], units@100 -1.56 [-1.56, +0.00], total@100 -0.67 [-3.03, +0.53].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 6.252 | -13.3% |  |
| death_self_per1k | 3.585 | 3.787 | +5.6% |  |
| death_ally_body_per1k | 1.563 | 1.639 | +4.9% |  |
| death_h2h_ally_per1k | 1.238 | 1.365 | +10.3% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -0.89 | -4.00 | +12.50 | +0.215 |
| B | 80 | +3.75 | +8.17 | +56.25 | +0.904 |
| C | 48 | +18.75 | -8.02 | +25.00 | -8.377 |
| D | 16 | +31.25 | -1.60 | +56.25 | +2.237 |
| E | 16 | -12.50 | +6.45 | +0.00 | +0.518 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 14-2 | +0.00 | -2.04 | 12/16 vs 0/16 | +0.463 |
| live/autarky | A | 16 | 15-1 | -6.25 | -12.35 | 4/5 vs 0/3 | -0.391 |
| live/default | A | 16 | 12-4 | -6.25 | -11.70 | 3/6 vs 0/5 | -0.084 |
| live/devil | A | 16 | 16-0 | +6.25 | +8.97 | 0/0 vs 0/0 | +0.922 |
| live/dilemma | C | 16 | 16-0 | +6.25 | +5.70 | 3/3 vs 0/2 | +0.795 |
| live/islands | B | 16 | 16-0 | +0.00 | +4.83 | 5/15 vs 0/12 | +0.181 |
| live/maze | B | 16 | 16-0 | +6.25 | +10.00 | 3/16 vs 0/15 | +0.883 |
| live/portals | E | 16 | 10-6 | -12.50 | +6.45 | 0/16 vs 0/14 | +0.518 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | +4.77 | 5/6 vs 0/3 | -0.360 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +7.11 | 15/15 vs 0/16 | +0.955 |
| live/slithery_fight | D | 16 | 15-1 | +31.25 | -1.60 | 9/16 vs 0/16 | +2.237 |
| live/stripes | A | 16 | 6-10 | +6.25 | -10.87 | 2/3 vs 0/2 | -0.074 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | +0.86 | 0/2 vs 0/3 | +1.522 |
| live/trauma | C | 16 | 15-1 | +12.50 | +26.87 | 5/15 vs 0/16 | +1.515 |
| live/trophy | A | 16 | 14-2 | -6.25 | -7.65 | 0/0 vs 0/0 | -0.026 |
| live/unsw | B | 16 | 14-2 | +0.00 | +20.93 | 10/16 vs 0/16 | +2.039 |
| live/weakhold | C | 16 | 14-2 | +37.50 | -56.64 | 4/10 vs 0/7 | -27.440 |

Runtime / fingerprint: cand `unswbc 1.2.3` `0880fecfebd8` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

