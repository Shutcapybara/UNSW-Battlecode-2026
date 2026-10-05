# bokuto-26-hunt vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 237 | 226 |
| L | 35 | 46 |
| D | 0 | 0 |
| win | 0.8713 | 0.8309 |
| reached | 180 | 146 |
| q_cond | 0.4833 | 0.0000 |
| q_joint | 0.3199 | 0.0000 |
| q_dec_W | 85 | 0 |
| q_dec_L | 1 | 5 |
| conv | 0.8722 | 0.8082 |
| pearls@50 | 42.3603 | 42.3088 |
| pearls@100 | 122.0368 | 126.0441 |
| pearls@150 | 215.2353 | 215.8162 |
| pearls@250 | 408.8897 | 395.0735 |
| units@100 | 28.6765 | 28.4816 |
| total@100 | 72.3824 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +4.04 [+0.00, +8.46] |
| econ | -2.72 [-6.68, +1.10] |
| econ_med | -2.00 [-5.44, +0.39] |
| units@100 | -1.56 [-1.89, +0.00] |
| total@100 | +0.00 [-4.08, +1.94] |
| q_joint | +31.99 [+26.84, +37.50] |
| q_cond | +48.33 [+41.07, +55.49] |
| conv | +6.40 [+0.23, +12.81] |
| death_wall_per1k | -1.81 [-3.04, -0.71] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +4.04 [+0.00, +8.09], econ~ -2.00 [-4.66, -0.10], units@100 -1.56 [-1.56, +0.00], total@100 +0.00 [-3.60, +1.20].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.402 | -25.1% |  |
| death_self_per1k | 3.585 | 4.852 | +35.3% | **yes** |
| death_ally_body_per1k | 1.563 | 1.618 | +3.5% |  |
| death_h2h_ally_per1k | 1.238 | 1.204 | -2.7% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +0.00 | -11.08 | +16.96 | -0.107 |
| B | 80 | -2.50 | +6.97 | +46.25 | +0.071 |
| C | 48 | +25.00 | -7.72 | +52.08 | -9.507 |
| D | 16 | +18.75 | -5.93 | +31.25 | -0.833 |
| E | 16 | -12.50 | +25.49 | +6.25 | -1.050 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -6.25 | -2.77 | 6/16 vs 0/16 | +0.094 |
| live/autarky | A | 16 | 16-0 | +0.00 | -14.22 | 6/10 vs 0/3 | -1.262 |
| live/default | A | 16 | 14-2 | +6.25 | -20.93 | 6/12 vs 0/5 | -0.029 |
| live/devil | A | 16 | 16-0 | +6.25 | +11.82 | 0/0 vs 0/0 | +0.817 |
| live/dilemma | C | 16 | 16-0 | +6.25 | +4.80 | 6/7 vs 0/2 | +0.127 |
| live/islands | B | 16 | 16-0 | +0.00 | +3.83 | 5/15 vs 0/12 | -0.818 |
| live/maze | B | 16 | 13-3 | -12.50 | +10.78 | 0/16 vs 0/15 | +0.803 |
| live/portals | E | 16 | 10-6 | -12.50 | +25.49 | 1/16 vs 0/14 | -1.050 |
| live/queen_of_spades | A | 16 | 15-1 | -6.25 | -8.81 | 4/6 vs 0/3 | -0.684 |
| live/schooltime | B | 16 | 15-1 | +6.25 | +6.06 | 16/16 vs 0/16 | -0.236 |
| live/slithery_fight | D | 16 | 13-3 | +18.75 | -5.93 | 5/16 vs 0/16 | -0.833 |
| live/stripes | A | 16 | 4-12 | -6.25 | -38.81 | 0/0 vs 0/2 | +0.857 |
| live/tower_defense | A | 16 | 14-2 | -6.25 | -11.65 | 3/7 vs 0/3 | -0.533 |
| live/trauma | C | 16 | 16-0 | +18.75 | +28.04 | 14/16 vs 0/16 | +0.982 |
| live/trophy | A | 16 | 16-0 | +6.25 | +5.05 | 0/0 vs 0/0 | +0.084 |
| live/unsw | B | 16 | 14-2 | +0.00 | +16.97 | 10/16 vs 0/16 | +0.512 |
| live/weakhold | C | 16 | 16-0 | +50.00 | -56.00 | 5/11 vs 0/7 | -29.630 |

Runtime / fingerprint: cand `unswbc 1.2.3` `c4bbe1c87566` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

