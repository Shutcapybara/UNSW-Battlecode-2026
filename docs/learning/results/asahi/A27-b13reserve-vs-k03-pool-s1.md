# asahi-27-b13-reserve vs kenma-03-pocket-queen — seeds 1

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
| reached | 162 | 147 |
| q_cond | 0.5926 | 0.1020 |
| q_joint | 0.3529 | 0.0551 |
| q_dec_W | 94 | 13 |
| q_dec_L | 2 | 4 |
| conv | 0.9074 | 0.7687 |
| pearls@50 | 42.0809 | 42.5331 |
| pearls@100 | 121.5184 | 126.2463 |
| pearls@150 | 211.8493 | 216.1397 |
| pearls@250 | 401.2279 | 394.1728 |
| units@100 | 28.7132 | 28.4228 |
| total@100 | 72.8897 | 71.2757 |

| Δ | point [90 %] |
|---|---|
| win | +6.25 [+2.57, +10.29] |
| econ | +1.03 [-3.30, +5.85] |
| econ_med | -2.05 [-4.78, +0.41] |
| units@100 | +0.00 [+0.00, +0.00] |
| total@100 | +0.00 [+0.00, +2.41] |
| q_joint | +29.78 [+24.26, +35.29] |
| q_cond | +49.06 [+41.17, +56.91] |
| conv | +13.87 [+7.77, +20.43] |
| death_wall_per1k | -1.35 [-2.46, -0.41] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +6.25 [+2.21, +10.29], econ~ -2.05 [-4.31, +0.17], units@100 +0.00 [+0.00, +0.00], total@100 +0.00 [+0.00, +1.96].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.182 | 5.828 | -18.9% |  |
| death_self_per1k | 3.560 | 3.936 | +10.6% | **yes** |
| death_ally_body_per1k | 1.547 | 1.534 | -0.8% |  |
| death_h2h_ally_per1k | 1.236 | 1.304 | +5.5% |  |
| death_invalid_per1k | 0.005 | 0.000 | -100.0% |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -1.79 | -3.07 | +16.07 | +0.148 |
| B | 80 | +13.75 | +6.20 | +40.00 | +0.122 |
| C | 48 | +16.67 | +5.87 | +45.83 | -7.855 |
| D | 16 | +12.50 | -7.49 | +56.25 | -1.409 |
| E | 16 | -12.50 | -2.11 | +0.00 | +0.317 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 14-2 | +18.75 | -1.26 | 13/16 vs 0/16 | +0.089 |
| live/autarky | A | 16 | 14-2 | -12.50 | -13.40 | 3/6 vs 0/3 | -0.872 |
| live/default | A | 16 | 14-2 | +6.25 | -13.99 | 9/11 vs 0/5 | -0.094 |
| live/devil | A | 16 | 16-0 | +6.25 | +0.47 | 1/1 vs 0/0 | -0.206 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +1.33 | 4/4 vs 0/2 | +0.487 |
| live/islands | B | 16 | 16-0 | +0.00 | +5.31 | 5/14 vs 0/14 | -0.494 |
| live/maze | B | 16 | 15-1 | +6.25 | +8.28 | 3/14 vs 0/16 | +0.408 |
| live/portals | E | 16 | 10-6 | -12.50 | -2.11 | 0/15 vs 0/14 | +0.317 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | -2.44 | 5/5 vs 0/3 | -0.383 |
| live/schooltime | B | 16 | 15-1 | +0.00 | +2.37 | 15/15 vs 14/14 | -0.094 |
| live/slithery_fight | D | 16 | 14-2 | +12.50 | -7.49 | 9/16 vs 0/16 | -1.409 |
| live/stripes | A | 16 | 4-12 | -6.25 | +15.50 | 0/0 vs 0/2 | +1.227 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | -2.93 | 0/3 vs 0/3 | +1.131 |
| live/trauma | C | 16 | 16-0 | +18.75 | +73.37 | 16/16 vs 0/16 | +1.485 |
| live/trophy | A | 16 | 14-2 | -6.25 | -4.71 | 0/0 vs 0/0 | +0.233 |
| live/unsw | B | 16 | 16-0 | +43.75 | +16.30 | 11/16 vs 1/16 | +0.699 |
| live/weakhold | C | 16 | 13-3 | +31.25 | -57.09 | 2/10 vs 0/7 | -25.538 |

Runtime / fingerprint: cand `unswbc 1.2.3` `16ceecff52c5` panel `39961c55d0e6`; parent `unswbc 1.2.3` `e60733a926fc` panel `39961c55d0e6`.

