# bokuto-17-atlas vs bokuto-13-cull — seeds 1

**Gate letter: NO LETTER (gen only, diagnostic)**

Intervals: cluster bootstrap over map × opponent (D-052 §C; both seats and all seeds together), 1,000 resamples, seed 7, linear 5th–95th percentile; the directional key (map × opp × seat) is printed as a sensitivity. Win, queen and conversion in percentage points; economy and material as normalised units ×100.

## gen

Paired fixtures 464 (cand expected 464, missing cand 0, parent 0). Status COMPLETE.

| | cand | parent |
|---|---|---|
| W | 348 | 354 |
| L | 115 | 110 |
| D | 1 | 0 |
| win | 0.7511 | 0.7629 |
| reached | 122 | 117 |
| q_cond | 0.5574 | 0.4530 |
| q_joint | 0.1466 | 0.1142 |
| q_dec_W | 66 | 53 |
| q_dec_L | 4 | 1 |
| conv | 0.7910 | 0.8034 |
| pearls@50 | 43.1358 | 43.3276 |
| pearls@100 | 117.7522 | 116.7608 |
| pearls@150 | 190.1013 | 188.2672 |
| pearls@250 | 300.5302 | 302.6272 |
| units@100 | 28.7953 | 28.5194 |
| total@100 | 71.8621 | 71.3082 |

| Δ | point [90 %] |
|---|---|
| win | -1.19 [-3.88, +1.51] |
| econ | +2.49 [+0.76, +4.21] |
| econ_med | +2.25 [+0.71, +3.51] |
| units@100 | +0.80 [+0.00, +1.92] |
| total@100 | +1.19 [-0.77, +3.65] |
| q_joint | +3.23 [+0.86, +5.82] |
| q_cond | +10.44 [+3.16, +18.33] |
| conv | -1.24 [-9.49, +6.04] |
| death_wall_per1k | +0.06 [-0.07, +0.19] |

Clusters: 232 (map × opp), valid draws 1000. Directional sensitivity (464 clusters): win -1.19 [-3.88, +1.62], econ~ +2.25 [+0.70, +3.52], units@100 +0.80 [+0.00, +1.82], total@100 +1.19 [-0.75, +3.63].

Tier-2 deaths per 1k dragon-turns:

| cause | parent | cand | rel | flag |
|---|---|---|---|---|
| death_wall_per1k | 1.970 | 2.029 | +3.0% |  |
| death_self_per1k | 1.869 | 1.908 | +2.1% |  |
| death_ally_body_per1k | 1.193 | 1.171 | -1.8% |  |
| death_h2h_ally_per1k | 1.003 | 1.039 | +3.7% |  |
| death_invalid_per1k | 0.000 | 0.000 | — |  |

Per class:

| class | n | Δwin pp | Δecon ×100 | Δq_joint pp | Δwall/1k |
|---|---|---|---|---|---|
| gen | 464 | -1.19 | +2.49 | +3.23 | +0.059 |

Per map:

| map | class | n | cand W-L | Δwin pp | Δecon ×100 | queen alive@RL (c vs p) | Δwall/1k |
|---|---|---|---|---|---|---|---|
| m2tr/autarky_tr | gen | 16 | 16-0 | +0.00 | +2.42 | 6/7 vs 5/5 | -0.047 |
| m2tr/default_tr | gen | 16 | 12-4 | -18.75 | +9.11 | 3/7 vs 5/9 | -0.005 |
| m2tr/dilemma_tr | gen | 16 | 15-1 | +6.25 | +1.46 | 3/6 vs 2/5 | -0.795 |
| m2tr/trophy_tr | gen | 16 | 12-4 | +0.00 | +2.25 | 1/1 vs 1/1 | -0.013 |
| new/mc26_archipelago | gen | 16 | 13-3 | -6.25 | +1.69 | 0/0 vs 0/0 | +0.103 |
| new/mc26_crossroads | gen | 16 | 11-5 | +0.00 | +2.52 | 5/6 vs 2/6 | +0.084 |
| new/mc26_delayed_commons | gen | 16 | 11-5 | +12.50 | +11.59 | 0/0 vs 2/2 | +0.009 |
| new/mc26_equatorial_belt | gen | 16 | 9-7 | +0.00 | -8.70 | 0/0 vs 0/0 | -0.030 |
| new/mc26_far_harbors | gen | 16 | 9-7 | -31.25 | -0.12 | 6/11 vs 7/9 | -0.017 |
| new/mc26_nursery_bays | gen | 16 | 13-3 | +6.25 | +2.15 | 2/2 vs 1/1 | -0.010 |
| new/mc26_pinwheel | gen | 16 | 10-6 | +0.00 | +1.08 | 0/2 vs 0/1 | -0.027 |
| new/mc26_portal_quartet | gen | 16 | 13-3 | -6.25 | +0.98 | 2/7 vs 3/7 | -0.090 |
| new/mc26_pulse_farms | gen | 16 | 12-4 | -6.25 | -6.22 | 1/1 vs 1/1 | +0.100 |
| new/mc26_relay_depots | gen | 16 | 12-4 | +6.25 | -4.43 | 3/6 vs 2/8 | -0.060 |
| new/mc26_scattered_fleets | gen | 16 | 15-1 | -6.25 | -4.42 | 3/4 vs 0/1 | -0.041 |
| new/mc26_seam_market | gen | 16 | 6-10 | +6.25 | -6.52 | 5/6 vs 3/3 | -0.024 |
| new/mc26_spring_wells | gen | 16 | 7-9 | +0.00 | +15.14 | 1/2 vs 1/1 | +0.000 |
| new/md26_causeway_detour_s0 | gen | 16 | 10-6 | -12.50 | -3.95 | 1/3 vs 0/3 | -0.034 |
| new/md26_causeway_portal_s0 | gen | 16 | 14-2 | +0.00 | +5.67 | 0/0 vs 0/0 | -0.077 |
| new/md26_commons_shared_s0 | gen | 16 | 11-5 | +6.25 | +5.77 | 0/0 vs 0/0 | +0.179 |
| new/md26_commons_spread_s0 | gen | 16 | 13-3 | -6.25 | -1.37 | 0/3 vs 0/4 | -0.077 |
| new/md26_orchard_narrow_s0 | gen | 16 | 14-2 | +0.00 | +1.67 | 4/6 vs 3/5 | +0.125 |
| new/md26_orchard_wide_s0 | gen | 16 | 14-2 | +0.00 | -1.28 | 0/1 vs 1/3 | +0.275 |
| new/md26_promenade_ring_s0 | gen | 16 | 11-5 | +0.00 | -2.62 | 1/1 vs 1/1 | -0.044 |
| var/crossroads_tr | gen | 16 | 9-7 | +0.00 | +2.70 | 2/2 vs 2/2 | -0.044 |
| var/devil_tr | gen | 16 | 16-0 | +0.00 | +6.91 | 0/0 vs 0/0 | +2.831 |
| var/portals_tr | gen | 16 | 11-4 | +9.38 | +3.56 | 0/15 vs 1/16 | -0.768 |
| var/queen_of_spades_tr | gen | 16 | 13-3 | -6.25 | +1.79 | 6/7 vs 2/7 | -0.378 |
| var/trauma_tr | gen | 16 | 16-0 | +12.50 | +33.50 | 13/16 vs 8/16 | +0.577 |

Runtime / fingerprint: cand `unswbc 1.2.3` `caf30880252c` panel `eaf9b0209184`; parent `unswbc 1.2.3` `d192d721c406` panel `eaf9b0209184`.

