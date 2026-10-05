# kageyama-02-p1-hb1 vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 189 | 226 |
| L | 83 | 46 |
| D | 0 | 0 |
| win | 0.6949 | 0.8309 |
| reached | 159 | 146 |
| q_cond | 0.0000 | 0.0000 |
| q_joint | 0.0000 | 0.0000 |
| q_dec_W | 0 | 0 |
| q_dec_L | 8 | 5 |
| conv | 0.7233 | 0.8082 |
| pearls@50 | 37.0368 | 42.3088 |
| pearls@100 | 106.3897 | 126.0441 |
| pearls@150 | 191.2132 | 215.8162 |
| pearls@250 | 372.5331 | 395.0735 |
| units@100 | 24.7721 | 28.4816 |
| total@100 | 61.3162 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -13.60 [-19.49, -8.09] |
| econ | -5.83 [-11.78, +0.46] |
| econ_med | -10.02 [-13.80, -6.26] |
| units@100 | -11.11 [-15.59, -7.81] |
| total@100 | -12.59 [-16.80, -9.09] |
| q_joint | +0.00 [+0.00, +0.00] |
| q_cond | +0.00 [+0.00, +0.00] |
| conv | -8.49 [-16.62, -0.90] |
| death_wall_per1k | -0.93 [-1.88, -0.06] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -13.60 [-19.12, -8.09], econ~ -10.02 [-13.20, -5.98], units@100 -11.11 [-15.38, -8.51], total@100 -12.59 [-16.73, -9.10].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 6.280 | -12.9% |  |
| death_self_per1k | 3.585 | 3.716 | +3.7% |  |
| death_ally_body_per1k | 1.563 | 1.691 | +8.2% |  |
| death_h2h_ally_per1k | 1.238 | 0.978 | -21.0% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -21.43 | -9.63 | +0.00 | +0.585 |
| B | 80 | -7.50 | -7.24 | +0.00 | +0.015 |
| C | 48 | -4.17 | +2.36 | +0.00 | -5.314 |
| D | 16 | -6.25 | +2.23 | +0.00 | +2.047 |
| E | 16 | -25.00 | -4.76 | +0.00 | -6.130 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 15-1 | +6.25 | -0.21 | 0/16 vs 0/16 | +0.021 |
| live/autarky | A | 16 | 13-3 | -18.75 | -9.93 | 0/4 vs 0/3 | +2.057 |
| live/default | A | 16 | 11-5 | -12.50 | -23.35 | 0/8 vs 0/5 | +0.308 |
| live/devil | A | 16 | 5-11 | -62.50 | -46.78 | 0/1 vs 0/0 | -1.923 |
| live/dilemma | C | 16 | 12-4 | -18.75 | -14.08 | 0/4 vs 0/2 | +0.529 |
| live/islands | B | 16 | 15-1 | -6.25 | -8.97 | 0/12 vs 0/12 | +0.568 |
| live/maze | B | 16 | 11-5 | -25.00 | -23.55 | 0/16 vs 0/15 | -0.922 |
| live/portals | E | 16 | 8-8 | -25.00 | -4.76 | 0/14 vs 0/14 | -6.130 |
| live/queen_of_spades | A | 16 | 12-4 | -25.00 | -17.50 | 0/5 vs 0/3 | +0.961 |
| live/schooltime | B | 16 | 13-3 | -6.25 | -9.42 | 0/14 vs 0/16 | +0.073 |
| live/slithery_fight | D | 16 | 9-7 | -6.25 | +2.23 | 0/16 vs 0/16 | +2.047 |
| live/stripes | A | 16 | 8-8 | +18.75 | +69.71 | 0/1 vs 0/2 | +1.868 |
| live/tower_defense | A | 16 | 12-4 | -18.75 | -18.34 | 0/6 vs 0/3 | +0.785 |
| live/trauma | C | 16 | 12-4 | -6.25 | +88.29 | 0/16 vs 0/16 | +1.269 |
| live/trophy | A | 16 | 10-6 | -31.25 | -21.21 | 0/1 vs 0/0 | +0.037 |
| live/unsw | B | 16 | 13-3 | -6.25 | +5.97 | 0/16 vs 0/16 | +0.335 |
| live/weakhold | C | 16 | 10-6 | +12.50 | -67.12 | 0/9 vs 0/7 | -17.741 |

Runtime / fingerprint: cand `unswbc 1.2.3` `60e8ed781d52` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

