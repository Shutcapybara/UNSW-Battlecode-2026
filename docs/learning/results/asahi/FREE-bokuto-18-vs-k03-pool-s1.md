# bokuto-18-queenfeed vs kenma-03-pocket-queen — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 237 | 220 |
| L | 35 | 52 |
| D | 0 | 0 |
| win | 0.8713 | 0.8088 |
| reached | 171 | 147 |
| q_cond | 0.4854 | 0.1020 |
| q_joint | 0.3051 | 0.0551 |
| q_dec_W | 80 | 13 |
| q_dec_L | 2 | 4 |
| conv | 0.8713 | 0.7687 |
| pearls@50 | 42.4485 | 42.5331 |
| pearls@100 | 123.4228 | 126.2463 |
| pearls@150 | 214.8824 | 216.1397 |
| pearls@250 | 406.7574 | 394.1728 |
| units@100 | 28.6324 | 28.4228 |
| total@100 | 72.7647 | 71.2757 |

| Δ | point [90 %] |
|---|---|
| win | +6.25 [+1.84, +10.66] |
| econ | -3.15 [-7.35, +0.57] |
| econ_med | -1.46 [-4.97, +1.02] |
| units@100 | +0.00 [+0.00, +0.00] |
| total@100 | +0.00 [-2.02, +2.21] |
| q_joint | +25.00 [+20.22, +30.51] |
| q_cond | +38.33 [+31.08, +45.86] |
| conv | +10.26 [+4.33, +16.52] |
| death_wall_per1k | -1.60 [-2.89, -0.52] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +6.25 [+1.84, +10.66], econ~ -1.46 [-4.24, +0.72], units@100 +0.00 [+0.00, +0.00], total@100 +0.00 [-1.31, +2.04].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.182 | 5.579 | -22.3% |  |
| death_self_per1k | 3.560 | 4.816 | +35.3% | **yes** |
| death_ally_body_per1k | 1.547 | 1.663 | +7.5% |  |
| death_h2h_ally_per1k | 1.236 | 1.146 | -7.2% |  |
| death_invalid_per1k | 0.005 | 0.000 | -100.0% |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -3.57 | -11.56 | +16.96 | +0.099 |
| B | 80 | +10.00 | +6.06 | +18.75 | +0.150 |
| C | 48 | +22.92 | -9.20 | +52.08 | -9.331 |
| D | 16 | +18.75 | -6.50 | +56.25 | -0.321 |
| E | 16 | -6.25 | +31.21 | +0.00 | -0.371 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | +12.50 | -1.16 | 5/16 vs 0/16 | +0.238 |
| live/autarky | A | 16 | 15-1 | -6.25 | -12.17 | 5/6 vs 0/3 | -0.113 |
| live/default | A | 16 | 11-5 | -12.50 | -14.19 | 6/11 vs 0/5 | -0.040 |
| live/devil | A | 16 | 16-0 | +6.25 | +9.65 | 0/0 vs 0/0 | +1.167 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +1.46 | 7/8 vs 0/2 | +0.258 |
| live/islands | B | 16 | 16-0 | +0.00 | +5.14 | 3/10 vs 0/14 | -0.848 |
| live/maze | B | 16 | 15-1 | +6.25 | +9.79 | 1/16 vs 0/16 | +0.796 |
| live/portals | E | 16 | 11-5 | -6.25 | +31.21 | 0/16 vs 0/14 | -0.371 |
| live/queen_of_spades | A | 16 | 15-1 | -6.25 | -12.18 | 5/7 vs 0/3 | -1.206 |
| live/schooltime | B | 16 | 16-0 | +6.25 | +1.09 | 14/14 vs 14/14 | -0.087 |
| live/slithery_fight | D | 16 | 15-1 | +18.75 | -6.50 | 9/16 vs 0/16 | -0.321 |
| live/stripes | A | 16 | 5-11 | +0.00 | -42.88 | 1/2 vs 0/2 | +0.737 |
| live/tower_defense | A | 16 | 13-3 | -12.50 | -12.79 | 2/7 vs 0/3 | -0.094 |
| live/trauma | C | 16 | 16-0 | +18.75 | +27.45 | 15/15 vs 0/16 | +1.294 |
| live/trophy | A | 16 | 16-0 | +6.25 | +3.65 | 0/0 vs 0/0 | +0.243 |
| live/unsw | B | 16 | 13-3 | +25.00 | +15.46 | 7/16 vs 1/16 | +0.652 |
| live/weakhold | C | 16 | 16-0 | +50.00 | -56.52 | 3/11 vs 0/7 | -29.546 |

Runtime / fingerprint: cand `unswbc 1.2.3` `fa93106401b1` panel `39961c55d0e6`; parent `unswbc 1.2.3` `e60733a926fc` panel `39961c55d0e6`.

