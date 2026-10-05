# kenma-03-pocket-queen vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 220 | 226 |
| L | 52 | 46 |
| D | 0 | 0 |
| win | 0.8088 | 0.8309 |
| reached | 147 | 146 |
| q_cond | 0.1020 | 0.0000 |
| q_joint | 0.0551 | 0.0000 |
| q_dec_W | 13 | 0 |
| q_dec_L | 4 | 5 |
| conv | 0.7687 | 0.8082 |
| pearls@50 | 42.5331 | 42.3088 |
| pearls@100 | 126.2463 | 126.0441 |
| pearls@150 | 216.1397 | 215.8162 |
| pearls@250 | 394.1728 | 395.0735 |
| units@100 | 28.4228 | 28.4816 |
| total@100 | 71.2757 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -2.21 [-4.41, -0.37] |
| econ | +0.28 [-0.01, +0.59] |
| econ_med | -0.11 [-0.28, +0.32] |
| units@100 | +0.00 [-1.56, +0.00] |
| total@100 | +0.00 [+0.00, +0.00] |
| q_joint | +5.51 [+2.57, +8.46] |
| q_cond | +10.20 [+4.64, +15.59] |
| conv | -3.95 [-8.02, -0.39] |
| death_wall_per1k | -0.03 [-0.06, -0.01] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -2.21 [-4.41, +0.37], econ~ -0.11 [-0.29, +0.31], units@100 +0.00 [-1.56, +0.00], total@100 +0.00 [+0.00, +0.00].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 7.182 | -0.4% |  |
| death_self_per1k | 3.585 | 3.560 | -0.7% |  |
| death_ally_body_per1k | 1.563 | 1.547 | -1.0% |  |
| death_h2h_ally_per1k | 1.238 | 1.236 | -0.2% |  |
| death_invalid_per1k | 0.000 | 0.005 | — | **yes** |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +0.00 | +0.02 | +0.00 | -0.003 |
| B | 80 | -10.00 | +1.02 | +18.75 | -0.040 |
| C | 48 | +0.00 | +0.00 | +0.00 | +0.000 |
| D | 16 | +12.50 | -0.52 | +0.00 | -0.313 |
| E | 16 | +0.00 | +0.00 | +0.00 | +0.000 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 11-5 | -18.75 | -0.74 | 0/16 vs 0/16 | +0.004 |
| live/autarky | A | 16 | 16-0 | +0.00 | +0.00 | 0/3 vs 0/3 | +0.000 |
| live/default | A | 16 | 13-3 | +0.00 | -0.02 | 0/5 vs 0/5 | +0.015 |
| live/devil | A | 16 | 15-1 | +0.00 | -0.00 | 0/0 vs 0/0 | +0.000 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |
| live/islands | B | 16 | 16-0 | +0.00 | -0.12 | 0/14 vs 0/12 | -0.081 |
| live/maze | B | 16 | 14-2 | -6.25 | +0.06 | 0/16 vs 0/15 | +0.013 |
| live/portals | E | 16 | 12-4 | +0.00 | +0.00 | 0/14 vs 0/14 | +0.000 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | +0.00 | 0/3 vs 0/3 | +0.000 |
| live/schooltime | B | 16 | 15-1 | +6.25 | +5.53 | 14/14 vs 0/16 | -0.153 |
| live/slithery_fight | D | 16 | 12-4 | +12.50 | -0.52 | 0/16 vs 0/16 | -0.313 |
| live/stripes | A | 16 | 5-11 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | +0.00 | 0/3 vs 0/3 | +0.000 |
| live/trauma | C | 16 | 13-3 | +0.00 | +0.00 | 0/16 vs 0/16 | +0.000 |
| live/trophy | A | 16 | 15-1 | +0.00 | +0.18 | 0/0 vs 0/0 | -0.035 |
| live/unsw | B | 16 | 9-7 | -31.25 | +0.40 | 1/16 vs 0/16 | +0.015 |
| live/weakhold | C | 16 | 8-8 | +0.00 | +0.00 | 0/7 vs 0/7 | +0.000 |

Runtime / fingerprint: cand `unswbc 1.2.3` `e60733a926fc` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

