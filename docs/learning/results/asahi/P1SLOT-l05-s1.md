# kageyama-01-p1-slot-l05 vs carthage-05-free-sprint — seeds 1

**Gate letter: screen-FAIL** — pool win -0.1176 [-0.1728, -0.0586] vs +0.00; gen win -0.0647 [-0.1056, -0.0237] vs -0.02; pool econ_med -0.0839 [-0.1222, -0.0368] vs -0.03; pool units@100 -0.1127 [-0.1562, -0.0906] vs -0.02; pool total@100 -0.1097 [-0.1285, -0.0804] vs -0.02; gen econ_med -0.0554 [-0.0876, -0.0269] vs -0.03; gen units@100 -0.1725 [-0.2079, -0.1560] vs -0.02; gen total@100 -0.1852 [-0.2203, -0.1510] vs -0.02; pool tier-2 up: ['death_self_per1k', 'death_ally_body_per1k', 'death_h2h_ally_per1k']; gen tier-2 up: ['death_wall_per1k', 'death_self_per1k', 'death_ally_body_per1k', 'death_h2h_ally_per1k']

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 194 | 226 |
| L | 78 | 46 |
| D | 0 | 0 |
| win | 0.7132 | 0.8309 |
| reached | 167 | 146 |
| q_cond | 0.0180 | 0.0000 |
| q_joint | 0.0110 | 0.0000 |
| q_dec_W | 3 | 0 |
| q_dec_L | 6 | 5 |
| conv | 0.7246 | 0.8082 |
| pearls@50 | 37.1618 | 42.3088 |
| pearls@100 | 110.9412 | 126.0441 |
| pearls@150 | 199.0809 | 215.8162 |
| pearls@250 | 390.3051 | 395.0735 |
| units@100 | 24.5441 | 28.4816 |
| total@100 | 60.3419 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -11.76 [-17.28, -5.86] |
| econ | -3.84 [-9.97, +2.50] |
| econ_med | -8.39 [-12.22, -3.68] |
| units@100 | -11.27 [-15.62, -9.06] |
| total@100 | -10.97 [-12.85, -8.04] |
| q_joint | +1.10 [+0.00, +2.21] |
| q_cond | +1.80 [+0.00, +3.64] |
| conv | -8.37 [-16.09, -0.49] |
| death_wall_per1k | -0.62 [-1.80, +0.41] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -11.76 [-17.28, -6.25], econ~ -8.39 [-11.29, -4.03], units@100 -11.27 [-15.38, -9.09], total@100 -10.97 [-12.50, -8.04].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 6.594 | -8.6% |  |
| death_self_per1k | 3.585 | 3.999 | +11.6% | **yes** |
| death_ally_body_per1k | 1.563 | 1.968 | +25.9% | **yes** |
| death_h2h_ally_per1k | 1.238 | 1.507 | +21.7% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -16.96 | -0.43 | +0.89 | +1.179 |
| B | 80 | -13.75 | -13.42 | +2.50 | +0.436 |
| C | 48 | -8.33 | -14.53 | +0.00 | -8.195 |
| D | 16 | +6.25 | +17.05 | +0.00 | +4.724 |
| E | 16 | +6.25 | +31.46 | +0.00 | -1.101 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 13-3 | -6.25 | -18.13 | 0/16 vs 0/16 | +0.254 |
| live/autarky | A | 16 | 13-3 | -18.75 | -11.68 | 0/6 vs 0/3 | +2.232 |
| live/default | A | 16 | 10-6 | -18.75 | -13.01 | 0/8 vs 0/5 | +0.666 |
| live/devil | A | 16 | 6-10 | -56.25 | -40.12 | 0/1 vs 0/0 | -0.901 |
| live/dilemma | C | 16 | 9-7 | -37.50 | -19.99 | 0/4 vs 0/2 | +0.592 |
| live/islands | B | 16 | 12-4 | -25.00 | -12.45 | 0/13 vs 0/12 | +0.780 |
| live/maze | B | 16 | 13-3 | -12.50 | -15.40 | 1/15 vs 0/15 | -0.182 |
| live/portals | E | 16 | 13-3 | +6.25 | +31.46 | 0/16 vs 0/14 | -1.101 |
| live/queen_of_spades | A | 16 | 10-6 | -37.50 | -11.08 | 0/5 vs 0/3 | +1.567 |
| live/schooltime | B | 16 | 12-4 | -12.50 | -13.19 | 0/15 vs 0/16 | +0.579 |
| live/slithery_fight | D | 16 | 11-5 | +6.25 | +17.05 | 0/16 vs 0/16 | +4.724 |
| live/stripes | A | 16 | 12-4 | +43.75 | +95.33 | 0/0 vs 0/2 | +2.931 |
| live/tower_defense | A | 16 | 14-2 | -6.25 | -6.06 | 1/4 vs 0/3 | +1.486 |
| live/trauma | C | 16 | 12-4 | -6.25 | +48.08 | 0/16 vs 0/16 | +1.638 |
| live/trophy | A | 16 | 11-5 | -25.00 | -16.41 | 0/0 vs 0/0 | +0.271 |
| live/unsw | B | 16 | 12-4 | -12.50 | -7.94 | 1/16 vs 0/16 | +0.749 |
| live/weakhold | C | 16 | 11-5 | +18.75 | -71.69 | 0/16 vs 0/7 | -26.815 |

