# bokuto-13-cull vs carthage-05-free-sprint — seeds 1

**Gate letter: NO LETTER (gen only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## gen

Paired fixtures 464 (cand expected 464, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 354 | 341 |
| L | 110 | 123 |
| D | 0 | 0 |
| win | 0.7629 | 0.7349 |
| reached | 117 | 74 |
| q_cond | 0.4530 | 0.0405 |
| q_joint | 0.1142 | 0.0065 |
| q_dec_W | 53 | 3 |
| q_dec_L | 1 | 3 |
| conv | 0.8034 | 0.6486 |
| pearls@50 | 43.3276 | 44.0065 |
| pearls@100 | 116.7608 | 121.0711 |
| pearls@150 | 188.2672 | 189.7608 |
| pearls@250 | 302.6272 | 281.4375 |
| units@100 | 28.5194 | 29.1444 |
| total@100 | 71.3082 | 72.9591 |

| Δ | point [90 %] |
|---|---|
| win | +2.80 [-0.22, +5.60] |
| econ | -0.80 [-2.98, +1.36] |
| econ_med | -3.04 [-4.88, -1.20] |
| units@100 | -1.89 [-4.17, +0.00] |
| total@100 | -2.00 [-4.03, +2.95] |
| q_joint | +10.78 [+8.41, +13.58] |
| q_cond | +41.25 [+32.74, +49.88] |
| conv | +15.48 [+4.65, +27.31] |
| death_wall_per1k | +0.03 [-0.08, +0.15] |

Clusters: 232 (map × opp), valid draws 1000. Directional sensitivity (464 clusters): win +2.80 [+0.00, +5.82], econ~ -3.04 [-4.86, -1.07], units@100 -1.89 [-3.85, +0.00], total@100 -2.00 [-3.51, +2.95].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 1.942 | 1.970 | +1.5% |  |
| death_self_per1k | 1.803 | 1.869 | +3.7% |  |
| death_ally_body_per1k | 1.039 | 1.193 | +14.8% | **yes** |
| death_h2h_ally_per1k | 0.750 | 1.003 | +33.8% | **yes** |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| gen | 464 | +2.80 | -0.80 | +10.78 | +0.028 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| m2tr/autarky_tr | gen | 16 | 16-0 | +0.00 | -13.63 | 5/5 vs 0/2 | -0.855 |
| m2tr/default_tr | gen | 16 | 15-1 | +31.25 | +1.28 | 5/9 vs 0/6 | -0.050 |
| m2tr/dilemma_tr | gen | 16 | 14-2 | -12.50 | +2.07 | 2/5 vs 1/4 | +1.059 |
| m2tr/trophy_tr | gen | 16 | 12-4 | +6.25 | +1.90 | 1/1 vs 0/0 | +0.042 |
| new/mc26_archipelago | gen | 16 | 14-2 | +12.50 | +7.69 | 0/0 vs 0/0 | -0.013 |
| new/mc26_crossroads | gen | 16 | 11-5 | +12.50 | +6.62 | 2/6 vs 0/3 | +0.105 |
| new/mc26_delayed_commons | gen | 16 | 9-7 | -6.25 | +2.42 | 2/2 vs 0/0 | +0.000 |
| new/mc26_equatorial_belt | gen | 16 | 9-7 | -6.25 | +29.75 | 0/0 vs 0/1 | +0.078 |
| new/mc26_far_harbors | gen | 16 | 14-2 | +37.50 | -5.36 | 7/9 vs 0/4 | +0.094 |
| new/mc26_nursery_bays | gen | 16 | 12-4 | -18.75 | -9.51 | 1/1 vs 0/1 | -0.031 |
| new/mc26_pinwheel | gen | 16 | 10-6 | -12.50 | -2.27 | 0/1 vs 0/1 | +0.181 |
| new/mc26_portal_quartet | gen | 16 | 14-2 | -12.50 | -5.49 | 3/7 vs 0/6 | +0.136 |
| new/mc26_pulse_farms | gen | 16 | 13-3 | +6.25 | -10.24 | 1/1 vs 0/0 | +0.178 |
| new/mc26_relay_depots | gen | 16 | 11-5 | -6.25 | +8.41 | 2/8 vs 0/4 | +0.146 |
| new/mc26_scattered_fleets | gen | 16 | 16-0 | +12.50 | +22.25 | 0/1 vs 0/0 | +0.100 |
| new/mc26_seam_market | gen | 16 | 5-11 | +25.00 | -8.13 | 3/3 vs 0/1 | +0.019 |
| new/mc26_spring_wells | gen | 16 | 7-9 | +6.25 | -5.45 | 1/1 vs 0/2 | -0.050 |
| new/md26_causeway_detour_s0 | gen | 16 | 12-4 | +0.00 | -1.11 | 0/3 vs 0/0 | +0.049 |
| new/md26_causeway_portal_s0 | gen | 16 | 14-2 | +0.00 | +1.43 | 0/0 vs 0/0 | +0.145 |
| new/md26_commons_shared_s0 | gen | 16 | 10-6 | -31.25 | -23.56 | 0/0 vs 0/0 | -0.148 |
| new/md26_commons_spread_s0 | gen | 16 | 14-2 | +12.50 | +1.61 | 0/4 vs 0/1 | +0.189 |
| new/md26_orchard_narrow_s0 | gen | 16 | 14-2 | +0.00 | -3.43 | 3/5 vs 0/3 | -0.096 |
| new/md26_orchard_wide_s0 | gen | 16 | 14-2 | +6.25 | +4.01 | 1/3 vs 0/2 | +0.112 |
| new/md26_promenade_ring_s0 | gen | 16 | 11-5 | -6.25 | -1.74 | 1/1 vs 0/0 | +0.068 |
| var/crossroads_tr | gen | 16 | 9-7 | +6.25 | +7.32 | 2/2 vs 0/1 | +0.211 |
| var/devil_tr | gen | 16 | 16-0 | +0.00 | +1.41 | 0/0 vs 0/0 | -0.109 |
| var/portals_tr | gen | 16 | 10-6 | -18.75 | -11.31 | 1/16 vs 0/15 | +0.749 |
| var/queen_of_spades_tr | gen | 16 | 14-2 | +25.00 | +1.41 | 2/7 vs 0/3 | -0.889 |
| var/trauma_tr | gen | 16 | 14-2 | +12.50 | -21.55 | 8/16 vs 2/14 | -0.596 |

Runtime / fingerprint: cand `unswbc 1.2.3` `d192d721c406` panel `eaf9b0209184`; parent `unswbc 1.2.3` `7df05a3f40b0` panel `eaf9b0209184`.

