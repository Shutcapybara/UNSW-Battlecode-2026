# bokuto-46-regions vs bokuto-41-atlas0 — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 235 | 238 |
| L | 35 | 34 |
| D | 2 | 0 |
| win | 0.8676 | 0.8750 |
| reached | 198 | 164 |
| q_cond | 0.5253 | 0.5305 |
| q_joint | 0.3824 | 0.3199 |
| q_dec_W | 99 | 85 |
| q_dec_L | 5 | 4 |
| conv | 0.8889 | 0.8963 |
| pearls@50 | 40.0000 | 43.6838 |
| pearls@100 | 112.7684 | 123.0993 |
| pearls@150 | 200.3787 | 210.9816 |
| pearls@250 | 396.3860 | 395.2169 |
| units@100 | 26.6691 | 28.4338 |
| total@100 | 68.5110 | 74.5551 |

| Δ | point [90 %] |
|---|---|
| win | -0.74 [-4.96, +3.32] |
| econ | +8.96 [-0.24, +18.37] |
| econ_med | -2.44 [-5.29, -0.02] |
| units@100 | +0.00 [-3.58, +0.00] |
| total@100 | -5.57 [-8.82, +0.00] |
| q_joint | +6.25 [-0.37, +12.15] |
| q_cond | -0.52 [-8.75, +7.47] |
| conv | -0.75 [-6.84, +5.02] |
| death_wall_per1k | +0.52 [+0.08, +0.96] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -0.74 [-4.60, +2.94], econ~ -2.44 [-4.62, -0.48], units@100 +0.00 [-3.03, +0.00], total@100 -5.57 [-8.39, -1.25].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.539 | 6.055 | +9.3% |  |
| death_self_per1k | 4.566 | 5.922 | +29.7% | **yes** |
| death_ally_body_per1k | 1.706 | 2.202 | +29.0% | **yes** |
| death_h2h_ally_per1k | 1.074 | 1.229 | +14.5% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +6.25 | +48.09 | +14.29 | +0.189 |
| B | 80 | -8.75 | -16.15 | -2.50 | +1.261 |
| C | 48 | -2.08 | -31.59 | +6.25 | +0.032 |
| D | 16 | -6.25 | +2.39 | -6.25 | +3.218 |
| E | 16 | +0.00 | -11.21 | +6.25 | -2.167 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 11-5 | -25.00 | -3.12 | 9/16 vs 8/16 | +0.973 |
| live/autarky | A | 16 | 14-2 | -12.50 | -4.54 | 8/14 vs 0/1 | -1.922 |
| live/default | A | 16 | 13-3 | +18.75 | +14.23 | 8/13 vs 5/12 | +0.057 |
| live/devil | A | 16 | 16-0 | +0.00 | +21.87 | 0/0 vs 0/1 | +1.991 |
| live/dilemma | C | 16 | 14-2 | -12.50 | -34.04 | 7/8 vs 5/5 | -2.201 |
| live/islands | B | 16 | 14-2 | -12.50 | +1.10 | 4/16 vs 4/12 | +3.395 |
| live/maze | B | 16 | 12-4 | -12.50 | +7.55 | 3/16 vs 5/16 | +2.849 |
| live/portals | E | 16 | 11-3 | +0.00 | -11.21 | 3/16 vs 2/15 | -2.167 |
| live/queen_of_spades | A | 16 | 16-0 | +12.50 | +82.86 | 6/10 vs 6/7 | +1.469 |
| live/schooltime | B | 16 | 16-0 | +0.00 | -75.74 | 16/16 vs 15/15 | -0.336 |
| live/slithery_fight | D | 16 | 15-1 | -6.25 | +2.39 | 6/15 vs 7/16 | +3.218 |
| live/stripes | A | 16 | 5-11 | +6.25 | -8.70 | 1/2 vs 0/0 | -3.461 |
| live/tower_defense | A | 16 | 15-1 | +25.00 | +207.84 | 4/10 vs 2/8 | +2.172 |
| live/trauma | C | 16 | 16-0 | +0.00 | -31.28 | 14/16 vs 16/16 | -1.273 |
| live/trophy | A | 16 | 15-1 | -6.25 | +23.10 | 2/8 vs 0/0 | +1.018 |
| live/unsw | B | 16 | 16-0 | +6.25 | -10.56 | 9/16 vs 11/16 | -0.575 |
| live/weakhold | C | 16 | 16-0 | +6.25 | -29.45 | 4/6 vs 1/8 | +3.569 |

Runtime / fingerprint: cand `unswbc 1.2.3` `2c2027132789` panel `39961c55d0e6`; parent `unswbc 1.2.3` `2fdf07f2dbc4` panel `39961c55d0e6`.

