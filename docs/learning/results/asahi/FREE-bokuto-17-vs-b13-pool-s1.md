# bokuto-17-atlas vs bokuto-13-cull — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 228 | 241 |
| L | 44 | 31 |
| D | 0 | 0 |
| win | 0.8382 | 0.8860 |
| reached | 166 | 163 |
| q_cond | 0.4639 | 0.5767 |
| q_joint | 0.2831 | 0.3456 |
| q_dec_W | 74 | 92 |
| q_dec_L | 3 | 2 |
| conv | 0.8614 | 0.9325 |
| pearls@50 | 46.7978 | 42.0809 |
| pearls@100 | 140.5147 | 123.8382 |
| pearls@150 | 251.2757 | 219.0735 |
| pearls@250 | 473.3750 | 414.6985 |
| units@100 | 30.2941 | 28.6728 |
| total@100 | 74.2610 | 72.0368 |

| Δ | point [90 %] |
|---|---|
| win | -4.78 [-8.46, -1.08] |
| econ | +60.10 [+34.77, +87.72] |
| econ_med | +12.53 [+9.48, +15.70] |
| units@100 | +3.23 [+0.00, +7.73] |
| total@100 | +6.15 [+1.78, +9.80] |
| q_joint | -6.25 [-11.03, -1.47] |
| q_cond | -11.28 [-18.58, -4.39] |
| conv | -7.11 [-11.82, -2.54] |
| death_wall_per1k | -0.63 [-1.11, -0.17] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -4.78 [-8.46, -1.10], econ~ +12.53 [+9.99, +14.71], units@100 +3.23 [+0.00, +7.46], total@100 +6.15 [+1.96, +8.62].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 6.296 | 5.669 | -10.0% |  |
| death_self_per1k | 3.698 | 4.957 | +34.0% | **yes** |
| death_ally_body_per1k | 1.517 | 1.864 | +22.9% | **yes** |
| death_h2h_ally_per1k | 1.417 | 2.534 | +78.8% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -6.25 | +14.66 | -6.25 | +0.492 |
| B | 80 | -6.25 | +9.05 | -16.25 | +0.116 |
| C | 48 | +2.08 | +247.48 | +0.00 | -1.632 |
| D | 16 | -12.50 | +10.96 | +18.75 | +0.936 |
| E | 16 | +0.00 | +120.40 | +0.00 | -10.729 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -18.75 | +27.01 | 9/16 vs 11/16 | +0.561 |
| live/autarky | A | 16 | 11-5 | -18.75 | +7.51 | 3/9 vs 3/6 | +2.162 |
| live/default | A | 16 | 14-2 | +0.00 | +52.99 | 7/11 vs 9/11 | +0.232 |
| live/devil | A | 16 | 15-1 | -6.25 | +11.57 | 0/0 vs 1/1 | +0.632 |
| live/dilemma | C | 16 | 13-3 | -12.50 | -50.97 | 2/2 vs 4/4 | -2.746 |
| live/islands | B | 16 | 16-0 | +0.00 | +12.72 | 3/14 vs 5/13 | +0.102 |
| live/maze | B | 16 | 15-1 | +0.00 | +16.57 | 1/16 vs 2/16 | +0.945 |
| live/portals | E | 16 | 10-6 | +0.00 | +120.40 | 0/16 vs 0/15 | -10.729 |
| live/queen_of_spades | A | 16 | 13-3 | -18.75 | +39.22 | 0/0 vs 5/5 | +0.616 |
| live/schooltime | B | 16 | 16-0 | +0.00 | +6.48 | 15/16 vs 16/16 | +0.399 |
| live/slithery_fight | D | 16 | 13-3 | -12.50 | +10.96 | 11/16 vs 8/16 | +0.936 |
| live/stripes | A | 16 | 4-12 | +0.00 | -24.20 | 0/2 vs 0/0 | +0.450 |
| live/tower_defense | A | 16 | 16-0 | +6.25 | +3.46 | 1/3 vs 0/3 | -0.583 |
| live/trauma | C | 16 | 16-0 | +0.00 | +758.14 | 14/15 vs 15/15 | +1.530 |
| live/trophy | A | 16 | 13-3 | -6.25 | +12.10 | 0/1 vs 0/0 | -0.068 |
| live/unsw | B | 16 | 14-2 | -12.50 | -17.53 | 6/16 vs 13/16 | -1.426 |
| live/weakhold | C | 16 | 16-0 | +18.75 | +35.27 | 5/13 vs 2/10 | -3.679 |

Runtime / fingerprint: cand `unswbc 1.2.3` `caf30880252c` panel `39961c55d0e6`; parent `unswbc 1.2.3` `d192d721c406` panel `39961c55d0e6`.

