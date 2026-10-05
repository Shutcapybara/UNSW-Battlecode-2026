# bokuto-35-knownbeds vs bokuto-13-cull — seeds 1

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
| reached | 135 | 117 |
| q_cond | 0.5481 | 0.4530 |
| q_joint | 0.1595 | 0.1142 |
| q_dec_W | 73 | 53 |
| q_dec_L | 1 | 1 |
| conv | 0.8074 | 0.8034 |
| pearls@50 | 42.1724 | 43.3276 |
| pearls@100 | 113.4116 | 116.7608 |
| pearls@150 | 180.8147 | 188.2672 |
| pearls@250 | 283.7091 | 302.6272 |
| units@100 | 27.8405 | 28.5194 |
| total@100 | 71.0690 | 71.3082 |

| Δ | point [90 %] |
|---|---|
| win | -2.37 [-5.82, +0.86] |
| econ | -3.23 [-5.56, -1.06] |
| econ_med | -1.57 [-3.43, -0.30] |
| units@100 | -2.57 [-4.00, +0.00] |
| total@100 | -0.18 [-2.55, +1.94] |
| q_joint | +4.53 [+1.29, +7.33] |
| q_cond | +9.52 [-0.59, +18.70] |
| conv | +0.40 [-9.13, +9.85] |
| death_wall_per1k | -0.14 [-0.24, -0.04] |

Clusters: 232 (map × opp), valid draws 1000. Directional sensitivity (464 clusters): win -2.37 [-5.60, +0.65], econ~ -1.57 [-3.36, -0.28], units@100 -2.57 [-3.81, +0.00], total@100 -0.18 [-2.25, +1.89].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 1.970 | 1.827 | -7.3% |  |
| death_self_per1k | 1.869 | 2.364 | +26.4% | **yes** |
| death_ally_body_per1k | 1.193 | 1.046 | -12.3% |  |
| death_h2h_ally_per1k | 1.003 | 0.652 | -35.0% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| gen | 464 | -2.37 | -3.23 | +4.53 | -0.144 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| m2tr/autarky_tr | gen | 16 | 16-0 | +0.00 | +9.57 | 4/4 vs 5/5 | -0.475 |
| m2tr/default_tr | gen | 16 | 14-2 | -6.25 | -6.67 | 7/12 vs 5/9 | -0.113 |
| m2tr/dilemma_tr | gen | 16 | 16-0 | +12.50 | -24.57 | 7/8 vs 2/5 | -2.330 |
| m2tr/trophy_tr | gen | 16 | 12-4 | +0.00 | +4.78 | 1/1 vs 1/1 | +0.238 |
| new/mc26_archipelago | gen | 16 | 14-2 | +0.00 | +4.57 | 0/0 vs 0/0 | -0.042 |
| new/mc26_crossroads | gen | 16 | 11-5 | +0.00 | -16.31 | 2/3 vs 2/6 | -0.095 |
| new/mc26_delayed_commons | gen | 16 | 9-7 | +0.00 | -12.04 | 2/2 vs 2/2 | +0.000 |
| new/mc26_equatorial_belt | gen | 16 | 9-7 | +0.00 | -12.10 | 0/1 vs 0/0 | -0.016 |
| new/mc26_far_harbors | gen | 16 | 10-6 | -25.00 | -1.25 | 4/11 vs 7/9 | -0.064 |
| new/mc26_nursery_bays | gen | 16 | 13-3 | +6.25 | +6.75 | 1/1 vs 1/1 | -0.024 |
| new/mc26_pinwheel | gen | 16 | 11-5 | +6.25 | -7.31 | 1/1 vs 0/1 | -0.138 |
| new/mc26_portal_quartet | gen | 16 | 13-3 | -6.25 | -8.23 | 0/7 vs 3/7 | -0.180 |
| new/mc26_pulse_farms | gen | 16 | 12-4 | -6.25 | -3.93 | 0/0 vs 1/1 | -0.106 |
| new/mc26_relay_depots | gen | 16 | 14-2 | +18.75 | -8.27 | 3/5 vs 2/8 | -0.136 |
| new/mc26_scattered_fleets | gen | 16 | 12-4 | -25.00 | -11.07 | 0/2 vs 0/1 | -0.123 |
| new/mc26_seam_market | gen | 16 | 3-13 | -12.50 | -1.28 | 3/5 vs 3/3 | -0.009 |
| new/mc26_spring_wells | gen | 16 | 9-7 | +12.50 | -6.33 | 3/3 vs 1/1 | +0.000 |
| new/md26_causeway_detour_s0 | gen | 16 | 11-5 | -6.25 | -0.26 | 2/5 vs 0/3 | -0.025 |
| new/md26_causeway_portal_s0 | gen | 16 | 14-2 | +0.00 | +3.71 | 0/0 vs 0/0 | -0.127 |
| new/md26_commons_shared_s0 | gen | 16 | 10-6 | +0.00 | -0.21 | 0/0 vs 0/0 | +0.187 |
| new/md26_commons_spread_s0 | gen | 16 | 10-6 | -25.00 | -1.90 | 0/3 vs 0/4 | -0.054 |
| new/md26_orchard_narrow_s0 | gen | 16 | 10-6 | -25.00 | -8.98 | 5/12 vs 3/5 | -0.241 |
| new/md26_orchard_wide_s0 | gen | 16 | 12-4 | -12.50 | -0.64 | 1/5 vs 1/3 | +0.022 |
| new/md26_promenade_ring_s0 | gen | 16 | 12-4 | +6.25 | -3.24 | 2/2 vs 1/1 | -0.114 |
| var/crossroads_tr | gen | 16 | 9-7 | +0.00 | +4.27 | 2/4 vs 2/2 | -0.246 |
| var/devil_tr | gen | 16 | 16-0 | +0.00 | +1.58 | 0/0 vs 0/0 | +0.979 |
| var/portals_tr | gen | 16 | 13-3 | +18.75 | -1.05 | 4/16 vs 1/16 | -0.821 |
| var/queen_of_spades_tr | gen | 16 | 12-4 | -12.50 | -23.32 | 5/7 vs 2/7 | -0.345 |
| var/trauma_tr | gen | 16 | 16-0 | +12.50 | +30.07 | 15/15 vs 8/16 | +0.231 |

Runtime / fingerprint: cand `unswbc 1.2.3` `71021e11586e` panel `eaf9b0209184`; parent `unswbc 1.2.3` `d192d721c406` panel `eaf9b0209184`.

