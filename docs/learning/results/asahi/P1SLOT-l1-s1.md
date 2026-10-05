# kageyama-01-p1-slot vs carthage-05-free-sprint — seeds 1

**Gate letter: screen-FAIL** — pool win -0.0699 [-0.1287, -0.0147] vs +0.00; gen win -0.0560 [-0.0948, -0.0151] vs -0.02; pool econ_med -0.0332 [-0.0600, -0.0013] vs -0.03; pool units@100 -0.0462 [-0.0718, -0.0156] vs -0.02; pool total@100 -0.0667 [-0.1037, -0.0426] vs -0.02; gen econ_med -0.0459 [-0.0743, -0.0148] vs -0.03; gen units@100 -0.1538 [-0.1795, -0.1250] vs -0.02; gen total@100 -0.1506 [-0.1852, -0.1097] vs -0.02; pool tier-2 up: ['death_ally_body_per1k']; gen tier-2 up: ['death_self_per1k', 'death_ally_body_per1k']

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 207 | 226 |
| L | 65 | 46 |
| D | 0 | 0 |
| win | 0.7610 | 0.8309 |
| reached | 165 | 146 |
| q_cond | 0.0182 | 0.0000 |
| q_joint | 0.0110 | 0.0000 |
| q_dec_W | 3 | 0 |
| q_dec_L | 6 | 5 |
| conv | 0.7515 | 0.8082 |
| pearls@50 | 37.2169 | 42.3088 |
| pearls@100 | 112.4743 | 126.0441 |
| pearls@150 | 202.7243 | 215.8162 |
| pearls@250 | 396.0956 | 395.0735 |
| units@100 | 26.1544 | 28.4816 |
| total@100 | 63.3456 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | -6.99 [-12.87, -1.47] |
| econ | +1.80 [-4.51, +7.96] |
| econ_med | -3.32 [-6.00, -0.13] |
| units@100 | -4.62 [-7.18, -1.56] |
| total@100 | -6.67 [-10.37, -4.26] |
| q_joint | +1.10 [+0.37, +2.21] |
| q_cond | +1.82 [+0.56, +3.64] |
| conv | -5.67 [-13.30, +1.44] |
| death_wall_per1k | -1.22 [-2.31, -0.22] |

Clusters: 136 (map × opp), valid draws 1000. Directional sensitivity (272 clusters): win -6.99 [-11.76, -1.84], econ~ -3.32 [-5.74, -0.83], units@100 -4.62 [-6.67, -2.13], total@100 -6.67 [-9.06, -4.39].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 5.989 | -17.0% |  |
| death_self_per1k | 3.585 | 3.800 | +6.0% |  |
| death_ally_body_per1k | 1.563 | 1.942 | +24.2% | **yes** |
| death_h2h_ally_per1k | 1.238 | 1.349 | +9.0% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | -10.71 | +4.03 | +0.89 | +0.869 |
| B | 80 | -10.00 | -6.79 | +1.25 | +0.184 |
| C | 48 | +0.00 | +1.09 | +2.08 | -8.362 |
| D | 16 | +0.00 | +5.94 | +0.00 | +2.046 |
| E | 16 | +6.25 | +27.04 | +0.00 | -4.769 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 10-6 | -25.00 | -5.64 | 1/16 vs 0/16 | -0.039 |
| live/autarky | A | 16 | 14-2 | -12.50 | -14.51 | 0/7 vs 0/3 | +1.319 |
| live/default | A | 16 | 13-3 | +0.00 | -0.15 | 0/10 vs 0/5 | +0.412 |
| live/devil | A | 16 | 4-12 | -68.75 | -44.31 | 0/1 vs 0/0 | -0.795 |
| live/dilemma | C | 16 | 11-5 | -25.00 | -26.69 | 0/4 vs 0/2 | -0.268 |
| live/islands | B | 16 | 14-2 | -12.50 | -4.85 | 0/14 vs 0/12 | +0.226 |
| live/maze | B | 16 | 16-0 | +6.25 | -10.65 | 0/15 vs 0/15 | +0.269 |
| live/portals | E | 16 | 13-3 | +6.25 | +27.04 | 0/16 vs 0/14 | -4.769 |
| live/queen_of_spades | A | 16 | 13-3 | -18.75 | -1.22 | 0/2 vs 0/3 | +1.346 |
| live/schooltime | B | 16 | 12-4 | -12.50 | -8.30 | 0/15 vs 0/16 | -0.090 |
| live/slithery_fight | D | 16 | 10-6 | +0.00 | +5.94 | 0/16 vs 0/16 | +2.046 |
| live/stripes | A | 16 | 13-3 | +50.00 | +98.18 | 0/1 vs 0/2 | +2.964 |
| live/tower_defense | A | 16 | 14-2 | -6.25 | +1.93 | 1/4 vs 0/3 | +0.799 |
| live/trauma | C | 16 | 12-4 | -6.25 | +86.11 | 1/16 vs 0/16 | +1.393 |
| live/trophy | A | 16 | 12-4 | -18.75 | -11.68 | 0/0 vs 0/0 | +0.039 |
| live/unsw | B | 16 | 13-3 | -6.25 | -4.52 | 0/16 vs 0/16 | +0.552 |
| live/weakhold | C | 16 | 13-3 | +31.25 | -56.14 | 0/12 vs 0/7 | -26.211 |

