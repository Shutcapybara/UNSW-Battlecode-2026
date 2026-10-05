# bokuto-35-knownbeds vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 225 | 237 |
| L | 47 | 35 |
| D | 0 | 0 |
| win | 0.8272 | 0.8713 |
| reached | 172 | 171 |
| q_cond | 0.5058 | 0.4854 |
| q_joint | 0.3199 | 0.3051 |
| q_dec_W | 85 | 80 |
| q_dec_L | 4 | 2 |
| conv | 0.8547 | 0.8713 |
| pearls@50 | 45.7022 | 42.4485 |
| pearls@100 | 130.8382 | 123.4228 |
| pearls@150 | 227.7574 | 214.8824 |
| pearls@250 | 431.9816 | 406.7574 |
| units@100 | 29.4779 | 28.6324 |
| total@100 | 75.8566 | 72.7647 |

| Δ | point [90 %] |
|---|---|
| win | -4.41 [-8.09, -0.37] |
| econ | +51.94 [+24.83, +81.23] |
| econ_med | +6.00 [+2.43, +8.74] |
| units@100 | -0.79 [-3.59, +5.21] |
| total@100 | +5.57 [+2.07, +9.83] |
| q_joint | +1.47 [-3.68, +6.64] |
| q_cond | +2.04 [-5.54, +9.86] |
| conv | -1.67 [-6.94, +4.06] |
| death_wall_per1k | -0.90 [-1.30, -0.52] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -4.41 [-8.82, +0.00], econ~ +6.00 [+3.28, +8.51], units@100 -0.79 [-3.28, +3.73], total@100 +5.57 [+2.54, +9.19].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.579 | 4.677 | -16.2% |  |
| death_self_per1k | 4.816 | 4.623 | -4.0% |  |
| death_ally_body_per1k | 1.663 | 2.210 | +32.9% | **yes** |
| death_h2h_ally_per1k | 1.146 | 2.009 | +75.2% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -2.68 | +3.51 | +0.00 | -0.341 |
| B | 80 | -6.25 | +14.90 | +10.00 | +0.076 |
| C | 48 | -4.17 | +254.28 | -10.42 | -1.027 |
| D | 16 | +0.00 | +8.84 | +6.25 | +0.172 |
| E | 16 | -12.50 | +12.32 | +0.00 | -10.425 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 10-6 | -18.75 | +76.20 | 7/16 vs 5/16 | +1.750 |
| live/autarky | A | 16 | 14-2 | -6.25 | +15.95 | 5/9 vs 5/6 | +0.223 |
| live/default | A | 16 | 13-3 | +12.50 | +46.78 | 7/15 vs 6/11 | +0.098 |
| live/devil | A | 16 | 14-2 | -12.50 | -6.99 | 0/0 vs 0/0 | -1.437 |
| live/dilemma | C | 16 | 15-1 | +0.00 | -47.68 | 3/4 vs 7/8 | -2.412 |
| live/islands | B | 16 | 15-1 | -6.25 | +13.27 | 4/15 vs 3/10 | +0.078 |
| live/maze | B | 16 | 14-2 | -6.25 | -3.44 | 3/16 vs 1/16 | -0.466 |
| live/portals | E | 16 | 9-7 | -12.50 | +12.32 | 0/15 vs 0/16 | -10.425 |
| live/queen_of_spades | A | 16 | 13-3 | -12.50 | -24.35 | 4/5 vs 5/7 | -0.227 |
| live/schooltime | B | 16 | 16-0 | +0.00 | +12.57 | 15/15 vs 14/14 | +0.322 |
| live/slithery_fight | D | 16 | 15-1 | +0.00 | +8.84 | 10/16 vs 9/16 | +0.172 |
| live/stripes | A | 16 | 5-11 | +0.00 | -6.62 | 1/1 vs 1/2 | +0.346 |
| live/tower_defense | A | 16 | 14-2 | +6.25 | -7.11 | 2/3 vs 2/7 | -1.379 |
| live/trauma | C | 16 | 16-0 | +0.00 | +823.32 | 12/15 vs 15/15 | -0.696 |
| live/trophy | A | 16 | 15-1 | -6.25 | +6.89 | 0/0 vs 0/0 | -0.008 |
| live/unsw | B | 16 | 13-3 | +0.00 | -24.12 | 9/16 vs 7/16 | -1.304 |
| live/weakhold | C | 16 | 14-2 | -12.50 | -12.79 | 5/11 vs 3/11 | +0.028 |

Runtime / fingerprint: cand `unswbc 1.2.3` `71021e11586e` panel `39961c55d0e6`; parent `unswbc 1.2.3` `fa93106401b1` panel `39961c55d0e6`.

