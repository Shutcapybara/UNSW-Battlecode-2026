# bokuto-17-atlas vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 228 | 226 |
| L | 44 | 46 |
| D | 0 | 0 |
| win | 0.8382 | 0.8309 |
| reached | 166 | 146 |
| q_cond | 0.4639 | 0.0000 |
| q_joint | 0.2831 | 0.0000 |
| q_dec_W | 74 | 0 |
| q_dec_L | 3 | 5 |
| conv | 0.8614 | 0.8082 |
| pearls@50 | 46.7978 | 42.3088 |
| pearls@100 | 140.5147 | 126.0441 |
| pearls@150 | 251.2757 | 215.8162 |
| pearls@250 | 473.3750 | 395.0735 |
| units@100 | 30.2941 | 28.4816 |
| total@100 | 74.2610 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +0.74 [-4.41, +5.88] |
| econ | +59.36 [+32.43, +88.67] |
| econ_med | +10.04 [+6.29, +13.35] |
| units@100 | +0.42 [-1.56, +5.00] |
| total@100 | +4.86 [+1.29, +10.31] |
| q_joint | +28.31 [+22.79, +33.82] |
| q_cond | +46.39 [+38.82, +53.60] |
| conv | +5.32 [-1.50, +12.71] |
| death_wall_per1k | -1.54 [-2.85, -0.35] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +0.74 [-4.04, +5.51], econ~ +10.04 [+7.05, +12.69], units@100 +0.42 [-1.56, +4.76], total@100 +4.86 [+1.39, +9.06].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.669 | -21.4% |  |
| death_self_per1k | 3.585 | 4.957 | +38.3% | **yes** |
| death_ally_body_per1k | 1.563 | 1.864 | +19.3% | **yes** |
| death_h2h_ally_per1k | 1.238 | 2.534 | +104.7% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -8.04 | +10.04 | +9.82 | +0.630 |
| B | 80 | +1.25 | +17.65 | +42.50 | +1.011 |
| C | 48 | +18.75 | +243.55 | +43.75 | -9.457 |
| D | 16 | +18.75 | +10.19 | +68.75 | +3.065 |
| E | 16 | -12.50 | +109.69 | +0.00 | -10.412 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -6.25 | +24.71 | 9/16 vs 0/16 | +1.103 |
| live/autarky | A | 16 | 11-5 | -31.25 | -6.84 | 3/9 vs 0/3 | +1.290 |
| live/default | A | 16 | 14-2 | +6.25 | +31.71 | 7/11 vs 0/5 | +0.144 |
| live/devil | A | 16 | 15-1 | +0.00 | +11.57 | 0/0 vs 0/0 | +0.424 |
| live/dilemma | C | 16 | 13-3 | -12.50 | -48.62 | 2/2 vs 0/2 | -2.258 |
| live/islands | B | 16 | 16-0 | +0.00 | +20.76 | 3/14 vs 0/12 | +0.482 |
| live/maze | B | 16 | 15-1 | +0.00 | +26.86 | 1/16 vs 0/15 | +1.491 |
| live/portals | E | 16 | 10-6 | -12.50 | +109.69 | 0/16 vs 0/14 | -10.412 |
| live/queen_of_spades | A | 16 | 13-3 | -18.75 | +37.15 | 0/0 vs 0/3 | +0.233 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +16.86 | 15/16 vs 0/16 | +1.231 |
| live/slithery_fight | D | 16 | 13-3 | +18.75 | +10.19 | 11/16 vs 0/16 | +3.065 |
| live/stripes | A | 16 | 4-12 | -6.25 | -10.55 | 0/2 vs 0/2 | +1.677 |
| live/tower_defense | A | 16 | 16-0 | +6.25 | +0.13 | 1/3 vs 0/3 | +0.547 |
| live/trauma | C | 16 | 16-0 | +18.75 | +821.83 | 14/15 vs 0/16 | +3.106 |
| live/trophy | A | 16 | 13-3 | -12.50 | +7.09 | 0/1 vs 0/0 | +0.094 |
| live/unsw | B | 16 | 14-2 | +0.00 | -0.93 | 6/16 vs 0/16 | +0.747 |
| live/weakhold | C | 16 | 16-0 | +50.00 | -42.56 | 5/13 vs 0/7 | -29.218 |

Runtime / fingerprint: cand `unswbc 1.2.3` `caf30880252c` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