Runtime / fingerprint: cand `unswbc 1.2.3` `234a2fff48b6` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

## gen

Paired fixtures 464 (cand expected 464, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 315 | 341 |
| L | 149 | 123 |
| D | 0 | 0 |
| win | 0.6789 | 0.7349 |
| reached | 94 | 74 |
| q_cond | 0.0213 | 0.0405 |
| q_joint | 0.0043 | 0.0065 |
| q_dec_W | 2 | 3 |
| q_dec_L | 5 | 3 |
| conv | 0.7447 | 0.6486 |
| pearls@50 | 43.8039 | 44.0065 |
| pearls@100 | 116.3513 | 121.0711 |
| pearls@150 | 186.8405 | 189.7608 |
| pearls@250 | 289.9741 | 281.4375 |
| units@100 | 25.9849 | 29.1444 |
| total@100 | 62.9116 | 72.9591 |

| Δ | point [90 %] |
|---|---|
| win | -5.60 [-9.48, -1.51] |
| econ | +7.64 [+1.33, +14.29] |
| econ_med | -4.59 [-7.43, -1.48] |
| units@100 | -15.38 [-17.95, -12.50] |
| total@100 | -15.06 [-18.52, -10.97] |
| q_joint | -0.22 [-0.65, +0.00] |
| q_cond | -1.93 [-4.76, -0.08] |
| conv | +9.60 [-1.84, +21.25] |
| death_wall_per1k | +0.12 [-0.01, +0.27] |

Clusters: 232 (map × opp), valid draws 1000. Directional sensitivity (464 clusters): win -5.60 [-9.05, -1.51], econ~ -4.59 [-7.13, -1.69], units@100 -15.38 [-17.55, -12.19], total@100 -15.06 [-18.34, -10.90].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 1.942 | 2.064 | +6.3% |  |
| death_self_per1k | 1.803 | 2.247 | +24.6% | **yes** |
| death_ally_body_per1k | 1.039 | 1.783 | +71.6% | **yes** |
| death_h2h_ally_per1k | 0.750 | 0.817 | +9.0% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| gen | 464 | -5.60 | +7.64 | -0.22 | +0.122 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| m2tr/autarky_tr | gen | 16 | 14-2 | -12.50 | +4.99 | 0/6 vs 0/2 | +1.161 |
| m2tr/default_tr | gen | 16 | 13-3 | +18.75 | +14.04 | 0/4 vs 0/6 | +0.174 |
| m2tr/dilemma_tr | gen | 16 | 10-6 | -37.50 | -6.96 | 0/5 vs 1/4 | +0.927 |
| m2tr/trophy_tr | gen | 16 | 7-9 | -25.00 | -13.32 | 0/0 vs 0/0 | +0.423 |
| new/mc26_archipelago | gen | 16 | 12-4 | +0.00 | +0.32 | 0/0 vs 0/0 | -0.043 |
| new/mc26_crossroads | gen | 16 | 5-11 | -25.00 | -38.17 | 0/0 vs 0/3 | -0.115 |
| new/mc26_delayed_commons | gen | 16 | 14-2 | +25.00 | +14.64 | 0/0 vs 0/0 | +0.000 |
| new/mc26_equatorial_belt | gen | 16 | 9-7 | -6.25 | +50.58 | 0/0 vs 0/1 | +0.085 |
| new/mc26_far_harbors | gen | 16 | 10-6 | +12.50 | +27.39 | 0/5 vs 0/4 | +0.053 |
| new/mc26_nursery_bays | gen | 16 | 8-8 | -43.75 | -24.73 | 0/0 vs 0/1 | +0.005 |
| new/mc26_pinwheel | gen | 16 | 10-6 | -12.50 | -26.39 | 0/1 vs 0/1 | -0.018 |
| new/mc26_portal_quartet | gen | 16 | 14-2 | -12.50 | -0.30 | 0/11 vs 0/6 | -0.044 |
| new/mc26_pulse_farms | gen | 16 | 12-4 | +0.00 | -10.67 | 0/0 vs 0/0 | +0.268 |
| new/mc26_relay_depots | gen | 16 | 9-7 | -18.75 | -12.16 | 0/5 vs 0/4 | +0.013 |
| new/mc26_scattered_fleets | gen | 16 | 11-5 | -18.75 | -23.06 | 0/1 vs 0/0 | -0.038 |
| new/mc26_seam_market | gen | 16 | 3-13 | +12.50 | +217.17 | 0/0 vs 0/1 | -0.005 |
| new/mc26_spring_wells | gen | 16 | 8-8 | +12.50 | +13.12 | 0/1 vs 0/2 | +0.002 |
| new/md26_causeway_detour_s0 | gen | 16 | 11-5 | -6.25 | +9.84 | 0/0 vs 0/0 | -0.016 |
| new/md26_causeway_portal_s0 | gen | 16 | 10-6 | -25.00 | -20.42 | 0/1 vs 0/0 | +0.024 |
| new/md26_commons_shared_s0 | gen | 16 | 13-3 | -12.50 | -27.83 | 0/0 vs 0/0 | +0.049 |
| new/md26_commons_spread_s0 | gen | 16 | 12-4 | +0.00 | -10.51 | 0/6 vs 0/1 | -0.047 |
| new/md26_orchard_narrow_s0 | gen | 16 | 13-3 | -6.25 | +6.55 | 0/8 vs 0/3 | +1.481 |
| new/md26_orchard_wide_s0 | gen | 16 | 14-2 | +6.25 | +9.83 | 0/5 vs 0/2 | +0.700 |
| new/md26_promenade_ring_s0 | gen | 16 | 15-1 | +18.75 | +13.98 | 0/0 vs 0/0 | -0.003 |
| var/crossroads_tr | gen | 16 | 14-2 | +37.50 | +146.71 | 0/1 vs 0/1 | +0.175 |
| var/devil_tr | gen | 16 | 9-7 | -43.75 | -21.03 | 0/1 vs 0/0 | -0.200 |
| var/portals_tr | gen | 16 | 11-5 | -12.50 | +7.70 | 0/16 vs 0/15 | -1.670 |
| var/queen_of_spades_tr | gen | 16 | 14-2 | +25.00 | -4.23 | 0/2 vs 0/3 | +1.142 |
| var/trauma_tr | gen | 16 | 10-6 | -12.50 | -75.51 | 2/15 vs 2/14 | -0.947 |

Runtime / fingerprint: cand `unswbc 1.2.3` `234a2fff48b6` panel `eaf9b0209184`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `eaf9b0209184`.

