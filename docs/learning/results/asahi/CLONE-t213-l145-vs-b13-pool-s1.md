# asahi-15-t213-l145 vs bokuto-13-cull — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 191 | 241 |
| L | 80 | 31 |
| D | 1 | 0 |
| win | 0.7040 | 0.8860 |
| reached | 157 | 163 |
| q_cond | 0.0064 | 0.5767 |
| q_joint | 0.0037 | 0.3456 |
| q_dec_W | 1 | 92 |
| q_dec_L | 9 | 2 |
| conv | 0.7166 | 0.9325 |
| pearls@50 | 32.4706 | 42.0809 |
| pearls@100 | 101.4816 | 123.8382 |
| pearls@150 | 179.2794 | 219.0735 |
| pearls@250 | 347.0147 | 414.6985 |
| units@100 | 26.1618 | 28.6728 |
| total@100 | 64.3346 | 72.0368 |

| Δ | point [90 %] |
|---|---|
| win | -18.20 [-22.98, -13.05] |
| econ | -14.75 [-19.91, -9.77] |
| econ_med | -15.47 [-18.47, -11.95] |
| units@100 | -1.59 [-5.10, +0.00] |
| total@100 | -6.14 [-10.20, -3.11] |
| q_joint | -34.19 [-40.07, -27.94] |
| q_cond | -57.03 [-64.67, -48.71] |
| conv | -21.60 [-28.32, -15.55] |
| death_wall_per1k | -1.27 [-1.64, -0.90] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -18.20 [-23.16, -13.60], econ~ -15.47 [-18.19, -12.71], units@100 -1.59 [-5.10, +0.00], total@100 -6.14 [-9.27, -3.29].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 6.296 | 5.031 | -20.1% |  |
| death_self_per1k | 3.698 | 3.298 | -10.8% |  |
| death_ally_body_per1k | 1.517 | 1.451 | -4.3% |  |
| death_h2h_ally_per1k | 1.417 | 0.956 | -32.5% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -17.86 | -9.83 | -16.07 | -0.136 |
| B | 80 | -17.50 | -10.58 | -58.75 | -1.236 |
| C | 48 | -30.21 | -37.55 | -43.75 | -1.446 |
| D | 16 | -12.50 | -31.60 | -43.75 | -3.933 |
| E | 16 | +6.25 | +15.17 | +0.00 | -6.111 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 11-5 | -31.25 | +30.48 | 0/16 vs 11/16 | -0.516 |
| live/autarky | A | 16 | 14-2 | +0.00 | +2.02 | 0/5 vs 3/6 | +1.833 |
| live/default | A | 16 | 12-4 | -12.50 | -0.23 | 0/3 vs 9/11 | +0.444 |
| live/devil | A | 16 | 10-6 | -37.50 | -24.55 | 0/0 vs 1/1 | -1.925 |
| live/dilemma | C | 16 | 14-2 | -6.25 | -7.67 | 0/6 vs 4/4 | -0.968 |
| live/islands | B | 16 | 16-0 | +0.00 | -13.68 | 0/14 vs 5/13 | -0.424 |
| live/maze | B | 16 | 11-5 | -25.00 | -25.20 | 0/16 vs 2/16 | -1.833 |
| live/portals | E | 16 | 11-5 | +6.25 | +15.17 | 0/15 vs 0/15 | -6.111 |
| live/queen_of_spades | A | 16 | 13-3 | -18.75 | -7.16 | 0/3 vs 5/5 | +0.767 |
| live/schooltime | B | 16 | 13-3 | -18.75 | -15.60 | 0/14 vs 16/16 | -0.871 |
| live/slithery_fight | D | 16 | 13-3 | -12.50 | -31.60 | 1/16 vs 8/16 | -3.933 |
| live/stripes | A | 16 | 6-10 | +12.50 | +18.83 | 0/1 vs 0/0 | -0.197 |
| live/tower_defense | A | 16 | 9-7 | -37.50 | -40.46 | 0/6 vs 0/3 | -1.692 |
| live/trauma | C | 16 | 10-6 | -37.50 | -61.41 | 0/16 vs 15/15 | -1.995 |
| live/trophy | A | 16 | 9-7 | -31.25 | -17.26 | 0/0 vs 0/0 | -0.184 |
| live/unsw | B | 16 | 14-2 | -12.50 | -28.88 | 0/16 vs 13/16 | -2.536 |
| live/weakhold | C | 16 | 5-10 | -46.88 | -43.57 | 0/10 vs 2/10 | -1.376 |

Runtime / fingerprint: cand `unswbc 1.2.3` `8c4ec413e575` panel `39961c55d0e6`; parent `unswbc 1.2.3` `d192d721c406` panel `39961c55d0e6`.

