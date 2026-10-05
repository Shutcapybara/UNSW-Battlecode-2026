# bokuto-61-mouth vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 228 | 237 |
| L | 44 | 35 |
| D | 0 | 0 |
| win | 0.8382 | 0.8713 |
| reached | 191 | 171 |
| q_cond | 0.5812 | 0.4854 |
| q_joint | 0.4081 | 0.3051 |
| q_dec_W | 109 | 80 |
| q_dec_L | 3 | 2 |
| conv | 0.8429 | 0.8713 |
| pearls@50 | 40.9265 | 42.4485 |
| pearls@100 | 118.2684 | 123.4228 |
| pearls@150 | 210.3750 | 214.8824 |
| pearls@250 | 410.6691 | 406.7574 |
| units@100 | 28.1397 | 28.6324 |
| total@100 | 71.7096 | 72.7647 |

| Δ | point [90 %] |
|---|---|
| win | -3.31 [-7.35, +1.10] |
| econ | +2.99 [-2.54, +8.57] |
| econ_med | +1.21 [-3.00, +4.53] |
| units@100 | -3.84 [-4.76, +0.00] |
| total@100 | +0.00 [-3.45, +3.99] |
| q_joint | +10.29 [+4.41, +15.81] |
| q_cond | +9.58 [+1.93, +17.04] |
| conv | -2.84 [-8.39, +3.08] |
| death_wall_per1k | +0.64 [+0.31, +1.00] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -3.31 [-7.35, +0.74], econ~ +1.21 [-1.92, +4.19], units@100 -3.84 [-4.76, -1.59], total@100 +0.00 [-3.34, +2.96].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.579 | 6.219 | +11.5% | **yes** |
| death_self_per1k | 4.816 | 5.581 | +15.9% | **yes** |
| death_ally_body_per1k | 1.663 | 2.103 | +26.5% | **yes** |
| death_h2h_ally_per1k | 1.146 | 1.277 | +11.4% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +0.89 | +8.99 | +14.29 | -0.145 |
| B | 80 | -7.50 | -5.24 | +15.00 | +1.826 |
| C | 48 | -2.08 | +9.88 | -4.17 | +0.268 |
| D | 16 | -31.25 | +8.10 | -18.75 | +3.049 |
| E | 16 | +12.50 | -23.63 | +31.25 | -1.092 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 9-7 | -25.00 | -3.28 | 7/16 vs 5/16 | +1.770 |
| live/autarky | A | 16 | 14-2 | -6.25 | +8.86 | 12/16 vs 5/6 | -3.172 |
| live/default | A | 16 | 13-3 | +12.50 | +12.73 | 8/13 vs 6/11 | +0.048 |
| live/devil | A | 16 | 16-0 | +0.00 | +7.99 | 0/0 vs 0/0 | +0.051 |
| live/dilemma | C | 16 | 15-1 | +0.00 | -44.48 | 4/5 vs 7/8 | -2.483 |
| live/islands | B | 16 | 13-3 | -18.75 | -3.15 | 6/16 vs 3/10 | +2.515 |
| live/maze | B | 16 | 13-3 | -12.50 | +19.46 | 5/15 vs 1/16 | +2.491 |
| live/portals | E | 16 | 13-3 | +12.50 | -23.63 | 5/16 vs 0/16 | -1.092 |
| live/queen_of_spades | A | 16 | 12-4 | -18.75 | -22.98 | 6/9 vs 5/7 | -0.281 |
| live/schooltime | B | 16 | 16-0 | +0.00 | -25.76 | 16/16 vs 14/14 | +2.976 |
| live/slithery_fight | D | 16 | 10-6 | -31.25 | +8.10 | 6/16 vs 9/16 | +3.049 |
| live/stripes | A | 16 | 5-11 | +0.00 | -14.19 | 1/3 vs 1/2 | +1.245 |
| live/tower_defense | A | 16 | 16-0 | +18.75 | +47.31 | 3/4 vs 2/7 | +0.576 |
| live/trauma | C | 16 | 16-0 | +0.00 | +69.47 | 16/16 vs 15/15 | -0.216 |
| live/trophy | A | 16 | 16-0 | +0.00 | +23.18 | 5/6 vs 0/0 | +0.520 |
| live/unsw | B | 16 | 16-0 | +18.75 | -13.46 | 8/16 vs 7/16 | -0.621 |
| live/weakhold | C | 16 | 15-1 | -6.25 | +4.66 | 3/8 vs 3/11 | +3.501 |

Runtime / fingerprint: cand `unswbc 1.2.3` `028c97bf6cc5` panel `39961c55d0e6`; parent `unswbc 1.2.3` `fa93106401b1` panel `39961c55d0e6`.

