# kenma-28-harvest-reserve vs bokuto-13-cull — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 241 | 241 |
| L | 31 | 31 |
| D | 0 | 0 |
| win | 0.8860 | 0.8860 |
| reached | 166 | 163 |
| q_cond | 0.5723 | 0.5767 |
| q_joint | 0.3493 | 0.3456 |
| q_dec_W | 93 | 92 |
| q_dec_L | 2 | 2 |
| conv | 0.9337 | 0.9325 |
| pearls@50 | 42.0846 | 42.0809 |
| pearls@100 | 121.9559 | 123.8382 |
| pearls@150 | 213.4485 | 219.0735 |
| pearls@250 | 401.6875 | 414.6985 |
| units@100 | 28.8676 | 28.6728 |
| total@100 | 73.0441 | 72.0368 |

| Δ | point [90 %] |
|---|---|
| win | +0.00 [-1.10, +1.10] |
| econ | -0.82 [-1.18, -0.50] |
| econ_med | -0.85 [-1.79, -0.24] |
| units@100 | +0.00 [+0.00, +1.54] |
| total@100 | +0.00 [+0.00, +1.89] |
| q_joint | +0.37 [-4.04, +4.41] |
| q_cond | -0.44 [-7.90, +6.67] |
| conv | +0.12 [-1.91, +2.10] |
| death_wall_per1k | -0.41 [-0.57, -0.27] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +0.00 [-1.47, +1.10], econ~ -0.85 [-1.75, -0.27], units@100 +0.00 [+0.00, +1.27], total@100 +0.00 [+0.00, +1.70].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 6.296 | 5.883 | -6.6% |  |
| death_self_per1k | 3.698 | 3.915 | +5.9% |  |
| death_ally_body_per1k | 1.517 | 1.539 | +1.5% |  |
| death_h2h_ally_per1k | 1.417 | 1.337 | -5.7% |  |
| death_invalid_per1k | 0.000 | 0.005 | — | **yes** |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +0.00 | -0.23 | +0.00 | +0.007 |
| B | 80 | +0.00 | -1.35 | -2.50 | -0.632 |
| C | 48 | +0.00 | +0.01 | +2.08 | -0.015 |
| D | 16 | +0.00 | -5.58 | +12.50 | -3.875 |
| E | 16 | +0.00 | +0.00 | +0.00 | +0.000 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 16-0 | +0.00 | -0.96 | 12/16 vs 11/16 | -0.564 |
| live/autarky | A | 16 | 14-2 | +0.00 | +0.00 | 3/6 vs 3/6 | +0.000 |
| live/default | A | 16 | 14-2 | +0.00 | +0.00 | 9/11 vs 9/11 | -0.007 |
| live/devil | A | 16 | 16-0 | +0.00 | -1.10 | 1/1 vs 1/1 | +0.085 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +0.00 | 4/4 vs 4/4 | +0.000 |
| live/islands | B | 16 | 16-0 | +0.00 | -1.72 | 4/15 vs 5/13 | -1.085 |
| live/maze | B | 16 | 16-0 | +6.25 | -0.31 | 5/16 vs 2/16 | -0.017 |
| live/portals | E | 16 | 10-6 | +0.00 | +0.00 | 0/15 vs 0/15 | +0.000 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | +0.00 | 5/5 vs 5/5 | +0.000 |
| live/schooltime | B | 16 | 16-0 | +0.00 | +0.00 | 16/16 vs 16/16 | -0.023 |
| live/slithery_fight | D | 16 | 15-1 | +0.00 | -5.58 | 10/16 vs 8/16 | -3.875 |
| live/stripes | A | 16 | 4-12 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | +0.00 | 0/3 vs 0/3 | +0.000 |
| live/trauma | C | 16 | 16-0 | +0.00 | +0.02 | 16/16 vs 15/15 | -0.046 |
| live/trophy | A | 16 | 14-2 | +0.00 | -0.53 | 0/0 vs 0/0 | -0.029 |
| live/unsw | B | 16 | 15-1 | -6.25 | -3.76 | 8/16 vs 13/16 | -1.472 |
| live/weakhold | C | 16 | 13-3 | +0.00 | +0.00 | 2/10 vs 2/10 | +0.000 |

Runtime / fingerprint: cand `unswbc 1.2.3
installed the replay viewer into /usr/local/bin/code` `73f60fe2664c` panel `39961c55d0e6`; parent `unswbc 1.2.3` `d192d721c406` panel `39961c55d0e6`.

