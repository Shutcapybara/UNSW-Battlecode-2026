# bokuto-04-queen vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 226 | 226 |
| L | 46 | 46 |
| D | 0 | 0 |
| win | 0.8309 | 0.8309 |
| reached | 189 | 146 |
| q_cond | 0.2328 | 0.0000 |
| q_joint | 0.1618 | 0.0000 |
| q_dec_W | 42 | 0 |
| q_dec_L | 4 | 5 |
| conv | 0.8307 | 0.8082 |
| pearls@50 | 41.4816 | 42.3088 |
| pearls@100 | 116.6434 | 126.0441 |
| pearls@150 | 203.4963 | 215.8162 |
| pearls@250 | 397.3934 | 395.0735 |
| units@100 | 28.1507 | 28.4816 |
| total@100 | 71.0368 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +0.00 [-5.15, +4.78] |
| econ | -5.73 [-9.24, -2.11] |
| econ_med | -6.29 [-9.47, -2.69] |
| units@100 | -1.89 [-5.71, -1.56] |
| total@100 | +0.00 [-3.28, +0.00] |
| q_joint | +16.18 [+11.40, +20.96] |
| q_cond | +23.28 [+16.84, +29.32] |
| conv | +2.25 [-5.12, +9.70] |
| death_wall_per1k | -1.37 [-2.55, -0.35] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +0.00 [-4.41, +4.78], econ~ -6.29 [-8.75, -3.13], units@100 -1.89 [-4.65, -1.56], total@100 +0.00 [-2.41, +0.00].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.848 | -18.9% |  |
| death_self_per1k | 3.585 | 3.840 | +7.1% |  |
| death_ally_body_per1k | 1.563 | 1.503 | -3.8% |  |
| death_h2h_ally_per1k | 1.238 | 1.355 | +9.5% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -6.25 | -3.19 | +3.57 | +0.097 |
| B | 80 | +0.00 | +2.91 | +30.00 | +0.520 |
| C | 48 | +12.50 | -22.04 | +29.17 | -9.140 |
| D | 16 | +12.50 | -3.37 | +12.50 | +1.380 |
| E | 16 | -6.25 | -20.21 | +0.00 | -0.450 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 15-1 | +6.25 | -3.42 | 3/16 vs 0/16 | +0.262 |
| live/autarky | A | 16 | 14-2 | -12.50 | -21.84 | 3/14 vs 0/3 | -2.587 |
| live/default | A | 16 | 11-5 | -12.50 | -27.27 | 0/14 vs 0/5 | +0.131 |
| live/devil | A | 16 | 16-0 | +6.25 | +13.06 | 0/1 vs 0/0 | -0.362 |
| live/dilemma | C | 16 | 13-3 | -12.50 | -11.70 | 4/9 vs 0/2 | -0.801 |
| live/islands | B | 16 | 15-1 | -6.25 | -3.97 | 2/16 vs 0/12 | +0.062 |
| live/maze | B | 16 | 16-0 | +6.25 | +3.70 | 3/16 vs 0/15 | -0.167 |
| live/portals | E | 16 | 11-5 | -6.25 | -20.21 | 0/16 vs 0/14 | -0.450 |
| live/queen_of_spades | A | 16 | 12-4 | -25.00 | -9.48 | 1/7 vs 0/3 | -0.597 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +4.45 | 16/16 vs 0/16 | +0.813 |
| live/slithery_fight | D | 16 | 12-4 | +12.50 | -3.37 | 2/16 vs 0/16 | +1.380 |
| live/stripes | A | 16 | 6-10 | +6.25 | +6.87 | 0/2 vs 0/2 | +2.216 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | +1.88 | 0/3 vs 0/3 | +1.170 |
| live/trauma | C | 16 | 15-1 | +12.50 | -6.14 | 10/16 vs 0/16 | +0.262 |
| live/trophy | A | 16 | 14-2 | -6.25 | +14.45 | 0/2 vs 0/0 | +0.710 |
| live/unsw | B | 16 | 11-5 | -18.75 | +13.81 | 0/16 vs 0/16 | +1.628 |
| live/weakhold | C | 16 | 14-2 | +37.50 | -48.29 | 0/9 vs 0/7 | -26.881 |

Runtime / fingerprint: cand `unswbc 1.2.3` `ff68a7093aa3` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

