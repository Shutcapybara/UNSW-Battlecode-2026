# bokuto-13-cull vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 241 | 226 |
| L | 31 | 46 |
| D | 0 | 0 |
| win | 0.8860 | 0.8309 |
| reached | 163 | 146 |
| q_cond | 0.5767 | 0.0000 |
| q_joint | 0.3456 | 0.0000 |
| q_dec_W | 92 | 0 |
| q_dec_L | 2 | 5 |
| conv | 0.9325 | 0.8082 |
| pearls@50 | 42.0809 | 42.3088 |
| pearls@100 | 123.8382 | 126.0441 |
| pearls@150 | 219.0735 | 215.8162 |
| pearls@250 | 414.6985 | 395.0735 |
| units@100 | 28.6728 | 28.4816 |
| total@100 | 72.0368 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +5.51 [+2.19, +9.19] |
| econ | +2.21 [-2.20, +6.95] |
| econ_med | -0.60 [-3.62, +1.97] |
| units@100 | -1.56 [-2.22, +0.00] |
| total@100 | +0.00 [-0.93, +1.39] |
| q_joint | +34.56 [+28.31, +40.44] |
| q_cond | +57.67 [+49.32, +65.27] |
| conv | +12.43 [+6.99, +18.63] |
| death_wall_per1k | -0.92 [-2.03, +0.03] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +5.51 [+1.84, +9.56], econ~ -0.60 [-3.31, +1.82], units@100 -1.56 [-2.13, +0.00], total@100 +0.00 [-0.93, +1.29].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 6.296 | -12.7% |  |
| death_self_per1k | 3.585 | 3.698 | +3.2% |  |
| death_ally_body_per1k | 1.563 | 1.517 | -3.0% |  |
| death_h2h_ally_per1k | 1.238 | 1.417 | +14.5% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -1.79 | -3.10 | +16.07 | +0.138 |
| B | 80 | +7.50 | +8.88 | +58.75 | +0.894 |
| C | 48 | +16.67 | +5.85 | +43.75 | -7.825 |
| D | 16 | +31.25 | -0.60 | +50.00 | +2.129 |
| E | 16 | -12.50 | -2.11 | +0.00 | +0.317 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 16-0 | +12.50 | -1.46 | 11/16 vs 0/16 | +0.542 |
| live/autarky | A | 16 | 14-2 | -12.50 | -13.40 | 3/6 vs 0/3 | -0.872 |
| live/default | A | 16 | 14-2 | +6.25 | -14.00 | 9/11 vs 0/5 | -0.088 |
| live/devil | A | 16 | 16-0 | +6.25 | +0.11 | 1/1 vs 0/0 | -0.209 |
| live/dilemma | C | 16 | 15-1 | +0.00 | +1.33 | 4/4 vs 0/2 | +0.487 |
| live/islands | B | 16 | 16-0 | +0.00 | +7.10 | 5/13 vs 0/12 | +0.380 |
| live/maze | B | 16 | 15-1 | +0.00 | +8.51 | 2/16 vs 0/15 | +0.546 |
| live/portals | E | 16 | 10-6 | -12.50 | -2.11 | 0/15 vs 0/14 | +0.317 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | -2.44 | 5/5 vs 0/3 | -0.383 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +8.96 | 16/16 vs 0/16 | +0.832 |
| live/slithery_fight | D | 16 | 15-1 | +31.25 | -0.60 | 8/16 vs 0/16 | +2.129 |
| live/stripes | A | 16 | 4-12 | -6.25 | +15.50 | 0/0 vs 0/2 | +1.227 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | -2.93 | 0/3 vs 0/3 | +1.131 |
| live/trauma | C | 16 | 16-0 | +18.75 | +73.33 | 15/15 vs 0/16 | +1.575 |
| live/trophy | A | 16 | 14-2 | -6.25 | -4.57 | 0/0 vs 0/0 | +0.162 |
| live/unsw | B | 16 | 16-0 | +12.50 | +21.28 | 13/16 vs 0/16 | +2.172 |
| live/weakhold | C | 16 | 13-3 | +31.25 | -57.09 | 2/10 vs 0/7 | -25.538 |

Runtime / fingerprint: cand `unswbc 1.2.3` `d192d721c406` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

