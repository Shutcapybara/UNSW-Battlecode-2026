---
id: shenzhen-unit24-global-e1-cage
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator screen (analysis copies only) — H-SZ50, the legal (map-blind) cage reserve
title: Unit 24 — a global one-slot reserve (E1 on every map, no map gate) keeps our Schooltime queen alive 6/6 on both live variants (C+D alone 4/6 cage, 3/6 open-4) and wins 5/6 on each; Around UNSW shows no cost (total +35 %, n = 6)
evidence: unswbc 1.2.9; `c05e1` = carthage-05 + C + D + E1 (non-queens decide with limit − 1, every map) vs `c05d` = carthage-05 + C + D; Schooltime template (`school_new`), Schooltime open-4 variant (`tools/shenzhen/maps_live/schooltime_variant_open4.map`), Around UNSW; seeds 1–3, both seats, 6 games per map
---

# 1. Result

| map | arm | our queen alive at end | queen deaths | wins | pool total |
|---|---|---|---|---|---|
| Schooltime (cage) | C+D | 4/6 | invalid 2 | 1 | 732 |
| | **C+D+E1** | **6/6** | — | **5** | **1,236** |
| Schooltime open-4 | C+D | 3/6 | invalid 3 | 1 | 832 |
| | **C+D+E1** | **6/6** | — | **5** | **1,091** |
| Around UNSW (cost check) | C+D | 0/6 | h2h 4, wall 1, self 1 | 2 | 878 |
| | C+D+E1 | 0/6 | h2h 3, wall 3 | 4 | 1,183 |

Every queen death under C+D on both Schooltime variants is `invalid`: a split at the unit cap, the mechanism in unit 22
(the caged queen must eat each bed spawn, and must then split). E1 leaves one slot free on every map, so she can
always split, and she survives.

# 2. Reading

* **H-SZ50 supported in the sim (0.45 → 0.65):** a map-blind E1 does what the cage needs on both live Schooltime
  variants. The open-4 variant (about half of live Schooltime, Kageyama) also loses its queen to cap splits under C+D, so a
  cage-only gate would not have covered it either.
* **Cost check:** one open map, 6 games, no visible cost (total +35 %, wins 4–2). That is too small to price E1 on
  the other 15 maps. Rome's live-set screen of E1/E3 measured pearls@250 −7/−11 on the pool, and unit 10 found team-wide
  E3 raising trapped deaths at the cap on Slithery. E1 should cost less than E3, but it needs the D-042 panel, not this
  unit.
* This is the legal answer to the observability problem Sugawara raised. Nobody needs to know the queen is caged
  if the slot is always free.

# 3. Hypotheses

* **H-SZ50 → 0.65.** Ask for Asahi/Rome: run **C+D+E1, ungated**, on `LIVE_MAPS_M2` with both Schooltime variants.
  Prediction: Schooltime queen alive@RL ≥ 12/16 on each variant, pool pearls@250 ≥ −8 vs C+D. Falsifier: queen
  ≤ 9/16, or pool cost < −10.
* **H-SZ52 (0.4, new) — E1 helps beyond the cage.** Under C+D, the queen's `invalid` deaths are not only a Schooltime
  thing: unit 17 found 4 cap-split queen deaths on open maps under the strike veto, and H-SZ40 removed them. A global
  E1 gives every dragon a free slot when its split is the only escape (probe C), not just the queen. Prediction:
  `invalid` deaths per 1k drop ≥ 50 % on the pool with E1, and wall deaths do not rise > 10 %. Falsifier: the pool
  invalid rate is unchanged. Size: the same E1 screen, read on the deaths table.

**RL translation.** Observation: unit headroom (units vs limit) is a first-class feature for every dragon. Action: a
production split is legal for the team only below limit − 1. Value: queen survival on cage maps, total elsewhere.
Demonstration: field queens on Schooltime survive 0.86 live (Chongqing unit 5).
