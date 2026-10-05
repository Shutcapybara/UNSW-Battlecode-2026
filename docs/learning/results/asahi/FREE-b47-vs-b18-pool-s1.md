# bokuto-47-precious vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 225 | 237 |
| L | 46 | 35 |
| D | 1 | 0 |
| win | 0.8290 | 0.8713 |
| reached | 198 | 171 |
| q_cond | 0.5253 | 0.4854 |
| q_joint | 0.3824 | 0.3051 |
| q_dec_W | 101 | 80 |
| q_dec_L | 4 | 2 |
| conv | 0.8409 | 0.8713 |
| pearls@50 | 40.0000 | 42.4485 |
| pearls@100 | 112.7684 | 123.4228 |
| pearls@150 | 200.3787 | 214.8824 |
| pearls@250 | 396.3860 | 406.7574 |
| units@100 | 26.6691 | 28.6324 |
| total@100 | 68.5110 | 72.7647 |

| Δ | point [90 %] |
|---|---|
| win | -4.23 [-8.27, -0.18] |
| econ | -2.76 [-8.62, +3.09] |
| econ_med | -1.33 [-5.37, +2.41] |
| units@100 | -2.67 [-4.05, +0.00] |
| total@100 | +2.11 [-1.73, +5.76] |
| q_joint | +7.72 [+1.10, +13.60] |
| q_cond | +3.99 [-3.99, +11.72] |
| conv | -3.04 [-8.63, +2.41] |
| death_wall_per1k | +0.48 [+0.11, +0.87] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -4.23 [-8.47, -0.36], econ~ -1.33 [-4.73, +1.77], units@100 -2.67 [-3.23, +0.00], total@100 +2.11 [-1.06, +4.19].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.579 | 6.064 | +8.7% |  |
| death_self_per1k | 4.816 | 5.941 | +23.3% | **yes** |
| death_ally_body_per1k | 1.663 | 2.245 | +35.0% | **yes** |
| death_h2h_ally_per1k | 1.146 | 1.212 | +5.7% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +0.00 | +14.29 | +10.71 | +0.151 |
| B | 80 | -11.25 | -16.98 | +13.75 | +1.187 |
| C | 48 | -2.08 | -18.67 | +2.08 | +0.056 |
| D | 16 | -12.50 | +10.41 | -25.00 | +3.606 |
| E | 16 | +3.12 | -16.52 | +6.25 | -2.526 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | +0.00 | -6.46 | 10/16 vs 5/16 | +0.937 |
| live/autarky | A | 16 | 15-1 | +0.00 | +8.17 | 12/15 vs 5/6 | -3.141 |
| live/default | A | 16 | 12-4 | +6.25 | +12.73 | 5/13 vs 6/11 | +0.113 |
| live/devil | A | 16 | 16-0 | +0.00 | +14.77 | 0/0 vs 0/0 | +0.905 |
| live/dilemma | C | 16 | 14-2 | -6.25 | -45.16 | 8/8 vs 7/8 | -2.988 |
| live/islands | B | 16 | 13-3 | -18.75 | -3.96 | 2/16 vs 3/10 | +3.372 |
| live/maze | B | 16 | 11-5 | -25.00 | +14.42 | 3/16 vs 1/16 | +2.209 |
| live/portals | E | 16 | 11-4 | +3.12 | -16.52 | 1/15 vs 0/16 | -2.526 |
| live/queen_of_spades | A | 16 | 14-2 | -6.25 | +57.13 | 6/10 vs 5/7 | +1.202 |
| live/schooltime | B | 16 | 14-2 | -12.50 | -74.88 | 16/16 vs 14/14 | -0.033 |
| live/slithery_fight | D | 16 | 13-3 | -12.50 | +10.41 | 5/16 vs 9/16 | +3.606 |
| live/stripes | A | 16 | 5-11 | +0.00 | -32.02 | 1/1 vs 1/2 | +0.273 |
| live/tower_defense | A | 16 | 15-1 | +12.50 | +16.63 | 5/10 vs 2/7 | +0.833 |
| live/trauma | C | 16 | 16-0 | +0.00 | -16.31 | 14/16 vs 15/15 | -1.423 |
| live/trophy | A | 16 | 14-2 | -12.50 | +22.60 | 2/8 vs 0/0 | +0.871 |
| live/unsw | B | 16 | 13-3 | +0.00 | -14.01 | 10/16 vs 7/16 | -0.550 |
| live/weakhold | C | 16 | 16-0 | +0.00 | +5.45 | 4/6 vs 3/11 | +4.580 |

Runtime / fingerprint: cand `unswbc 1.2.3` `7322520f4e61` panel `39961c55d0e6`; parent `unswbc 1.2.3` `fa93106401b1` panel `39961c55d0e6`.

