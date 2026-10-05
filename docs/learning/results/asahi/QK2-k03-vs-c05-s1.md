# kenma-03-pocket-queen vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 25 | 21 |
| L | 43 | 47 |
| D | 0 | 0 |
| win | 0.3676 | 0.3088 |
| reached | 50 | 50 |
| q_cond | 0.0800 | 0.0000 |
| q_joint | 0.0588 | 0.0000 |
| q_dec_W | 0 | 0 |
| q_dec_L | 24 | 27 |
| conv | 0.3800 | 0.3000 |
| pearls@50 | 38.3824 | 38.2353 |
| pearls@100 | 110.2647 | 109.0735 |
| pearls@150 | 194.9853 | 190.5588 |
| pearls@250 | 372.8824 | 371.1029 |
| units@100 | 24.5294 | 24.2206 |
| total@100 | 59.8088 | 59.0588 |

| Δ | point [90 %] |
|---|---|
| win | +5.88 [-1.47, +14.71] |
| econ | +0.68 [-0.32, +1.88] |
| econ_med | +0.81 [-0.08, +1.29] |
| units@100 | +0.00 [-2.13, +0.00] |
| total@100 | +0.00 [+0.00, +0.00] |
| q_joint | +5.88 [+0.00, +11.76] |
| q_cond | +8.00 [+0.00, +17.78] |
| conv | +8.00 [-2.33, +19.05] |
| death_wall_per1k | -0.06 [-0.17, +0.02] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win +5.88 [-1.47, +13.24], econ~ +0.81 [-0.41, +1.42], units@100 +0.00 [-2.13, +0.00], total@100 +0.00 [-1.56, +1.14].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 8.088 | 8.025 | -0.8% |  |
| death_self_per1k | 3.520 | 3.478 | -1.2% |  |
| death_ally_body_per1k | 1.257 | 1.259 | +0.1% |  |
| death_h2h_ally_per1k | 1.293 | 1.278 | -1.1% |  |
| death_invalid_per1k | 0.000 | 0.006 | — | **yes** |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | +0.00 | -0.63 | +0.00 | -0.042 |
| B | 20 | +25.00 | +3.29 | +20.00 | -0.024 |
| C | 12 | +0.00 | +0.00 | +0.00 | +0.000 |
| D | 4 | -25.00 | -0.42 | +0.00 | -0.646 |
| E | 4 | +0.00 | +0.00 | +0.00 | +0.000 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 2-2 | +25.00 | +0.59 | 0/4 vs 0/4 | -0.014 |
| live/autarky | A | 4 | 2-2 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |
| live/default | A | 4 | 2-2 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |
| live/devil | A | 4 | 0-4 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/dilemma | C | 4 | 2-2 | +0.00 | +0.00 | 0/4 vs 0/4 | +0.000 |
| live/islands | B | 4 | 3-1 | +25.00 | +0.26 | 0/4 vs 0/4 | -0.621 |
| live/maze | B | 4 | 2-2 | +0.00 | +0.00 | 0/4 vs 0/4 | +0.000 |
| live/portals | E | 4 | 2-2 | +0.00 | +0.00 | 0/4 vs 0/4 | +0.000 |
| live/queen_of_spades | A | 4 | 2-2 | +0.00 | +0.00 | 0/4 vs 0/4 | +0.000 |
| live/schooltime | B | 4 | 4-0 | +100.00 | +15.60 | 4/4 vs 0/4 | +0.371 |
| live/slithery_fight | D | 4 | 0-4 | -25.00 | -0.42 | 0/4 vs 0/4 | -0.646 |
| live/stripes | A | 4 | 0-4 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/tower_defense | A | 4 | 2-2 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |
| live/trauma | C | 4 | 0-4 | +0.00 | +0.00 | 0/4 vs 0/4 | +0.000 |
| live/trophy | A | 4 | 2-2 | +0.00 | -4.40 | 0/0 vs 0/0 | -0.295 |
| live/unsw | B | 4 | 0-4 | -25.00 | -0.02 | 0/4 vs 0/4 | +0.144 |
| live/weakhold | C | 4 | 0-4 | +0.00 | +0.00 | 0/4 vs 0/4 | +0.000 |

Runtime / fingerprint: cand `unswbc 1.2.3` `e60733a926fc` panel `28a92b488185`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `28a92b488185`.

