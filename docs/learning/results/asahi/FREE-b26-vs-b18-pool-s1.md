# bokuto-26-hunt vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 237 | 237 |
| L | 35 | 35 |
| D | 0 | 0 |
| win | 0.8713 | 0.8713 |
| reached | 180 | 171 |
| q_cond | 0.4833 | 0.4854 |
| q_joint | 0.3199 | 0.3051 |
| q_dec_W | 85 | 80 |
| q_dec_L | 1 | 2 |
| conv | 0.8722 | 0.8713 |
| pearls@50 | 42.3603 | 42.4485 |
| pearls@100 | 122.0368 | 123.4228 |
| pearls@150 | 215.2353 | 214.8824 |
| pearls@250 | 408.8897 | 406.7574 |
| units@100 | 28.6765 | 28.6324 |
| total@100 | 72.3824 | 72.7647 |

| Δ | point [90 %] |
|---|---|
| win | +0.00 [-2.94, +2.57] |
| econ | +0.41 [-0.85, +1.94] |
| econ_med | -0.80 [-1.53, +0.07] |
| units@100 | +0.00 [+0.00, +0.00] |
| total@100 | +0.00 [-1.06, +0.70] |
| q_joint | +1.47 [-3.31, +5.88] |
| q_cond | -0.20 [-6.99, +6.00] |
| conv | +0.09 [-4.03, +4.28] |
| death_wall_per1k | -0.18 [-0.31, -0.04] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +0.00 [-3.31, +2.94], econ~ -0.80 [-1.46, +0.03], units@100 +0.00 [+0.00, +0.00], total@100 +0.00 [-1.11, +0.67].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.579 | 5.402 | -3.2% |  |
| death_self_per1k | 4.816 | 4.852 | +0.7% |  |
| death_ally_body_per1k | 1.663 | 1.618 | -2.7% |  |
| death_h2h_ally_per1k | 1.146 | 1.204 | +5.0% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +3.57 | +0.87 | +0.00 | -0.203 |
| B | 80 | -2.50 | -0.17 | +8.75 | -0.039 |
| C | 48 | +2.08 | +1.72 | +0.00 | -0.176 |
| D | 16 | -12.50 | +1.12 | -25.00 | -0.199 |
| E | 16 | -6.25 | -4.52 | +6.25 | -0.680 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | +0.00 | -0.93 | 6/16 vs 5/16 | -0.148 |
| live/autarky | A | 16 | 16-0 | +6.25 | -2.36 | 6/10 vs 5/6 | -1.149 |
| live/default | A | 16 | 14-2 | +18.75 | -7.54 | 6/12 vs 6/11 | -0.003 |
| live/devil | A | 16 | 16-0 | +0.00 | +1.89 | 0/0 vs 0/0 | -0.350 |
| live/dilemma | C | 16 | 16-0 | +6.25 | +3.12 | 6/7 vs 7/8 | -0.131 |
| live/islands | B | 16 | 16-0 | +0.00 | -1.12 | 5/15 vs 3/10 | +0.111 |
| live/maze | B | 16 | 13-3 | -12.50 | +0.71 | 0/16 vs 1/16 | -0.006 |
| live/portals | E | 16 | 10-6 | -6.25 | -4.52 | 1/16 vs 0/16 | -0.680 |
| live/queen_of_spades | A | 16 | 15-1 | +0.00 | +2.46 | 4/6 vs 5/7 | +0.522 |
| live/schooltime | B | 16 | 15-1 | -6.25 | -0.58 | 16/16 vs 14/14 | +0.004 |
| live/slithery_fight | D | 16 | 13-3 | -12.50 | +1.12 | 5/16 vs 9/16 | -0.199 |
| live/stripes | A | 16 | 4-12 | -6.25 | +9.29 | 0/0 vs 1/2 | +0.120 |
| live/tower_defense | A | 16 | 14-2 | +6.25 | +1.05 | 3/7 vs 2/7 | -0.439 |
| live/trauma | C | 16 | 16-0 | +0.00 | +1.18 | 14/16 vs 15/15 | -0.312 |
| live/trophy | A | 16 | 16-0 | +0.00 | +1.31 | 0/0 vs 0/0 | -0.124 |
| live/unsw | B | 16 | 14-2 | +6.25 | +1.07 | 10/16 vs 7/16 | -0.155 |
| live/weakhold | C | 16 | 16-0 | +0.00 | +0.86 | 5/11 vs 3/11 | -0.084 |

Runtime / fingerprint: cand `unswbc 1.2.3` `c4bbe1c87566` panel `39961c55d0e6`; parent `unswbc 1.2.3` `fa93106401b1` panel `39961c55d0e6`.

