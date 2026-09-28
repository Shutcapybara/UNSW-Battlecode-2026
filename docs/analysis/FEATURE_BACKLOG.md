# F1 feature backlog

Living list for the local feature lab (`tools/analysis/features/`). Who raised each idea: **U** = the user, **D** = the director's
F1 prompt, **C** = Claude (analysis session, 29 Sep). Status: `done` (in the registry), `next`, `idea`, `dropped` (with the reason).

| idea | raised | status | notes |
|---|---|---|---|
| Dragons over time at key rounds; cumulative dragons (births) | U | done | `units@c`, `births@c`, `peak_units`, `peak_units_round` |
| Pearls over time | U | done | `pearls@c`, `bed_pearls@c`; eat events with origin (bed / our corpse / their corpse), not length deltas |
| Splits, rolling-window splits | U | done | `splits_0_50 … splits_250_500`, per-phase `*_splits_per100dt`; `first_split`, `last_split` |
| Self kills | U | done | Split into `death_self` (own body), `death_ally_body`, `death_h2h_ally` and `death_suicide` (deliberate) |
| Our kills / their kills | U | done | Credit only for body hits (the owner of the body hit) and head-on collisions (h2h); `kills@c`, `kill_length`, `kill_length_ratio` |
| Longest and average length over time | U | done | `longest@c`, `mean_len` series |
| Length spread (stddev / entropy / Gini / CV) | U | done | `top1_share@c` (robust, and the one the win rule uses), `len_gini@c`, `len_cv` series; entropy not added (redundant with Gini at n ≤ 50) |
| Sonar volume, by compass direction | U | done | `rays_per_dt*`, `rays_{N,E,S,W}_share` over rays that left the head. V1 probe found that a ray aimed into the own neck is recorded in its refracted direction (`ray_refracted_share`) |
| Sonar toward / away from the team's centre of mass | U | done | Circular mean of the other allied heads; `rays_toward_com_share`, `rays_away_com_share`, `rays_side_com_share` |
| Distance explored at key times | U | done | `seen_share@c` (union of 7×7 views), `visited_share@c`, `seen50`, `seen90` |
| Space controlled | U | done | Terrain-BFS territory (walls and portals), bed-weighted territory, logistic expected bed share; every 5 rounds |
| Enclosed vs open dragons and deaths | U | done | reach5 = cells reachable in 5 steps with bodies blocked; `enclosed_share@c`, `enclosed_death_share`, open and enclosed death rates; hazard curve in the report |
| Derivative-derivatives (short / long moving-average momentum) | U | next | Planned as event reducers (round of momentum flip, largest drop; `max_drawdown_total` done) rather than per-round scalars |
| Expected pearl gain = time spent near beds weighted by density | U | done | `epg_tau{1,2,4}` = Σ rate·exp(−d/τ); `epg_conversion` = bed pearls / EPG; `density_ratio` |
| Split every table by win / loss / all × each map / all maps | U | done | `quantiles.csv`; report box plots |
| Phase changes (opening exploration → economy churn → crown race) | U | done | Three detectors: rule markers, exact changepoint (K = 2 and BIC), and a pooled left-to-right 3-state HMM (primary); per-phase rates |
| Validation that does not have to wait for live data | U | done | Ladder V0–V6; V0 identities, V1 probe bots, V2 seed ICC, V3 proximal targets live in the report |
| Material at fixed checkpoints and first lead | D | done | |
| Newborn deaths within 10 rounds per 100 births | D | done | |
| Corpse-pearl recovery | D | done | `corpse_recovered_share`, `corpse_lost_share` |
| Deaths within 2 steps of a portal | D | done | `portal_death_share` |
| Head-on deaths with initiative (who moved) | D | idea | The decoder has the mover; add `h2h_initiated_share` and the survival of the initiator |
| Revisits (dithering): steps onto a cell visited in the last 20 rounds | D | next | Needs per-dragon head paths (available in the frame) |
| Mean distance between allied heads; spread of heads | D | next | Cheap from snapshots |
| Portal transits per 100 dragon-turns and their outcomes | D | idea | Frame v5 has head positions; detect a non-adjacent head step |
| Sonar rate responds to state (correlation with local ally count / being behind) | D | idea | |
| Bed occupancy (adjacent to a bed with countdown < 5) | D | dropped | On maps where every tile is a bed (Colosseum-style Trophy) adjacency is meaningless; replaced by the rate-weighted `density_ratio` |
| Contested pearls (both heads within 3) and who got them | D | idea | |
| Role clustering of dragons (explorer / farmer / fighter) from per-dragon paths | C | next | `dragons.parquet` already has gyration, density ratio, contact share, rays per turn, sprint share, eats per 100 turns |
| Sonar leakage (share of our rays received by the enemy) | C | done | `ray_leak_share` |
| Lead dragon exposure (enemies near the crown) | C | idea | |
| Decisive round (after it the end-of-game ranking never changes) | C | idea | |
| Coverage-gap statistic for A2 (share of field games outside the zoo 5–95 range) | C | next | Runs once the corpus features exist; the extractor already runs unchanged on field replays |
| Four-state HMM (a separate "war" state) | C | next | The fitted "crown" state is high on contact as well as on concentration; test whether contact deserves its own state |
| First contact round | C | dropped as headline | Map-locked: the starting layout fixes it on most maps (flagged in the report) |
