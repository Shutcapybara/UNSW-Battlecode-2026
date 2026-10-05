# bokuto-35-knownbeds vs bokuto-27-exitsplit — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 225 | 242 |
| L | 47 | 30 |
| D | 0 | 0 |
| win | 0.8272 | 0.8897 |
| reached | 172 | 171 |
| q_cond | 0.5058 | 0.4444 |
| q_joint | 0.3199 | 0.2794 |
| q_dec_W | 85 | 73 |
| q_dec_L | 4 | 2 |
| conv | 0.8547 | 0.9006 |
| pearls@50 | 45.7022 | 43.7574 |
| pearls@100 | 130.8382 | 124.0037 |
| pearls@150 | 227.7574 | 219.4301 |
| pearls@250 | 431.9816 | 412.8125 |
| units@100 | 29.4779 | 29.2206 |
| total@100 | 75.8566 | 74.6949 |

| Δ | point [90 %] |
|---|---|
| win | -6.25 [-10.29, -2.21] |
| econ | +48.68 [+22.57, +76.61] |
| econ_med | +3.73 [-0.82, +6.75] |
| units@100 | -3.23 [-4.76, +0.00] |
| total@100 | +0.00 [-2.56, +4.85] |
| q_joint | +4.04 [-1.47, +9.56] |
| q_cond | +6.14 [-1.17, +14.37] |
| conv | -4.59 [-10.02, +1.08] |
| death_wall_per1k | -0.91 [-1.37, -0.44] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -6.25 [-9.93, -1.84], econ~ +3.73 [+0.77, +6.33], units@100 -3.23 [-4.76, -1.33], total@100 +0.00 [-2.38, +3.88].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.587 | 4.677 | -16.3% |  |
| death_self_per1k | 4.673 | 4.623 | -1.1% |  |
| death_ally_body_per1k | 1.649 | 2.210 | +34.0% | **yes** |
| death_h2h_ally_per1k | 1.216 | 2.009 | +65.1% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -4.46 | +4.89 | +0.89 | +0.068 |
| B | 80 | -11.25 | +15.05 | +5.00 | +0.016 |
| C | 48 | +0.00 | +233.84 | -4.17 | -1.652 |
| D | 16 | +6.25 | +5.87 | +62.50 | +1.306 |
| E | 16 | -25.00 | +10.71 | -12.50 | -12.377 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 10-6 | -25.00 | +79.54 | 7/16 vs 6/16 | +1.906 |
| live/autarky | A | 16 | 14-2 | -12.50 | +12.20 | 5/9 vs 3/3 | +1.343 |
| live/default | A | 16 | 13-3 | +12.50 | +46.78 | 7/15 vs 6/11 | +0.098 |
| live/devil | A | 16 | 14-2 | -12.50 | -8.49 | 0/0 vs 0/0 | -0.997 |
| live/dilemma | C | 16 | 15-1 | +6.25 | -41.20 | 3/4 vs 5/6 | -1.744 |
| live/islands | B | 16 | 15-1 | -6.25 | +13.18 | 4/15 vs 5/14 | +0.123 |
| live/maze | B | 16 | 14-2 | -12.50 | -9.55 | 3/16 vs 0/16 | -1.287 |
| live/portals | E | 16 | 9-7 | -25.00 | +10.71 | 0/15 vs 2/16 | -12.377 |
| live/queen_of_spades | A | 16 | 13-3 | -12.50 | -23.53 | 4/5 vs 5/7 | -0.354 |
| live/schooltime | B | 16 | 16-0 | +0.00 | +14.92 | 15/15 vs 15/15 | +0.448 |
| live/slithery_fight | D | 16 | 15-1 | +6.25 | +5.87 | 10/16 vs 0/16 | +1.306 |
| live/stripes | A | 16 | 5-11 | -6.25 | +6.22 | 1/1 vs 2/2 | +1.256 |
| live/tower_defense | A | 16 | 14-2 | +6.25 | -5.86 | 2/3 vs 2/7 | -0.864 |
| live/trauma | C | 16 | 16-0 | +0.00 | +784.02 | 12/15 vs 15/15 | -1.008 |
| live/trophy | A | 16 | 15-1 | -6.25 | +6.89 | 0/0 vs 0/0 | -0.008 |
| live/unsw | B | 16 | 13-3 | -12.50 | -22.83 | 9/16 vs 8/16 | -1.111 |
| live/weakhold | C | 16 | 14-2 | -6.25 | -41.28 | 5/11 vs 2/11 | -2.203 |

Runtime / fingerprint: cand `unswbc 1.2.3` `71021e11586e` panel `39961c55d0e6`; parent `unswbc 1.2.3
installed the replay viewer into /usr/local/bin/code` `568c1a862535` panel `39961c55d0e6`.

