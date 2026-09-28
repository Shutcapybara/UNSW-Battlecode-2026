# yeji-s05-young

**Lineage:** Yeji. **Parent:** `yeji-s04-compactprior`. **Status:** frozen. **In-sample only**: its edge comes from the public-map prior, which cannot fire on out-of-sample tournament maps.

Change from s04: a CPU degradation for newborns — for the first `young_turns` (2) turns after birth the target search uses `young_bfs_cap` 90 / `young_rbfs_cap` 120 (the second turn of a newborn warmed every cache and produced the s04 spikes).

Metered, Portals as B vs sinbad-v07-divecap (1.2.2 sandbox): **max 67.6M, p99 53.1M**, 11,231 turns, 0 exceeded (s04: max 79.8M). Schooltime runs without the prior (identical to s04's no-prior path).

Panel, **seed 2** (10 live maps × both sides × 8 refs; paired with the control on 144 fixtures): **0.597**; vs `ouroboros-v10-beacon` **+0.174 (32 better / 7 worse, p < 0.001)**; vs `yeji-s01p-production` (0.478 on seed 2) clearly ahead. Per map vs v10: devil +0.62, schooltime +0.25, default +0.19, QoS +0.19, dilemma +0.12, portals +0.12, trophy +0.06, autarky 0, slithery 0.

**Caveat.** The tournament plays maps outside the public pool. On them the prior does not fire and s05 = production arm + portal-exit memory + direct certificate rays + newborn CPU caps. Its tournament-relevant evaluation is the held-out panel under `yeji-s06-onlinebeds`.
