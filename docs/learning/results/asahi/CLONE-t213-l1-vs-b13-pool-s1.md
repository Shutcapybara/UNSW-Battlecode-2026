# kageyama-02-p1-hb1-t213 vs bokuto-13-cull — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 192 | 241 |
| L | 80 | 31 |
| D | 0 | 0 |
| win | 0.7059 | 0.8860 |
| reached | 161 | 163 |
| q_cond | 0.0124 | 0.5767 |
| q_joint | 0.0074 | 0.3456 |
| q_dec_W | 2 | 92 |
| q_dec_L | 11 | 2 |
| conv | 0.6894 | 0.9325 |
| pearls@50 | 34.0368 | 42.0809 |
| pearls@100 | 104.7610 | 123.8382 |
| pearls@150 | 188.6838 | 219.0735 |
| pearls@250 | 368.6471 | 414.6985 |
| units@100 | 25.9743 | 28.6728 |
| total@100 | 64.9007 | 72.0368 |

| Δ | point [90 %] |
|---|---|
| win | -18.01 [-22.79, -12.87] |
| econ | +5.32 [-6.19, +18.39] |
| econ_med | -10.45 [-13.63, -7.74] |
| units@100 | -3.51 [-6.86, +0.00] |
| total@100 | -5.39 [-8.38, -0.78] |
| q_joint | -33.82 [-39.71, -27.57] |
| q_cond | -56.43 [-64.56, -47.69] |
| conv | -24.31 [-30.79, -18.22] |
| death_wall_per1k | -0.63 [-0.97, -0.32] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -18.01 [-22.79, -12.87], econ~ -10.45 [-13.36, -7.97], units@100 -3.51 [-6.83, +0.00], total@100 -5.39 [-8.18, -1.97].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 6.296 | 5.664 | -10.0% |  |
| death_self_per1k | 3.698 | 3.599 | -2.7% |  |
| death_ally_body_per1k | 1.517 | 1.624 | +7.1% |  |
| death_h2h_ally_per1k | 1.417 | 1.111 | -21.6% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -13.39 | -2.81 | -15.18 | +0.079 |
| B | 80 | -20.00 | -18.75 | -58.75 | -1.034 |
| C | 48 | -29.17 | +72.47 | -43.75 | +0.458 |
| D | 16 | -18.75 | -22.11 | -43.75 | -2.907 |
| E | 16 | -6.25 | +8.61 | +0.00 | -4.597 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -18.75 | -15.14 | 0/16 vs 11/16 | -0.606 |
| live/autarky | A | 16 | 14-2 | +0.00 | +1.18 | 0/6 vs 3/6 | +2.011 |
| live/default | A | 16 | 11-5 | -18.75 | -4.24 | 0/8 vs 9/11 | +0.258 |
| live/devil | A | 16 | 12-4 | -25.00 | -11.94 | 0/0 vs 1/1 | -0.047 |
| live/dilemma | C | 16 | 10-6 | -31.25 | -19.60 | 0/6 vs 4/4 | +0.421 |
| live/islands | B | 16 | 13-3 | -18.75 | -15.54 | 0/13 vs 5/13 | -0.078 |
| live/maze | B | 16 | 13-3 | -12.50 | -23.60 | 0/16 vs 2/16 | -1.286 |
| live/portals | E | 16 | 9-7 | -6.25 | +8.61 | 0/14 vs 0/15 | -4.597 |
| live/queen_of_spades | A | 16 | 11-5 | -31.25 | -5.88 | 0/5 vs 5/5 | +1.059 |
| live/schooltime | B | 16 | 13-3 | -18.75 | -22.60 | 0/15 vs 16/16 | -0.878 |
| live/slithery_fight | D | 16 | 12-4 | -18.75 | -22.11 | 1/15 vs 8/16 | -2.907 |
| live/stripes | A | 16 | 7-9 | +18.75 | +28.94 | 0/0 vs 0/0 | -0.984 |
| live/tower_defense | A | 16 | 12-4 | -18.75 | -14.35 | 1/5 vs 0/3 | -1.354 |
| live/trauma | C | 16 | 12-4 | -25.00 | +309.37 | 0/15 vs 15/15 | +0.329 |
| live/trophy | A | 16 | 11-5 | -18.75 | -13.36 | 0/0 vs 0/0 | -0.391 |
| live/unsw | B | 16 | 11-5 | -31.25 | -16.87 | 0/16 vs 13/16 | -2.322 |
| live/weakhold | C | 16 | 8-8 | -31.25 | -72.37 | 0/11 vs 2/10 | +0.625 |

Runtime / fingerprint: cand `unswbc 1.2.3` `db2531c5b17b` panel `39961c55d0e6`; parent `unswbc 1.2.3` `d192d721c406` panel `39961c55d0e6`.

