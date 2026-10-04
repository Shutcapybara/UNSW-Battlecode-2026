---
id: shenzhen-unit8-cage-cap-reserve
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator check (analysis copy, not a candidate)
title: Unit 8 — H-SZ22 implemented as probe E (non-queens keep 3 unit slots free): 12/12 on live Schooltime, no change on Trauma/Portals
evidence: cloud workspace, unswbc 1.2.9, maps/live templates + tools/shenzhen/maps_live/schooltime_variant_open4.map; carthage-05 vs probe copies
patch: tools/shenzhen/probes/h-sz1-cage-main.cpp.patch (now C + D + E)
---

# 1. Probe E

Non-queen dragons decide with the unit cap lowered (the queen keeps the real cap), so a slot is always free for the
caged queen's forced split (a pearl spawns in the cage's free cell → the queen must eat → length 4 → split).

**Reserve 1 is not enough.** Seed 5 (seat B) still lost its queen at r292 (invalid split at 64 units): the team went 61 →
63 in one round, because several dragons split in the same round on a unit count sensed at the start of their own turn.
**Reserve 3** closes it.

| probe (vs carthage-05, live Schooltime) | seeds × seats | wins | queen alive at end |
|---|---|---|---|
| C (unit 4) | 6 × 2 | 11/12 | final length 2 (paid sprint) |
| C + D (unit 5) | 6 × 2 | 10/12 | 3 in 9/12 |
| C + D + E, reserve 1 | 6 × 2 | 12/12 | 11/12 (s5-B dies r292 at the cap) |
| **C + D + E, reserve 3** | s3, s5 × 2 + the open-4 variant s1–3 | **7/7** | **7/7, length 3** |

Off-cage check: C+D+E3 vs C+D on Trauma and Portals, seeds 1–2, both seats: the four games are identical in each seat
order (same winner, same score). The reserve did not bind there. Four games are not a parity run; the desktop golden
harness should confirm.

# 2. Hypothesis added

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ24 stale unit count | Within a round every dragon reads the unit count from the start of its own turn, so several splits can land on the same "free" slots. Any cap-based rule in our bot (the 70 % saturation search cap, split gating, H-SZ22) overshoots by up to a few units per round; at the cap the overshoot is invalid splits, which kill the splitter. Corpus check: our `invalid` deaths at 63–64 units. | our invalid deaths with units ≥ 62 < 1 per 20 live games (nothing to fix) | corpus count over live 14585 games | analyst, then the cage arm |
