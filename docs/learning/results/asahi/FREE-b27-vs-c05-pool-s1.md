# bokuto-27-exitsplit vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (pool only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 242 | 226 |
| L | 30 | 46 |
| D | 0 | 0 |
| win | 0.8897 | 0.8309 |
| reached | 171 | 146 |
| q_cond | 0.4444 | 0.0000 |
| q_joint | 0.2794 | 0.0000 |
| q_dec_W | 73 | 0 |
| q_dec_L | 2 | 5 |
| conv | 0.9006 | 0.8082 |
| pearls@50 | 43.7574 | 42.3088 |
| pearls@100 | 124.0037 | 126.0441 |
| pearls@150 | 219.4301 | 215.8162 |
| pearls@250 | 412.8125 | 395.0735 |
| units@100 | 29.2206 | 28.4816 |
| total@100 | 74.6949 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +5.88 [+1.47, +9.93] |
| econ | +0.18 [-4.26, +4.49] |
| econ_med | -0.69 [-3.95, +1.48] |
| units@100 | +0.00 [-1.56, +4.37] |
| total@100 | +3.72 [+0.00, +6.81] |
| q_joint | +27.94 [+22.79, +33.82] |
| q_cond | +44.44 [+36.97, +52.60] |
| conv | +9.24 [+2.44, +16.23] |
| death_wall_per1k | -1.63 [-2.80, -0.64] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win +5.88 [+1.84, +9.93], econ~ -0.69 [-3.47, +1.07], units@100 +0.00 [-1.56, +4.20], total@100 +3.72 [+1.19, +6.23].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.587 | -22.5% |  |
| death_self_per1k | 3.585 | 4.673 | +30.3% | **yes** |
| death_ally_body_per1k | 1.563 | 1.649 | +5.5% |  |
| death_h2h_ally_per1k | 1.238 | 1.216 | -1.7% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -1.79 | -11.85 | +16.07 | -0.312 |
| B | 80 | +5.00 | +6.96 | +42.50 | +0.170 |
| C | 48 | +18.75 | +7.39 | +45.83 | -8.706 |
| D | 16 | +25.00 | -4.34 | +0.00 | -1.768 |
| E | 16 | +6.25 | +33.47 | +12.50 | +1.580 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 14-2 | +0.00 | -5.93 | 6/16 vs 0/16 | +0.086 |
| live/autarky | A | 16 | 16-0 | +0.00 | -9.76 | 3/3 vs 0/3 | -1.233 |
| live/default | A | 16 | 11-5 | -12.50 | -14.21 | 6/11 vs 0/5 | -0.026 |
| live/devil | A | 16 | 16-0 | +6.25 | +12.13 | 0/0 vs 0/0 | +0.727 |
| live/dilemma | C | 16 | 14-2 | -6.25 | -11.35 | 5/6 vs 0/2 | -0.410 |
| live/islands | B | 16 | 16-0 | +0.00 | +5.05 | 5/14 vs 0/12 | -0.973 |
| live/maze | B | 16 | 16-0 | +6.25 | +17.88 | 0/16 vs 0/15 | +1.629 |
| live/portals | E | 16 | 13-3 | +6.25 | +33.47 | 2/16 vs 0/14 | +1.580 |
| live/queen_of_spades | A | 16 | 15-1 | -6.25 | -12.90 | 5/7 vs 0/3 | -1.079 |
| live/schooltime | B | 16 | 16-0 | +12.50 | +4.15 | 15/15 vs 0/16 | -0.367 |
| live/slithery_fight | D | 16 | 14-2 | +25.00 | -4.34 | 0/16 vs 0/16 | -1.768 |
| live/stripes | A | 16 | 6-10 | +6.25 | -47.86 | 2/2 vs 0/2 | -0.173 |
| live/tower_defense | A | 16 | 13-3 | -12.50 | -14.19 | 2/7 vs 0/3 | -0.610 |
| live/trauma | C | 16 | 16-0 | +18.75 | +65.16 | 15/15 vs 0/16 | +1.606 |
| live/trophy | A | 16 | 16-0 | +6.25 | +3.83 | 0/0 vs 0/0 | +0.208 |
| live/unsw | B | 16 | 15-1 | +6.25 | +13.64 | 8/16 vs 0/16 | +0.475 |
| live/weakhold | C | 16 | 15-1 | +43.75 | -31.65 | 2/11 vs 0/7 | -27.314 |

Runtime / fingerprint: cand `unswbc 1.2.3
installed the replay viewer into /usr/local/bin/code` `568c1a862535` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

