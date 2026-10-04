# Chongqing unit 8 — opening gap per structural cluster; the field is still adopting the queen

Claude analyst (Opus 5.5), S-1 store / replay lead. 4 Oct 2026, 09:25 UTC. Store 51,396 games (post-m2 ≈ 7,200; no decode this
unit — the VM's growth is < 1 % per unit and the native job has not resumed). Era `post-m2`, ranked unless stated, ladder 05:17Z.
`r/chongqing` units 3–7 merged to main at e3838cc84 (the 2-hourly task skips any branch with a "changed in both" file, which
`tools/s1/build.py` now is; merged on explicit request, 0 conflict markers).

## 1. Adaptation clock (ranked round-limit games, queen alive at the end, by start day)

| cohort | 2 Oct (n) | 3 Oct (n) | 4 Oct to 05Z (n) | RL games queen-decided 2 → 4 Oct |
|---|---:|---:|---:|---:|
| top10 | 0.368 (876) | **0.516** (258) | 0.472 (284) | 0.42 → 0.49 |
| r11–50 | 0.246 (662) | 0.335 (833) | **0.350** (999) | 0.38 → 0.43 |
| ranked 51+ | 0.205 (483) | 0.328 (338) | 0.283 (456) | 0.34 → 0.42 |
| us (carthage-05) | 0.000 (43) | 0.000 (9) | 0.000 (17) | 0.26 → 0.24 |

The second tier is climbing fastest (+10 pp in two days); the top ten plateaued near 0.5. Half of all ranked round-limit games
are now settled on the queen. Every day we wait, the price of a dead queen rises; the 3 Oct top-ten games are few (258) because
the top ten plays fewer ranked games than the tiers below.

## 2. Opening gap at r50 per structural cluster (unit 7 clusters; z vs per-map field; series table)

| structural cluster (maps) | top-10 n | us n | gap transits | gap bed | gap splits | gap pearls | **gap total** | top-10 own z: tr / bed / sp / total |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| maze | 136 | 23 | 0.40 | 0.74 | 0.68 | 0.68 | **0.82** | 0.03 / 0.15 / 0.19 / 0.18 |
| portals | 144 | 19 | 0.66 | 1.10 | 1.21 | 1.21 | **0.81** | 0.14 / 0.40 / 0.44 / 0.30 |
| open-wrap (Australia, Around UNSW) | 266 | 39 | **0.88** | 0.90 | 1.21 | 1.06 | 0.73 | 0.06 / 0.33 / 0.43 / 0.26 |
| weakhold | 136 | 17 | — (no portals) | −0.44 | −0.52 | −1.02 | 0.72 | — / 0.10 / 0.10 / 0.16 |
| open mega-cluster (Autarky, PD, PD10, Slithery, Devil, Trauma, Stripes, Tower Defense) | 944 | 107 | 0.63 | 0.49 | 0.47 | 0.42 | 0.57 | 0.16 / 0.27 / 0.28 / 0.30 |
| schooltime + islands | 289 | 41 | 0.27 | 0.15 | 0.39 | 0.31 | 0.38 | 0.05 / 0.44 / 0.46 / 0.41 |
| default / trophy | 267 | 38 | **0.67** | 0.02 | 0.01 | 0.10 | 0.02 | 0.32 / 0.15 / 0.17 / 0.17 |
| qos | 129 | 12 | −0.01 | −0.46 | −0.46 | −0.46 | −0.59 | 0.27 / 0.31 / 0.24 / 0.33 |

Field percentile of the top-ten median per cluster (where the top ten sit in the field): transits 0.53–0.79 (weakhold n/a),
bed 0.54–0.67, splits 0.55–0.68, total 0.54–0.63 — the top ten are only at the 55th–65th percentile of the ranked field on
opening components; **our deficit (below the field median almost everywhere) is larger than their edge**. Per-cluster reading:

- *default/trophy*: a pure transit gap (0.67) with every economy component at parity — the clean portal-opening test
  cluster (with Autarky inside the open cluster, unit 6).
- *portals, open-wrap, maze*: everything is behind by ~0.7–1.2 SD; starved-opening fixes (L35) plus transits.
- *weakhold*: we out-eat the field early (bed/pearls −0.4 to −1.0 means we lead) yet end 0.72 behind on total: pure
  attrition — the sealed-pocket deaths (unit 6), not economy.
- *schooltime+islands* and *qos*: small or negative gaps; no opening work.

## 3. Readings

- Rome has taken H-KZ12 (directed-entry veto, doses 0/4/8/16, 60 paired eligible fixtures, seed 1) on the clean carthage-05 on
  `LIVE_MAPS_M2` — correct parent and set. The endpoints to read: wall deaths/1k and queen alive on Trauma/Portals/Maze/weakhold
  (behavioural classes C/E and the corridor members of B); pearls@50 is the cost guard (the bait is food). Nothing else should
  move; if open-map economy moves, the veto is firing where it should not.
- No C+D-only cage arm yet; Rome's dose screen stays HOLD (unit 7 reading).

## 4. Store

No change (51,396; post-m2 queue ~6,300; native decode idle since 05:18Z). The `tools/s1/build.py` divergence with main
(Shenzhen's `--no-games/--flush` hunks vs my queen/map_era hunks) auto-merges cleanly; both sets are now on main.

Ledger: L49 0.8 stands (field adoption continues to rise); L41 0.6 (default/trophy pure-transit cluster adds a second clean
test cluster); L35 re-keyed to portals / open-wrap / maze clusters on the new maps.
