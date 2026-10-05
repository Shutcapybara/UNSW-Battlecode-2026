# bokuto-27-exitsplit vs bokuto-18-queenfeed — seeds 1

**Gate letter: NO LETTER (qk2 only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## qk2

Paired fixtures 68 (cand expected 68, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 26 | 30 |
| L | 42 | 38 |
| D | 0 | 0 |
| win | 0.3824 | 0.4412 |
| reached | 52 | 48 |
| q_cond | 0.3269 | 0.3542 |
| q_joint | 0.2500 | 0.2500 |
| q_dec_W | 9 | 9 |
| q_dec_L | 19 | 14 |
| conv | 0.4231 | 0.4583 |
| pearls@50 | 41.6471 | 38.9412 |
| pearls@100 | 113.8382 | 106.6324 |
| pearls@150 | 197.0294 | 186.1765 |
| pearls@250 | 384.4265 | 370.7941 |
| units@100 | 24.4118 | 24.3235 |
| total@100 | 60.4412 | 59.1765 |

| Δ | point [90 %] |
|---|---|
| win | -5.88 [-14.71, +1.47] |
| econ | +7.34 [+3.80, +11.33] |
| econ_med | +3.76 [+1.29, +7.00] |
| units@100 | +0.00 [-3.23, +0.00] |
| total@100 | +0.00 [-2.60, +2.82] |
| q_joint | +0.00 [-5.88, +5.88] |
| q_cond | -2.72 [-10.70, +5.77] |
| conv | -3.53 [-16.01, +8.70] |
| death_wall_per1k | +0.04 [-0.17, +0.23] |

Clusters: 34 (map × opp), valid draws 1000. Directional sensitivity (68 clusters): win -5.88 [-17.65, +5.88], econ~ +3.76 [+1.30, +7.08], units@100 +0.00 [-3.28, +1.45], total@100 +0.00 [-3.40, +2.50].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 5.361 | 5.399 | +0.7% |  |
| death_self_per1k | 3.676 | 3.823 | +4.0% |  |
| death_ally_body_per1k | 1.225 | 1.245 | +1.7% |  |
| death_h2h_ally_per1k | 1.243 | 1.309 | +5.3% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 28 | +7.14 | +3.07 | +7.14 | -0.211 |
| B | 20 | -10.00 | +1.77 | +5.00 | +0.072 |
| C | 12 | -16.67 | +25.46 | -16.67 | +0.304 |
| D | 4 | -50.00 | +8.41 | -25.00 | -0.314 |
| E | 4 | +0.00 | +9.66 | +0.00 | +1.154 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 4 | 1-3 | +0.00 | +0.00 | 0/4 vs 0/4 | +0.058 |
| live/autarky | A | 4 | 4-0 | +50.00 | +17.65 | 2/4 vs 0/4 | -2.037 |
| live/default | A | 4 | 0-4 | +0.00 | +0.00 | 2/4 vs 2/4 | +0.000 |
| live/devil | A | 4 | 0-4 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/dilemma | C | 4 | 0-4 | -50.00 | -3.13 | 0/4 vs 2/4 | -0.492 |
| live/islands | B | 4 | 2-2 | +0.00 | -0.77 | 1/4 vs 1/4 | +0.045 |
| live/maze | B | 4 | 2-2 | +25.00 | +2.27 | 0/4 vs 0/4 | -0.403 |
| live/portals | E | 4 | 4-0 | +0.00 | +9.66 | 2/4 vs 2/4 | +1.154 |
| live/queen_of_spades | A | 4 | 0-4 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |
| live/schooltime | B | 4 | 0-4 | -50.00 | +1.38 | 4/4 vs 4/4 | +0.279 |
| live/slithery_fight | D | 4 | 1-3 | -50.00 | +8.41 | 0/4 vs 1/4 | -0.314 |
| live/stripes | A | 4 | 2-2 | +0.00 | +3.84 | 0/0 vs 0/0 | +0.558 |
| live/tower_defense | A | 4 | 0-4 | +0.00 | +0.00 | 0/2 vs 0/2 | +0.000 |
| live/trauma | C | 4 | 2-2 | +0.00 | +27.12 | 4/4 vs 4/4 | +0.255 |
| live/trophy | A | 4 | 2-2 | +0.00 | +0.00 | 0/0 vs 0/0 | +0.000 |
| live/unsw | B | 4 | 2-2 | -25.00 | +5.96 | 2/4 vs 1/4 | +0.381 |
| live/weakhold | C | 4 | 4-0 | +0.00 | +52.38 | 0/4 vs 0/0 | +1.150 |

Runtime / fingerprint: cand `unswbc 1.2.3` `568c1a862535` panel `28a92b488185`; parent `unswbc 1.2.3` `fa93106401b1` panel `28a92b488185`.

