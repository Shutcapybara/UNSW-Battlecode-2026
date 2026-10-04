---
id: shenzhen-unit10-serialised-splits
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator check (analysis copies, not candidates) + corpus query
title: Unit 10 — serialising production splits near the cap halves trapped deaths at the cap but costs a fifth of total length; the reserve (E3) does the opposite; at the cap the top ten are longer per unit
evidence: cloud workspace, unswbc 1.2.9 live Slithery Fight, carthage-05 copies, seeds 1–6 both seats (12 sides per arm); lean table post-m2
probes: G = C + D + "near the cap (units ≥ limit − 8) a non-queen production split (len ≥ 4) runs only when id % 4 == round % 4; escape splits are never blocked"
---

# 1. Simulator (Slithery, vs C+D, 12 sides each)

| arm | wins | side-rounds at 64 units | at ≥ 60 | non-queen trapped deaths (wall/self, len ≥ 4) at ≥ 60 units | total at end | longest at end |
|---|---|---|---|---|---|---|
| C+D (parent) | 6/12 | 2,433 | 3,861 | 174 | 1,587 | 530 |
| **G (serialised)** | 6/12 | 1,438 (−41 %) | 3,772 | **97 (−44 %)** | 1,218 (**−23 %**) | 475 (−10 %) |
| E3 (reserve 3), s1–3 only, 6 sides vs 6 | 3/6 vs 3/6 | 39 vs 1,146 | 1,874 vs 1,883 | **150 vs 83 (+81 %)** | 664 vs 784 | 264 vs 244 |

Seeds 1–3 alone looked like a win (G 5/6); seeds 4–6 reversed it. The mechanism does what H-SZ25 said (fewer dragons
trapped at the cap, less time at 64), and the reserve does the opposite (it blocks escape splits, so trapped deaths rise
+81 %). But neither moves wins, and both cost total length. **The cap churn is not pure waste**: split → trapped → die →
corpse → eaten keeps total length up.

# 2. Corpus: at the cap, the top ten are longer per unit

Post-m2 lean table. Share of sides at ≥ 62 units at r250: Slithery top ten 0.67, us 0.94; Around UNSW 0.73 / 1.00;
Australia 0.55 / 0.59; Islands 0.54 / 0.33; Schooltime 0.48 / 0.59; 0.00–0.03 on Default, Devil, Autarky, Trauma, Portals,
QoS, PD, Stripes, Tower Defense, weakhold. On Slithery at r250 the top ten hold 62 units and **194** total length (median),
we hold 64 and **158**. Same unit count, 23 % more length.

# 3. Hypotheses

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ25 (simulator: mechanism yes, value no) | Serialising production splits near the cap halves trapped deaths at the cap. Not a win lever alone (6/12 vs 6/12, total −23 %). Kept as a component for H-SZ26, not as an arm. | — | — | — |
| H-SZ22 (revised down) | The reserve E3 blocks escape splits (+81 % trapped deaths at the cap on Slithery). Keep it only where it protects the caged queen: apply it only when our queen is caged (it has no non-fatal move without splitting). | cage results fall below 7/7, or Slithery trapped deaths still up with the cage-only condition | simulator | Claude tester |
| H-SZ26 length per unit at the cap | On cap maps (Slithery, Around UNSW, Australia, Islands, Schooltime) production splits buy nothing once units ≥ ~60: the top ten hold 62 units with 23 % more length. At the cap, stop production splits and grow instead (eat without splitting; cull small units into a longer one). | an arm that disables production splits at ≥ 60 units does not raise total@400 on those maps, or loses wins | simulator first (Slithery/Around UNSW, 12 sides), then panel | Claude tester |
