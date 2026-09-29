# cx-b02-router (C1-B, lineage cx; built on anna-a02-chassis)

Route finding and bed assignment on the C++ chassis. Arm (c) of the C1-B ablation.
`cx-b02-router-noatlas` is the same source with `CX_ATLAS 0` (out-of-sample rule 2).

`router.hpp` (per dragon, per turn; all horizons and caps keyed on measured structure):
1. terrain 2-core peel (cached per step-table version): dead-end trees with depth and tree id;
2. arrival maps: own time-aware BFS (body/vacancy mask), enemy multi-source BFS (visible + recent
   heads), one BFS per nearby visible ally (nearest `ally_cap`);
3. bed value: pearls eaten before the enemy's earliest arrival over the horizon (clamp(sqrt(NC), 20, 60)),
   discounted, first ripening full weight, later ones `later_event_w`, observed respawn gaps,
   unseen beds at the share observed in play, plus a cluster share; dead-end trees only if the pearls
   inside pay the exit split;
4. greedy assignment over (me + visible allies) x candidate beds with spacing, pair swap for me,
   hysteresis on the previous target;
5. movement: chassis one-step simulation and room tiers decide; within a tier, patrol timing (arrive
   when the pearl spawns), de-convergence from allies' planned paths, dead-end depth, enemy proximity;
   a known-exit portal is an ordinary route step (landing needs >= 2 open sides, not in a tree);
6. splits pearl-gated (len >= 4, 2 + 2) when the child has a first target it reaches first; starters split
   at once; trapped dragons split so the child from the tail keeps len - 2.

Differences from cx-b01-router: `later_event_w` (a patrol never outvalues a pearl on the ground),
`split_open_rounds`, `target_hysteresis` + cluster best-cell targeting, observed first-sight pearl share,
blind-landing exit rule. See docs/findings/2026-09-30-cx-b01-router.md.
