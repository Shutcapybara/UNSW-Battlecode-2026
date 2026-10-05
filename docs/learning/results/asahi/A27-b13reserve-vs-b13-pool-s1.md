# asahi-27-b13-reserve vs bokuto-13-cull — seeds 1

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
| reached | 162 | 163 |
| q_cond | 0.5926 | 0.5767 |
| q_joint | 0.3529 | 0.3456 |
| q_dec_W | 94 | 92 |
| q_dec_L | 2 | 2 |
| conv | 0.9074 | 0.9325 |
| pearls@50 | 42.0809 | 42.0809 |
| pearls@100 | 121.5184 | 123.8382 |
| pearls@150 | 211.8493 | 219.0735 |
| pearls@250 | 401.2279 | 414.6985 |
| units@100 | 28.7132 | 28.6728 |
| total@100 | 72.8897 | 72.0368 |

| Δ | point [90 %] |
|---|---|
| win | -1.47 [-2.94, +0.00] |
| econ | -0.82 [-1.20, -0.47] |
| econ_med | -0.78 [-1.81, -0.27] |
| units@100 | +0.00 [+0.00, +0.00] |
| total@100 | +0.00 [+0.00, +0.63] |
| q_joint | +0.74 [-2.57, +4.04] |
| q_cond | +1.59 [-4.26, +7.23] |
| conv | -2.51 [-5.08, -0.08] |
| death_wall_per1k | -0.47 [-0.63, -0.33] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -1.47 [-2.96, +0.00], econ~ -0.78 [-1.76, -0.36], units@100 +0.00 [+0.00, +0.00], total@100 +0.00 [+0.00, +0.63].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 6.296 | 5.828 | -7.4% |  |
| death_self_per1k | 3.698 | 3.936 | +6.4% |  |
| death_ally_body_per1k | 1.517 | 1.534 | +1.2% |  |
| death_h2h_ally_per1k | 1.417 | 1.304 | -8.0% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +0.00 | +0.06 | +0.00 | +0.007 |
| B | 80 | -3.75 | -1.41 | +0.00 | -0.813 |
| C | 48 | +0.00 | +0.01 | +2.08 | -0.030 |
| D | 16 | -6.25 | -7.27 | +6.25 | -3.852 |
| E | 16 | +0.00 | +0.00 | +0.00 | +0.000 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 14-2 | -12.50 | -0.45 | 13/16 vs 11/16 | -0.448 |
| live/autarky | A | 16 | 14-2 | +0.00 | +0.00 | 3/6 vs 3/6 | +0.000 |
| live/default | A | 16 | 14-2 | +0.00 | +0.00 | 9/11 vs 9/11 | +0.009 |
| live/devil | A | 16 | 16-0 | +0.00 | +0.36 | 1/1 vs 1/1 | +0.003 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +0.00 | 4/4 vs 4/4 | +0.000 |
| live/islands | B | 16 | 16-0 | +0.00 | -1.74 | 5/14 vs 5/13 | -0.956 |
| live/maze | B | 16 | 15-1 | +0.00 | -0.10 | 3/14 vs 2/16 | -0.125 |
| live/portals | E | 16 | 10-6 | +0.00 | +0.00 | 0/15 vs 0/15 | +0.000 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | +0.00 | 5/5 vs 5/5 | +0.000 |
| live/schooltime | B | 16 | 15-1 | -6.25 | -0.78 | 15/15 vs 16/16 | -1.079 |
| live/slithery_fight | D | 16 | 14-2 | -6.25 | -7.27 | 9/16 vs 8/16 | -3.852 |
| live/stripes | A | 16 | 4-12 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | +0.00 | 0/3 vs 0/3 | +0.000 |
| live/trauma | C | 16 | 16-0 | +0.00 | +0.02 | 16/16 vs 15/15 | -0.091 |
| live/trophy | A | 16 | 14-2 | +0.00 | +0.03 | 0/0 vs 0/0 | +0.037 |
| live/unsw | B | 16 | 16-0 | +0.00 | -3.99 | 11/16 vs 13/16 | -1.458 |
| live/weakhold | C | 16 | 13-3 | +0.00 | +0.00 | 2/10 vs 2/10 | +0.000 |

Runtime / fingerprint: cand `unswbc 1.2.3` `16ceecff52c5` panel `39961c55d0e6`; parent `unswbc 1.2.3` `d192d721c406` panel `39961c55d0e6`.

