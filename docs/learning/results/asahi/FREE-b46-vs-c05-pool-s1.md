# bokuto-46-regions vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 235 | 226 |
| L | 35 | 46 |
| D | 2 | 0 |
| win | 0.8676 | 0.8309 |
| reached | 198 | 146 |
| q_cond | 0.5253 | 0.0000 |
| q_joint | 0.3824 | 0.0000 |
| q_dec_W | 99 | 0 |
| q_dec_L | 5 | 5 |
| conv | 0.8889 | 0.8082 |
| pearls@50 | 40.0000 | 42.3088 |
| pearls@100 | 112.7684 | 126.0441 |
| pearls@150 | 200.3787 | 215.8162 |
| pearls@250 | 396.3860 | 395.0735 |
| units@100 | 26.6691 | 28.4816 |
| total@100 | 68.5110 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +3.68 [-1.29, +8.64] |
| econ | -6.40 [-12.22, -1.00] |
| econ_med | -3.20 [-6.92, -0.79] |
| units@100 | -4.69 [-6.25, +0.00] |
| total@100 | +0.72 [-3.71, +4.00] |
| q_joint | +38.24 [+32.33, +44.12] |
| q_cond | +52.53 [+45.36, +60.00] |
| conv | +8.07 [+1.38, +15.14] |
| death_wall_per1k | -1.16 [-2.30, -0.15] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +3.68 [-1.10, +8.46], econ~ -3.20 [-5.64, -1.30], units@100 -4.69 [-6.25, -2.34], total@100 +0.72 [-2.86, +3.53].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 6.055 | -16.1% |  |
| death_self_per1k | 3.585 | 5.922 | +65.2% | **yes** |
| death_ally_body_per1k | 1.563 | 2.202 | +40.9% | **yes** |
| death_h2h_ally_per1k | 1.238 | 1.229 | -0.7% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -0.89 | +4.03 | +25.89 | +0.255 |
| B | 80 | -5.00 | -11.93 | +51.25 | +1.307 |
| C | 48 | +20.83 | -29.98 | +52.08 | -9.262 |
| D | 16 | +31.25 | +2.68 | +37.50 | +2.845 |
| E | 16 | +0.00 | +9.80 | +18.75 | -3.072 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 11-5 | -18.75 | -8.25 | 9/16 vs 0/16 | +1.242 |
| live/autarky | A | 16 | 14-2 | -12.50 | -5.04 | 8/14 vs 0/3 | -3.229 |
| live/default | A | 16 | 13-3 | +0.00 | -2.70 | 8/13 vs 0/5 | +0.022 |
| live/devil | A | 16 | 16-0 | +6.25 | +26.05 | 0/0 vs 0/0 | +2.068 |
| live/dilemma | C | 16 | 14-2 | -6.25 | -45.74 | 7/8 vs 0/2 | -2.712 |
| live/islands | B | 16 | 14-2 | -12.50 | +0.79 | 4/16 vs 0/12 | +2.423 |
| live/maze | B | 16 | 12-4 | -18.75 | +26.77 | 3/16 vs 0/15 | +3.140 |
| live/portals | E | 16 | 11-3 | +0.00 | +9.80 | 3/16 vs 0/14 | -3.072 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | +40.34 | 6/10 vs 0/3 | -0.085 |
| live/schooltime | B | 16 | 16-0 | +12.50 | -78.42 | 16/16 vs 0/16 | -0.268 |
| live/slithery_fight | D | 16 | 15-1 | +31.25 | +2.68 | 6/15 vs 0/16 | +2.845 |
| live/stripes | A | 16 | 5-11 | +0.00 | -56.36 | 1/2 vs 0/2 | +1.006 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | -1.99 | 4/10 vs 0/3 | +0.926 |
| live/trauma | C | 16 | 16-0 | +18.75 | +6.11 | 14/16 vs 0/16 | -0.201 |
| live/trophy | A | 16 | 15-1 | +0.00 | +27.91 | 2/8 vs 0/0 | +1.080 |
| live/unsw | B | 16 | 16-0 | +12.50 | -0.54 | 9/16 vs 0/16 | -0.001 |
| live/weakhold | C | 16 | 16-0 | +50.00 | -50.30 | 4/6 vs 0/7 | -24.872 |

Runtime / fingerprint: cand `unswbc 1.2.3` `2c2027132789` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

