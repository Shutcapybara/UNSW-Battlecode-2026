# bokuto-47-precious vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 225 | 226 |
| L | 46 | 46 |
| D | 1 | 0 |
| win | 0.8290 | 0.8309 |
| reached | 198 | 146 |
| q_cond | 0.5253 | 0.0000 |
| q_joint | 0.3824 | 0.0000 |
| q_dec_W | 101 | 0 |
| q_dec_L | 4 | 5 |
| conv | 0.8409 | 0.8082 |
| pearls@50 | 40.0000 | 42.3088 |
| pearls@100 | 112.7684 | 126.0441 |
| pearls@150 | 200.3787 | 215.8162 |
| pearls@250 | 396.3860 | 395.0735 |
| units@100 | 26.6691 | 28.4816 |
| total@100 | 68.5110 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -0.18 [-5.15, +4.78] |
| econ | -6.40 [-12.22, -1.00] |
| econ_med | -3.20 [-6.92, -0.79] |
| units@100 | -4.69 [-6.25, +0.00] |
| total@100 | +0.72 [-3.71, +4.00] |
| q_joint | +38.24 [+31.99, +44.12] |
| q_cond | +52.53 [+45.30, +59.32] |
| conv | +3.27 [-3.43, +10.22] |
| death_wall_per1k | -1.15 [-2.29, -0.14] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -0.18 [-5.34, +4.60], econ~ -3.20 [-5.64, -1.30], units@100 -4.69 [-6.25, -2.34], total@100 +0.72 [-2.86, +3.53].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 6.064 | -15.9% |  |
| death_self_per1k | 3.585 | 5.941 | +65.7% | **yes** |
| death_ally_body_per1k | 1.563 | 2.245 | +43.6% | **yes** |
| death_h2h_ally_per1k | 1.238 | 1.212 | -2.1% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -3.57 | +4.03 | +27.68 | +0.247 |
| B | 80 | -11.25 | -11.93 | +51.25 | +1.297 |
| C | 48 | +20.83 | -29.98 | +54.17 | -9.275 |
| D | 16 | +18.75 | +2.68 | +31.25 | +2.971 |
| E | 16 | -3.12 | +9.80 | +6.25 | -2.897 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -6.25 | -8.25 | 10/16 vs 0/16 | +1.179 |
| live/autarky | A | 16 | 15-1 | -6.25 | -5.04 | 12/15 vs 0/3 | -3.253 |
| live/default | A | 16 | 12-4 | -6.25 | -2.70 | 5/13 vs 0/5 | +0.087 |
| live/devil | A | 16 | 16-0 | +6.25 | +26.05 | 0/0 vs 0/0 | +2.072 |
| live/dilemma | C | 16 | 14-2 | -6.25 | -45.74 | 8/8 vs 0/2 | -2.731 |
| live/islands | B | 16 | 13-3 | -18.75 | +0.79 | 2/16 vs 0/12 | +2.443 |
| live/maze | B | 16 | 11-5 | -25.00 | +26.77 | 3/16 vs 0/15 | +3.018 |
| live/portals | E | 16 | 11-4 | -3.12 | +9.80 | 1/15 vs 0/14 | -2.897 |
| live/queen_of_spades | A | 16 | 14-2 | -12.50 | +40.34 | 6/10 vs 0/3 | -0.004 |
| live/schooltime | B | 16 | 14-2 | +0.00 | -78.42 | 16/16 vs 0/16 | -0.274 |
| live/slithery_fight | D | 16 | 13-3 | +18.75 | +2.68 | 5/16 vs 0/16 | +2.971 |
| live/stripes | A | 16 | 5-11 | +0.00 | -56.36 | 1/1 vs 0/2 | +1.010 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | -1.99 | 5/10 vs 0/3 | +0.739 |
| live/trauma | C | 16 | 16-0 | +18.75 | +6.11 | 14/16 vs 0/16 | -0.129 |
| live/trophy | A | 16 | 14-2 | -6.25 | +27.91 | 2/8 vs 0/0 | +1.079 |
| live/unsw | B | 16 | 13-3 | -6.25 | -0.54 | 10/16 vs 0/16 | +0.118 |
| live/weakhold | C | 16 | 16-0 | +50.00 | -50.30 | 4/6 vs 0/7 | -24.965 |

Runtime / fingerprint: cand `unswbc 1.2.3` `7322520f4e61` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

