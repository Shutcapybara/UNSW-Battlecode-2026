# bokuto-27-exitsplit vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 242 | 237 |
| L | 30 | 35 |
| D | 0 | 0 |
| win | 0.8897 | 0.8713 |
| reached | 171 | 171 |
| q_cond | 0.4444 | 0.4854 |
| q_joint | 0.2794 | 0.3051 |
| q_dec_W | 73 | 80 |
| q_dec_L | 2 | 2 |
| conv | 0.9006 | 0.8713 |
| pearls@50 | 43.7574 | 42.4485 |
| pearls@100 | 124.0037 | 123.4228 |
| pearls@150 | 219.4301 | 214.8824 |
| pearls@250 | 412.8125 | 406.7574 |
| units@100 | 29.2206 | 28.6324 |
| total@100 | 74.6949 | 72.7647 |

| Δ | point [90 %] |
|---|---|
| win | +1.84 [-0.74, +4.41] |
| econ | +5.21 [+2.27, +8.24] |
| econ_med | +0.81 [+0.14, +2.64] |
| units@100 | +0.00 [+0.00, +0.00] |
| total@100 | +2.56 [+1.13, +4.70] |
| q_joint | -2.57 [-6.62, +1.12] |
| q_cond | -4.09 [-9.64, +1.18] |
| conv | +2.92 [-1.09, +6.64] |
| death_wall_per1k | +0.01 [-0.17, +0.19] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +1.84 [-1.10, +4.41], econ~ +0.81 [+0.06, +2.52], units@100 +0.00 [+0.00, +0.00], total@100 +2.56 [+1.20, +4.63].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.579 | 5.587 | +0.1% |  |
| death_self_per1k | 4.816 | 4.673 | -3.0% |  |
| death_ally_body_per1k | 1.663 | 1.649 | -0.8% |  |
| death_h2h_ally_per1k | 1.146 | 1.216 | +6.1% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +1.79 | -1.13 | -0.89 | -0.408 |
| B | 80 | +5.00 | -0.32 | +5.00 | +0.060 |
| C | 48 | -4.17 | +31.01 | -6.25 | +0.625 |
| D | 16 | -6.25 | +2.88 | -56.25 | -1.134 |
| E | 16 | +12.50 | +2.15 | +12.50 | +1.951 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 14-2 | +6.25 | -4.12 | 6/16 vs 5/16 | -0.156 |
| live/autarky | A | 16 | 16-0 | +6.25 | +2.77 | 3/3 vs 5/6 | -1.120 |
| live/default | A | 16 | 11-5 | +0.00 | +0.00 | 6/11 vs 6/11 | +0.000 |
| live/devil | A | 16 | 16-0 | +0.00 | +2.07 | 0/0 vs 0/0 | -0.440 |
| live/dilemma | C | 16 | 14-2 | -6.25 | -12.49 | 5/6 vs 7/8 | -0.668 |
| live/islands | B | 16 | 16-0 | +0.00 | +0.02 | 5/14 vs 3/10 | -0.045 |
| live/maze | B | 16 | 16-0 | +6.25 | +6.73 | 0/16 vs 1/16 | +0.821 |
| live/portals | E | 16 | 13-3 | +12.50 | +2.15 | 2/16 vs 0/16 | +1.951 |
| live/queen_of_spades | A | 16 | 15-1 | +0.00 | -0.82 | 5/7 vs 5/7 | +0.127 |
| live/schooltime | B | 16 | 16-0 | +0.00 | -2.27 | 15/15 vs 14/14 | -0.126 |
| live/slithery_fight | D | 16 | 14-2 | -6.25 | +2.88 | 0/16 vs 9/16 | -1.134 |
| live/stripes | A | 16 | 6-10 | +6.25 | -10.61 | 2/2 vs 1/2 | -0.910 |
| live/tower_defense | A | 16 | 13-3 | +0.00 | -1.30 | 2/7 vs 2/7 | -0.516 |
| live/trauma | C | 16 | 16-0 | +0.00 | +35.27 | 15/15 vs 15/15 | +0.312 |
| live/trophy | A | 16 | 16-0 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/unsw | B | 16 | 15-1 | +12.50 | -1.98 | 8/16 vs 7/16 | -0.192 |
| live/weakhold | C | 16 | 15-1 | -6.25 | +70.25 | 2/11 vs 3/11 | +2.231 |

Runtime / fingerprint: cand `unswbc 1.2.3
installed the replay viewer into /usr/local/bin/code` `568c1a862535` panel `39961c55d0e6`; parent `unswbc 1.2.3` `fa93106401b1` panel `39961c55d0e6`.