Runtime / fingerprint: cand `unswbc 1.2.3` `9c46f63c197d` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

## gen

Paired fixtures 464 (cand expected 464, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 311 | 341 |
| L | 153 | 123 |
| D | 0 | 0 |
| win | 0.6703 | 0.7349 |
| reached | 95 | 74 |
| q_cond | 0.0211 | 0.0405 |
| q_joint | 0.0043 | 0.0065 |
| q_dec_W | 0 | 3 |
| q_dec_L | 5 | 3 |
| conv | 0.6105 | 0.6486 |
| pearls@50 | 40.5862 | 44.0065 |
| pearls@100 | 114.5927 | 121.0711 |
| pearls@150 | 188.0647 | 189.7608 |
| pearls@250 | 298.8685 | 281.4375 |
| units@100 | 24.3168 | 29.1444 |
| total@100 | 58.3168 | 72.9591 |

| Δ | point [90 %] |
|---|---|
| win | -6.47 [-10.56, -2.37] |
| econ | +12.78 [+5.51, +20.54] |
| econ_med | -5.54 [-8.76, -2.69] |
| units@100 | -17.25 [-20.79, -15.60] |
| total@100 | -18.52 [-22.03, -15.10] |
| q_joint | -0.22 [-1.08, +0.65] |
| q_cond | -1.95 [-6.23, +2.45] |
| conv | -3.81 [-15.47, +8.23] |
| death_wall_per1k | +0.31 [+0.17, +0.47] |

Clusters: 232 (map × opp), valid draws 1000. Directional sensitivity (464 clusters): win -6.47 [-9.91, -2.58], econ~ -5.54 [-8.32, -3.20], units@100 -17.25 [-20.57, -15.52], total@100 -18.52 [-21.83, -15.65].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 1.942 | 2.257 | +16.2% | **yes** |
| death_self_per1k | 1.803 | 2.427 | +34.6% | **yes** |
| death_ally_body_per1k | 1.039 | 2.029 | +95.3% | **yes** |
| death_h2h_ally_per1k | 0.750 | 0.983 | +31.1% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| gen | 464 | -6.47 | +12.78 | -0.22 | +0.315 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| m2tr/autarky_tr | gen | 16 | 14-2 | -12.50 | -2.35 | 0/5 vs 0/2 | +1.399 |
| m2tr/default_tr | gen | 16 | 14-2 | +25.00 | +46.25 | 0/2 vs 0/6 | +0.346 |
| m2tr/dilemma_tr | gen | 16 | 7-9 | -56.25 | -13.45 | 2/5 vs 1/4 | +1.522 |
| m2tr/trophy_tr | gen | 16 | 9-7 | -12.50 | -6.85 | 0/0 vs 0/0 | +0.739 |
| new/mc26_archipelago | gen | 16 | 10-6 | -12.50 | -10.24 | 0/0 vs 0/0 | -0.076 |
| new/mc26_crossroads | gen | 16 | 13-3 | +25.00 | +38.39 | 0/1 vs 0/3 | +0.003 |
| new/mc26_delayed_commons | gen | 16 | 14-2 | +25.00 | +23.80 | 0/0 vs 0/0 | +0.026 |
| new/mc26_equatorial_belt | gen | 16 | 12-4 | +12.50 | +47.26 | 0/0 vs 0/1 | +0.211 |
| new/mc26_far_harbors | gen | 16 | 7-9 | -6.25 | +13.40 | 0/6 vs 0/4 | +0.026 |
| new/mc26_nursery_bays | gen | 16 | 14-2 | -6.25 | -9.58 | 0/1 vs 0/1 | +0.123 |
| new/mc26_pinwheel | gen | 16 | 11-5 | -6.25 | -8.80 | 0/0 vs 0/1 | +0.053 |
| new/mc26_portal_quartet | gen | 16 | 13-3 | -18.75 | +10.07 | 0/9 vs 0/6 | -0.032 |
| new/mc26_pulse_farms | gen | 16 | 13-3 | +6.25 | -7.05 | 0/0 vs 0/0 | +0.391 |
| new/mc26_relay_depots | gen | 16 | 8-8 | -25.00 | -32.41 | 0/4 vs 0/4 | +0.003 |
| new/mc26_scattered_fleets | gen | 16 | 14-2 | +0.00 | -22.35 | 0/1 vs 0/0 | +0.027 |
| new/mc26_seam_market | gen | 16 | 7-9 | +37.50 | +248.36 | 0/0 vs 0/1 | +0.011 |
| new/mc26_spring_wells | gen | 16 | 11-5 | +31.25 | +92.43 | 0/0 vs 0/2 | +0.021 |
| new/md26_causeway_detour_s0 | gen | 16 | 10-6 | -12.50 | -17.52 | 0/0 vs 0/0 | +0.003 |
| new/md26_causeway_portal_s0 | gen | 16 | 9-7 | -31.25 | -31.73 | 0/0 vs 0/0 | +0.012 |
| new/md26_commons_shared_s0 | gen | 16 | 5-11 | -62.50 | -44.08 | 0/0 vs 0/0 | +0.048 |
| new/md26_commons_spread_s0 | gen | 16 | 12-4 | +0.00 | -11.81 | 0/6 vs 0/1 | -0.099 |
| new/md26_orchard_narrow_s0 | gen | 16 | 13-3 | -6.25 | +9.21 | 0/9 vs 0/3 | +1.529 |
| new/md26_orchard_wide_s0 | gen | 16 | 12-4 | -6.25 | -1.28 | 0/5 vs 0/2 | +1.140 |
| new/md26_promenade_ring_s0 | gen | 16 | 14-2 | +12.50 | +5.83 | 0/0 vs 0/0 | -0.041 |
| var/crossroads_tr | gen | 16 | 10-6 | +12.50 | +143.61 | 0/1 vs 0/1 | -0.005 |
| var/devil_tr | gen | 16 | 8-8 | -50.00 | -15.53 | 0/1 vs 0/0 | +1.246 |
| var/portals_tr | gen | 16 | 11-5 | -12.50 | +3.58 | 0/15 vs 0/15 | +0.808 |
| var/queen_of_spades_tr | gen | 16 | 11-5 | +6.25 | +5.55 | 0/8 vs 0/3 | +1.513 |
| var/trauma_tr | gen | 16 | 5-11 | -43.75 | -82.22 | 0/16 vs 2/14 | -1.814 |

Runtime / fingerprint: cand `unswbc 1.2.3` `9c46f63c197d` panel `eaf9b0209184`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `eaf9b0209184`.

