# bokuto-47-precious vs bokuto-13-cull — seeds 1

**Gate letter: NO LETTER (gen only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## gen

Paired fixtures 464 (cand expected 464, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 343 | 354 |
| L | 121 | 110 |
| D | 0 | 0 |
| win | 0.7392 | 0.7629 |
| reached | 138 | 117 |
| q_cond | 0.5435 | 0.4530 |
| q_joint | 0.1616 | 0.1142 |
| q_dec_W | 74 | 53 |
| q_dec_L | 1 | 1 |
| conv | 0.8116 | 0.8034 |
| pearls@50 | 42.0927 | 43.3276 |
| pearls@100 | 113.3750 | 116.7608 |
| pearls@150 | 180.7478 | 188.2672 |
| pearls@250 | 284.0302 | 302.6272 |
| units@100 | 27.8793 | 28.5194 |
| total@100 | 71.2457 | 71.3082 |

| Δ | point [90 %] |
|---|---|
| win | -2.37 [-5.40, +0.65] |
| econ | -3.21 [-5.60, -1.00] |
| econ_med | -1.69 [-3.41, -0.37] |
| units@100 | -2.48 [-3.70, +0.00] |
| total@100 | +0.00 [-2.45, +2.02] |
| q_joint | +4.74 [+1.72, +7.76] |
| q_cond | +9.05 [-0.57, +18.19] |
| conv | +0.82 [-7.93, +8.38] |
| death_wall_per1k | -0.13 [-0.22, -0.04] |

Clusters: 232 (map × opp), valid draws 1000. Directional sensitivity (464 clusters): win -2.37 [-5.60, +0.65], econ~ -1.69 [-3.42, -0.35], units@100 -2.48 [-3.50, +0.00], total@100 +0.00 [-1.89, +2.01].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 1.970 | 1.837 | -6.8% |  |
| death_self_per1k | 1.869 | 2.445 | +30.8% | **yes** |
| death_ally_body_per1k | 1.193 | 1.057 | -11.4% |  |
| death_h2h_ally_per1k | 1.003 | 0.603 | -39.8% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| gen | 464 | -2.37 | -3.21 | +4.74 | -0.133 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| m2tr/autarky_tr | gen | 16 | 16-0 | +0.00 | +9.57 | 5/5 vs 5/5 | -0.463 |
| m2tr/default_tr | gen | 16 | 14-2 | -6.25 | -6.67 | 6/13 vs 5/9 | -0.081 |
| m2tr/dilemma_tr | gen | 16 | 15-1 | +6.25 | -25.13 | 6/7 vs 2/5 | -1.943 |
| m2tr/trophy_tr | gen | 16 | 12-4 | +0.00 | +7.83 | 1/1 vs 1/1 | -0.011 |
| new/mc26_archipelago | gen | 16 | 15-1 | +6.25 | +3.82 | 0/0 vs 0/0 | -0.035 |
| new/mc26_crossroads | gen | 16 | 11-5 | +0.00 | -16.32 | 6/6 vs 2/6 | -0.128 |
| new/mc26_delayed_commons | gen | 16 | 9-7 | +0.00 | -12.04 | 2/2 vs 2/2 | +0.000 |
| new/mc26_equatorial_belt | gen | 16 | 9-7 | +0.00 | -12.22 | 0/0 vs 0/0 | -0.019 |
| new/mc26_far_harbors | gen | 16 | 10-6 | -25.00 | -1.25 | 3/12 vs 7/9 | -0.061 |
| new/mc26_nursery_bays | gen | 16 | 13-3 | +6.25 | +6.75 | 1/1 vs 1/1 | -0.024 |
| new/mc26_pinwheel | gen | 16 | 11-5 | +6.25 | -7.33 | 1/2 vs 0/1 | -0.140 |
| new/mc26_portal_quartet | gen | 16 | 12-4 | -12.50 | -8.16 | 2/9 vs 3/7 | -0.173 |
| new/mc26_pulse_farms | gen | 16 | 12-4 | -6.25 | -3.93 | 0/0 vs 1/1 | -0.093 |
| new/mc26_relay_depots | gen | 16 | 13-3 | +12.50 | -8.27 | 4/6 vs 2/8 | -0.135 |
| new/mc26_scattered_fleets | gen | 16 | 12-4 | -25.00 | -11.07 | 0/3 vs 0/1 | -0.123 |
| new/mc26_seam_market | gen | 16 | 3-13 | -12.50 | -1.28 | 3/5 vs 3/3 | -0.009 |
| new/mc26_spring_wells | gen | 16 | 9-7 | +12.50 | -6.33 | 3/3 vs 1/1 | +0.000 |
| new/md26_causeway_detour_s0 | gen | 16 | 11-5 | -6.25 | -0.26 | 2/4 vs 0/3 | -0.024 |
| new/md26_causeway_portal_s0 | gen | 16 | 14-2 | +0.00 | +3.71 | 0/0 vs 0/0 | -0.136 |
| new/md26_commons_shared_s0 | gen | 16 | 10-6 | +0.00 | -0.21 | 0/0 vs 0/0 | +0.187 |
| new/md26_commons_spread_s0 | gen | 16 | 12-4 | -12.50 | -1.91 | 0/4 vs 0/4 | -0.057 |
| new/md26_orchard_narrow_s0 | gen | 16 | 9-7 | -31.25 | -9.66 | 2/10 vs 3/5 | -0.215 |
| new/md26_orchard_wide_s0 | gen | 16 | 13-3 | -6.25 | -1.06 | 0/1 vs 1/3 | -0.001 |
| new/md26_promenade_ring_s0 | gen | 16 | 12-4 | +6.25 | -3.24 | 2/2 vs 1/1 | -0.114 |
| var/crossroads_tr | gen | 16 | 9-7 | +0.00 | +4.27 | 3/5 vs 2/2 | -0.209 |
| var/devil_tr | gen | 16 | 16-0 | +0.00 | +1.52 | 0/0 vs 0/0 | +0.920 |
| var/portals_tr | gen | 16 | 13-3 | +18.75 | -0.96 | 2/15 vs 1/16 | -0.567 |
| var/queen_of_spades_tr | gen | 16 | 12-4 | -12.50 | -23.32 | 6/7 vs 2/7 | -0.351 |
| var/trauma_tr | gen | 16 | 16-0 | +12.50 | +30.07 | 15/15 vs 8/16 | +0.139 |

Runtime / fingerprint: cand `unswbc 1.2.3` `7322520f4e61` panel `eaf9b0209184`; parent `unswbc 1.2.3` `d192d721c406` panel `eaf9b0209184`.

