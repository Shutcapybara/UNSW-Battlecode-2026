# asahi-01-cage-cd-e0 vs carthage-05-free-sprint — seeds 1

**Gate letter: screen-FAIL** — pool win +0.0221 [-0.0037, +0.0515] vs +0.00; pool tier-2 up: ['death_invalid_per1k']; gen tier-2 up: ['death_invalid_per1k']

Intervals: cluster bootstrap (map×opp×seat), 1,000 resamples, seed 7, 5th–95th percentile. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## pool

Paired fixtures 272 (cand expected 272, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 232 | 226 |
| L | 40 | 46 |
| D | 0 | 0 |
| win | 0.8529 | 0.8309 |
| reached | 149 | 146 |
| q_cond | 0.0403 | 0.0000 |
| q_joint | 0.0221 | 0.0000 |
| q_dec_W | 5 | 0 |
| q_dec_L | 4 | 5 |
| conv | 0.8523 | 0.8082 |
| pearls@50 | 43.8713 | 42.3088 |
| pearls@100 | 127.3309 | 126.0441 |
| pearls@150 | 213.8162 | 215.8162 |
| pearls@250 | 395.2941 | 395.0735 |
| units@100 | 28.7610 | 28.4816 |
| total@100 | 72.0257 | 71.3529 |

| Δ | point [90 %] |
|---|---|
| win | +2.21 [-0.37, +5.15] |
| econ | +0.65 [-0.01, +1.37] |
| econ_med | -0.10 [-0.53, +0.40] |
| units@100 | +0.00 [+0.00, +0.00] |
| total@100 | +0.00 [+0.00, +0.65] |
| q_joint | +2.21 [+0.74, +3.68] |
| q_cond | +4.03 [+1.35, +6.71] |
| conv | +4.41 [-0.09, +9.87] |
| death_wall_per1k | -5.77 [-6.88, -4.76] |

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 7.213 | 1.441 | -80.0% |  |
| death_self_per1k | 3.585 | 2.238 | -37.6% |  |
| death_ally_body_per1k | 1.563 | 0.764 | -51.1% |  |
| death_h2h_ally_per1k | 1.238 | 1.262 | +2.0% |  |
| death_invalid_per1k | 0.000 | 8.069 | — | **yes** |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| A | 112 | +0.00 | -0.26 | +0.00 | -2.526 |
| B | 80 | +6.25 | +3.55 | +6.25 | -2.528 |
| C | 48 | +0.00 | -0.97 | +0.00 | -14.831 |
| D | 16 | +18.75 | -2.14 | +6.25 | -5.474 |
| E | 16 | -12.50 | +0.12 | +0.00 | -17.833 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| live/australia | B | 16 | 16-0 | +12.50 | +2.20 | 1/16 vs 0/16 | -0.700 |
| live/autarky | A | 16 | 16-0 | +0.00 | -0.26 | 0/4 vs 0/3 | -8.969 |
| live/default | A | 16 | 13-3 | +0.00 | -0.12 | 0/5 vs 0/5 | -0.253 |
| live/devil | A | 16 | 15-1 | +0.00 | -3.60 | 0/0 vs 0/0 | -1.258 |
| live/dilemma | C | 16 | 15-1 | +0.00 | -3.38 | 0/3 vs 0/2 | -3.839 |
| live/islands | B | 16 | 16-0 | +0.00 | +0.00 | 0/13 vs 0/12 | -2.962 |
| live/maze | B | 16 | 16-0 | +6.25 | +0.38 | 0/16 vs 0/15 | -4.736 |
| live/portals | E | 16 | 10-6 | -12.50 | +0.12 | 0/13 vs 0/14 | -17.833 |
| live/queen_of_spades | A | 16 | 16-0 | +0.00 | -2.26 | 0/3 vs 0/3 | -2.314 |
| live/schooltime | B | 16 | 15-1 | +6.25 | +4.93 | 4/15 vs 0/16 | -2.099 |
| live/slithery_fight | D | 16 | 13-3 | +18.75 | -2.14 | 1/16 vs 0/16 | -5.474 |
| live/stripes | A | 16 | 5-11 | +0.00 | +1.98 | 0/3 vs 0/2 | -2.170 |
| live/tower_defense | A | 16 | 15-1 | +0.00 | +3.05 | 0/3 vs 0/3 | -2.500 |
| live/trauma | C | 16 | 12-4 | -6.25 | +0.50 | 0/16 vs 0/16 | -4.751 |
| live/trophy | A | 16 | 15-1 | +0.00 | -0.61 | 0/0 vs 0/0 | -0.220 |
| live/unsw | B | 16 | 15-1 | +6.25 | +10.25 | 0/16 vs 0/16 | -2.143 |
| live/weakhold | C | 16 | 9-7 | +6.25 | -0.02 | 0/7 vs 0/7 | -35.903 |

Runtime / fingerprint: cand `unswbc 1.2.3` `c0579163db45` panel `39961c55d0e6`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `39961c55d0e6`.

## gen

Paired fixtures 464 (cand expected 464, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 346 | 341 |
| L | 118 | 123 |
| D | 0 | 0 |
| win | 0.7457 | 0.7349 |
| reached | 67 | 74 |
| q_cond | 0.0000 | 0.0405 |
| q_joint | 0.0000 | 0.0065 |
| q_dec_W | 0 | 3 |
| q_dec_L | 4 | 3 |
| conv | 0.6567 | 0.6486 |
| pearls@50 | 44.4871 | 44.0065 |
| pearls@100 | 121.9483 | 121.0711 |
| pearls@150 | 190.2780 | 189.7608 |
| pearls@250 | 282.5625 | 281.4375 |
| units@100 | 29.6422 | 29.1444 |
| total@100 | 74.6358 | 72.9591 |

| Δ | point [90 %] |
|---|---|
| win | +1.08 [-0.65, +2.81] |
| econ | +0.62 [-0.57, +1.86] |
| econ_med | +0.25 [-0.10, +1.27] |
| units@100 | +0.00 [+0.00, +1.44] |
| total@100 | +0.68 [+0.00, +3.18] |
| q_joint | -0.65 [-1.29, +0.00] |
| q_cond | -4.05 [-8.00, +0.00] |
| conv | +0.81 [-8.39, +10.07] |
| death_wall_per1k | -1.20 [-1.40, -1.00] |

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 1.942 | 0.738 | -62.0% |  |
| death_self_per1k | 1.803 | 1.040 | -42.3% |  |
| death_ally_body_per1k | 1.039 | 0.727 | -30.0% |  |
| death_h2h_ally_per1k | 0.750 | 0.752 | +0.3% |  |
| death_invalid_per1k | 0.000 | 2.357 | — | **yes** |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| gen | 464 | +1.08 | +0.62 | -0.65 | -1.204 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| m2tr/autarky_tr | gen | 16 | 16-0 | +0.00 | +0.03 | 0/2 vs 0/2 | -4.801 |
| m2tr/default_tr | gen | 16 | 10-6 | +0.00 | +0.48 | 0/5 vs 0/6 | -0.265 |
| m2tr/dilemma_tr | gen | 16 | 16-0 | +0.00 | -1.07 | 0/3 vs 1/4 | -7.592 |
| m2tr/trophy_tr | gen | 16 | 11-5 | +0.00 | +0.12 | 0/0 vs 0/0 | -0.211 |
| new/mc26_archipelago | gen | 16 | 14-2 | +12.50 | +4.69 | 0/0 vs 0/0 | -0.038 |
| new/mc26_crossroads | gen | 16 | 10-6 | +6.25 | +7.24 | 0/1 vs 0/3 | -0.130 |
| new/mc26_delayed_commons | gen | 16 | 12-4 | +12.50 | +0.93 | 0/0 vs 0/0 | +0.000 |
| new/mc26_equatorial_belt | gen | 16 | 10-6 | +0.00 | -3.48 | 0/1 vs 0/1 | -0.037 |
| new/mc26_far_harbors | gen | 16 | 9-7 | +6.25 | +3.17 | 0/2 vs 0/4 | -0.024 |
| new/mc26_nursery_bays | gen | 16 | 15-1 | +0.00 | +0.70 | 0/1 vs 0/1 | -0.049 |
| new/mc26_pinwheel | gen | 16 | 12-4 | +0.00 | +0.46 | 0/1 vs 0/1 | +0.002 |
| new/mc26_portal_quartet | gen | 16 | 16-0 | +0.00 | -0.17 | 0/6 vs 0/6 | -0.051 |
| new/mc26_pulse_farms | gen | 16 | 12-4 | +0.00 | +3.34 | 0/0 vs 0/0 | -0.031 |
| new/mc26_relay_depots | gen | 16 | 12-4 | +0.00 | -0.57 | 0/4 vs 0/4 | -0.020 |
| new/mc26_scattered_fleets | gen | 16 | 14-2 | +0.00 | +1.88 | 0/1 vs 0/0 | -0.040 |
| new/mc26_seam_market | gen | 16 | 0-16 | -6.25 | -7.28 | 0/0 vs 0/1 | -0.005 |
| new/mc26_spring_wells | gen | 16 | 7-9 | +6.25 | +12.39 | 0/1 vs 0/2 | -0.050 |
| new/md26_causeway_detour_s0 | gen | 16 | 12-4 | +0.00 | +0.00 | 0/0 vs 0/0 | -0.000 |
| new/md26_causeway_portal_s0 | gen | 16 | 14-2 | +0.00 | +1.64 | 0/0 vs 0/0 | +0.015 |
| new/md26_commons_shared_s0 | gen | 16 | 15-1 | +0.00 | -9.72 | 0/0 vs 0/0 | -0.040 |
| new/md26_commons_spread_s0 | gen | 16 | 14-2 | +12.50 | +1.45 | 0/3 vs 0/1 | -0.117 |
| new/md26_orchard_narrow_s0 | gen | 16 | 14-2 | +0.00 | +0.68 | 0/2 vs 0/3 | -0.841 |
| new/md26_orchard_wide_s0 | gen | 16 | 14-2 | +6.25 | +1.73 | 0/0 vs 0/2 | -0.470 |
| new/md26_promenade_ring_s0 | gen | 16 | 12-4 | +0.00 | -0.52 | 0/0 vs 0/0 | -0.071 |
| var/crossroads_tr | gen | 16 | 8-8 | +0.00 | -0.47 | 0/1 vs 0/1 | -0.098 |
| var/devil_tr | gen | 16 | 16-0 | +0.00 | +0.08 | 0/0 vs 0/0 | -3.726 |
| var/portals_tr | gen | 16 | 7-9 | -37.50 | -0.15 | 0/16 vs 0/15 | -9.852 |
| var/queen_of_spades_tr | gen | 16 | 10-6 | +0.00 | +0.21 | 0/2 vs 0/3 | -2.519 |
| var/trauma_tr | gen | 16 | 14-2 | +12.50 | +0.09 | 0/15 vs 2/14 | -3.855 |

Runtime / fingerprint: cand `unswbc 1.2.3` `c0579163db45` panel `eaf9b0209184`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `eaf9b0209184`.

