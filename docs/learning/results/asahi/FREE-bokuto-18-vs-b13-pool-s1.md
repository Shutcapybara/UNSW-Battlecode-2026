# bokuto-18-queenfeed vs bokuto-13-cull — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 237 | 241 |
| L | 35 | 31 |
| D | 0 | 0 |
| win | 0.8713 | 0.8860 |
| reached | 171 | 163 |
| q_cond | 0.4854 | 0.5767 |
| q_joint | 0.3051 | 0.3456 |
| q_dec_W | 80 | 92 |
| q_dec_L | 2 | 2 |
| conv | 0.8713 | 0.9325 |
| pearls@50 | 42.4485 | 42.0809 |
| pearls@100 | 123.4228 | 123.8382 |
| pearls@150 | 214.8824 | 219.0735 |
| pearls@250 | 406.7574 | 414.6985 |
| units@100 | 28.6324 | 28.6728 |
| total@100 | 72.7647 | 72.0368 |

| Δ | point [90 %] |
|---|---|
| win | -1.47 [-5.15, +2.21] |
| econ | -4.56 [-8.72, -0.77] |
| econ_med | -1.64 [-3.69, +0.10] |
| units@100 | +0.00 [+0.00, +0.00] |
| total@100 | +0.00 [-3.14, +1.44] |
| q_joint | -4.04 [-9.58, +1.84] |
| q_cond | -9.13 [-17.29, -1.03] |
| conv | -6.12 [-11.44, -1.32] |
| death_wall_per1k | -0.72 [-1.02, -0.42] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -1.47 [-5.15, +2.21], econ~ -1.64 [-3.63, -0.09], units@100 +0.00 [+0.00, +0.00], total@100 +0.00 [-2.59, +0.63].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 6.296 | 5.579 | -11.4% |  |
| death_self_per1k | 3.698 | 4.816 | +30.2% | **yes** |
| death_ally_body_per1k | 1.517 | 1.663 | +9.6% |  |
| death_h2h_ally_per1k | 1.417 | 1.146 | -19.1% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -1.79 | -8.07 | +0.89 | -0.042 |
| B | 80 | -7.50 | -1.48 | -21.25 | -0.785 |
| C | 48 | +6.25 | -14.49 | +8.33 | -1.506 |
| D | 16 | +0.00 | -6.30 | +6.25 | -2.763 |
| E | 16 | +6.25 | +36.16 | +0.00 | -0.688 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -18.75 | -0.36 | 5/16 vs 11/16 | -0.299 |
| live/autarky | A | 16 | 15-1 | +6.25 | +1.42 | 5/6 vs 3/6 | +0.760 |
| live/default | A | 16 | 11-5 | -18.75 | -0.10 | 6/11 vs 9/11 | +0.063 |
| live/devil | A | 16 | 16-0 | +0.00 | +9.60 | 0/0 vs 1/1 | +1.376 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +0.24 | 7/8 vs 4/4 | -0.230 |
| live/islands | B | 16 | 16-0 | +0.00 | -1.89 | 3/10 vs 5/13 | -1.309 |
| live/maze | B | 16 | 15-1 | +0.00 | +1.53 | 1/16 vs 2/16 | +0.262 |
| live/portals | E | 16 | 11-5 | +6.25 | +36.16 | 0/16 vs 0/15 | -0.688 |
| live/queen_of_spades | A | 16 | 15-1 | -6.25 | -9.65 | 5/7 vs 5/5 | -0.824 |
| live/schooltime | B | 16 | 16-0 | +0.00 | -1.95 | 14/14 vs 16/16 | -1.073 |
| live/slithery_fight | D | 16 | 15-1 | +0.00 | -6.30 | 9/16 vs 8/16 | -2.763 |
| live/stripes | A | 16 | 5-11 | +6.25 | -56.36 | 1/2 vs 0/0 | -0.490 |
| live/tower_defense | A | 16 | 13-3 | -12.50 | -10.07 | 2/7 vs 0/3 | -1.225 |
| live/trauma | C | 16 | 16-0 | +0.00 | -46.40 | 15/15 vs 15/15 | -0.281 |
| live/trophy | A | 16 | 16-0 | +12.50 | +8.69 | 0/0 vs 0/0 | +0.046 |
| live/unsw | B | 16 | 13-3 | -18.75 | -4.74 | 7/16 vs 13/16 | -1.505 |
| live/weakhold | C | 16 | 16-0 | +18.75 | +2.70 | 3/11 vs 2/10 | -4.007 |

Runtime / fingerprint: cand `unswbc 1.2.3` `fa93106401b1` panel `39961c55d0e6`; parent `unswbc 1.2.3` `d192d721c406` panel `39961c55d0e6`.

