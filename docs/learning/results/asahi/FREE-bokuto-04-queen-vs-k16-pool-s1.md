# bokuto-04-queen vs asahi-05-kz12-k16 — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 226 | 233 |
| L | 46 | 39 |
| D | 0 | 0 |
| win | 0.8309 | 0.8566 |
| reached | 189 | 148 |
| q_cond | 0.2328 | 0.0000 |
| q_joint | 0.1618 | 0.0000 |
| q_dec_W | 42 | 0 |
| q_dec_L | 4 | 5 |
| conv | 0.8307 | 0.8311 |
| pearls@50 | 41.4816 | 41.5588 |
| pearls@100 | 116.6434 | 125.1434 |
| pearls@150 | 203.4963 | 216.5515 |
| pearls@250 | 397.3934 | 400.2426 |
| units@100 | 28.1507 | 28.7500 |
| total@100 | 71.0368 | 72.1949 |

| Δ | point [90 %] |
|---|---|
| win | -2.57 [-7.35, +2.21] |
| econ | -5.66 [-9.04, -2.07] |
| econ_med | -5.96 [-9.16, -2.42] |
| units@100 | -1.56 [-4.76, -1.56] |
| total@100 | +0.00 [-3.33, +0.00] |
| q_joint | +16.18 [+11.40, +20.96] |
| q_cond | +23.28 [+16.84, +29.32] |
| conv | -0.04 [-6.75, +6.50] |
| death_wall_per1k | -0.28 [-0.63, +0.06] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -2.57 [-7.35, +2.21], econ~ -5.96 [-8.65, -2.80], units@100 -1.56 [-4.01, -1.56], total@100 +0.00 [-3.03, +0.00].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 6.129 | 5.848 | -4.6% |  |
| death_self_per1k | 3.620 | 3.840 | +6.1% |  |
| death_ally_body_per1k | 1.584 | 1.503 | -5.1% |  |
| death_h2h_ally_per1k | 1.226 | 1.355 | +10.6% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -6.25 | -3.62 | +3.57 | -0.006 |
| B | 80 | +0.00 | +3.03 | +30.00 | +0.472 |
| C | 48 | -2.08 | -20.79 | +29.17 | -2.594 |
| D | 16 | +6.25 | -3.34 | +12.50 | +1.311 |
| E | 16 | +0.00 | -20.28 | +0.00 | -0.639 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 15-1 | +6.25 | -3.46 | 3/16 vs 0/16 | +0.279 |
| live/autarky | A | 16 | 14-2 | -12.50 | -21.58 | 3/14 vs 0/4 | -2.486 |
| live/default | A | 16 | 11-5 | -12.50 | -27.27 | 0/14 vs 0/5 | +0.131 |
| live/devil | A | 16 | 16-0 | +6.25 | +11.97 | 0/1 vs 0/0 | -0.308 |
| live/dilemma | C | 16 | 13-3 | -12.50 | -12.93 | 4/9 vs 0/2 | -0.807 |
| live/islands | B | 16 | 15-1 | -6.25 | -4.04 | 2/16 vs 0/13 | +0.075 |
| live/maze | B | 16 | 16-0 | +6.25 | +4.37 | 3/16 vs 0/15 | -0.433 |
| live/portals | E | 16 | 11-5 | +0.00 | -20.28 | 0/16 vs 0/14 | -0.639 |
| live/queen_of_spades | A | 16 | 12-4 | -25.00 | -11.54 | 1/7 vs 0/3 | -0.410 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +4.45 | 16/16 vs 0/16 | +0.813 |
| live/slithery_fight | D | 16 | 12-4 | +6.25 | -3.34 | 2/16 vs 0/16 | +1.311 |
| live/stripes | A | 16 | 6-10 | +0.00 | +6.08 | 0/2 vs 0/1 | +2.093 |
| live/tower_defense | A | 16 | 15-1 | +6.25 | +2.56 | 0/3 vs 0/4 | +0.231 |
| live/trauma | C | 16 | 15-1 | +12.50 | -6.14 | 10/16 vs 0/16 | +0.301 |
| live/trophy | A | 16 | 14-2 | -6.25 | +14.45 | 0/2 vs 0/0 | +0.710 |
| live/unsw | B | 16 | 11-5 | -18.75 | +13.81 | 0/16 vs 0/16 | +1.628 |
| live/weakhold | C | 16 | 14-2 | -6.25 | -43.30 | 0/9 vs 0/7 | -7.275 |

Runtime / fingerprint: cand `unswbc 1.2.3` `ff68a7093aa3` panel `39961c55d0e6`; parent `unswbc 1.2.3` `43bd2d4fc7a8` panel `39961c55d0e6`.

