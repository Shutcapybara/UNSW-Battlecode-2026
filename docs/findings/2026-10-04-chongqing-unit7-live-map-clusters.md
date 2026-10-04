# Chongqing unit 7 — map clusters on the live pool: structure says "same maps", behaviour says five classes

Claude analyst (Opus 5.5), S-1 store / replay lead. 4 Oct 2026, 08:20 UTC. Store 51,396 games (post-m2 ≈ 7,200; native decode
idle since 05:18Z; one VM batch at 1.45 s/game). Era `post-m2`, field = non-team-7 sides, ladder 05:17Z.

## 1. Structural signatures (Esquie's `tools/esquie/signature.py`, 23 features, average linkage) on `maps/live/`

Every swapped map clusters with its old version at k = 6 and k = 8 — the 2 Oct edits were local (spawn pockets and the
Schooltime cage, a handful of beds: Trophy bed_count 625 → 547, Schooltime spawn-bed supply 5.0 → 3.3, Default spawn supply
95 → 92; tile counts, kelp density, portal pairs unchanged). So Esquie's clusters carry over for the ten ladder maps. The
seven restored maps fall as: **Australia + Around UNSW** (4,096 tiles, wrap 0.9, few portals) form a new large-open-wrap
cluster; **Islands** joins Schooltime (large, 12 portal pairs, wrap); **Stripes and Tower Defense** join the open mega-cluster
with Devil/Trauma/Autarky/PD/Slithery; **Maze** (16 portal pairs, kelp 0.27) and **weakhold** (no portals, no beds near spawn:
`spawn_bed_supply` 0, kelp 0.25) are singles. The structural signature does *not* separate corridor from open maps at
k ≤ 8 (Devil and Trauma sit with Autarky), which is why it should not drive the queen column.

## 2. Behavioural classes (store, post-m2 field: RL share, queen survival/decided, deaths/1k and causes, pearls@50, units@100,
total/longest at end, transits@50; average linkage on z-scores)

| class | maps | RL share | field queen alive (RL) | queen-decided | total@end | signature |
|---|---|---:|---:|---:|---:|---|
| A — elimination / short | Devil, Trophy, Stripes, Tower Defense, QoS, Default, Autarky | 0.03–0.45 | 0.00–0.35 | 0.00–0.56 | 30–68 | h2h 0.4–0.85 of deaths; the queen rarely matters |
| B — long open round-limit | Australia, Around UNSW, Islands, Maze, Schooltime | 0.90–1.00 | 0.09–0.26 (Schooltime 0.88) | 0.18–0.47 | 122–230 | big economies (units@100 25–53), contact deaths |
| C — starved corridor round-limit | Trauma, weakhold, Prisoners Dilemma (4 and 10) | 0.23–0.94 | 0.28–0.64 | **0.47–0.86** | 17–66 | tiny economies, wall deaths 0.34–0.49 |
| D — Slithery Fight | — | 0.99 | 0.26 | 0.46 | 179 | the richest map (pearls@50 186) |
| E — Portals | — | 0.99 | 0.25 | 0.43 | 56 | transits 16.6 by r50, 42 deaths/1k, no head-ons |

The behavioural classes cut across the structural clusters: Devil and Trauma share a structure and sit in opposite classes
(elimination vs the most queen-decided map). **Recommendation:** keep Esquie's structural clusters for opening/navigation
mechanisms (the per-map r50 gaps of unit 6 group by them: the starved cluster Trauma/Maze/Around UNSW/Australia/Schooltime
is a *behavioural* B+C mix, while Autarky/Default's pure-transit gap is one structural cluster), and use the behavioural
class — in practice the **RL share** — to weight the queen column: class B+C+D+E (10 maps) is where the queen decides games,
class A (7 maps) is where it does not. `tools.analysis.features.run_panel.LIVE_MAPS_M2` can carry both labels.

## 3. Readings

- **Rome's cage-package dose screen** (H-SZ1/21/22, parent carthage-05, `LIVE_MAPS_M2`, seed 1, both seats, pool 272/dose):
  Schooltime queen alive@490 **0 → 11/16 → 13/16** at dose 1/3 — the cage column moved as expected (the field is 0.86); pool
  W-L 226-46 / 229-43 / 224-48 (flat within seed-1 noise); invalid deaths 0 → 8/1k (the child sacrifice — intended); **pearls
  @250 −7 / −11 at dose 1/3**: that is the E component (reserve unit slots) taxing production everywhere, as Shenzhen's
  simulator warned. Reading: HOLD, agree with Himeji H28-06; the C+D-only arm (E = 0) is the one to run, and the Schooltime
  column is the only one to read until then. Map set and parent are correct per D-043.
- **Shenzhen's corpse-economy retraction** (07:35): noted; the corrected result (top ten eat 35–67 % more bed pearls after
  r150; 31–42 % of our corpse pearls go to the enemy on Around UNSW/Islands) is consistent with class B's big late economies
  above — the late-game lever on the B maps is bed throughput plus corpse protection, not the opening.
- **Seoul on H-KZ12's contract** (C ≤ k vs C < k, doses): an analyst should freeze one definition before the arm; Kanazawa
  owns it. From the store side: our sealed deaths have reach5 ≤ 2 in 92 % and the top ten's in 92 % too (unit 6) — whichever
  cutoff is chosen, the endpoint should be wall deaths/1k on classes C/E and queen alive on Trauma/Portals/Maze/weakhold.

## 4. Store

51,396 games; post-m2 ≈ 7,200 of ~13,500 in scope; the native decode has not resumed since 05:18Z (queue ~6,300). VM batches
at 1.3–1.5 s/game, ~45 games each. No table refresh this unit (growth < 500 games).

Ledger: no weight moves. Proposal: D-037's per-map opening programme uses the structural clusters (Esquie, unchanged for the
ten + the four new assignments above); the queen gate uses the RL-share classes.
