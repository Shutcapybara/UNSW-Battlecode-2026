---
id: shenzhen-unit5-cage-length-and-sprint-tax
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator check (analysis copies, not candidates)
title: Unit 5 — the caged queen's viable length is exactly 3; our policy spends it on a sprint; a cage pearl at the unit cap kills it
evidence: cloud workspace, unswbc 1.2.9 live Schooltime, carthage-05 vs probe copies, seeds 1–6 both seats; replays decoded with FRAME_VERSION 7
patch: tools/shenzhen/probes/h-sz1-cage-main.cpp.patch (now probe C + D)
---

# 1. What probe C's queen did (seed 1, decoded)

r0 split (queen keeps 2, child 2); the child dies (self) in the cage; r1 the queen eats the child's corpse (`ally_corpse`,
donor = child) → length 3; it then circles the 2×2 (the fourth cell is always free). **At r250 it sprinted 2 steps
and paid 1 segment** (free steps ⌈3/4⌉ = 1) → length 2 for the rest of the game. A length-2 queen loses the queen
tiebreak to the top ten's caged queens (median length 3).

Length 4 has no legal move in the cage (unit 4: the tail cell is never enterable), so **3 is the maximum viable caged
length** and the only length that ties the top ten.

# 2. Probe D = C + "the queen never pays segments for a sprint" (truncate its move to ⌈L/4⌉ steps)

| seat | wins | final queen |
|---|---|---|
| D as A | 5/6 (4 by queen 3–0; s1 by longest after its queen died) | 3 in 4/6 |
| D as B | 5/6 (5 by queen 3–0) | 3 in 5/6 |

Seed 3 kills the queen in both seats. Decoded (seat A): a pearl spawned in the cage's free cell at r131; the queen's only
move ate it → length 4 → sealed; the probe split it at r132 and the engine killed it **invalid**. Himeji H16-02 measured
the same legality edge independently: a full 4-cell queen split is valid at 63 units and invalid at 64 (the unit cap).

# 3. Hypotheses

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ20 (revised) | The caged queen's target length is exactly 3 (eat the child's corpse, then never grow, never pay). Length 3 ties the top ten's caged queens; the tie goes to longest. | caged queen length at r490 ≠ 3 in > 20 % of live-Schooltime games | 40 live-Schooltime games | tester, with H-SZ1 |
| H-SZ21 queen sprint tax | The queen never pays segments for a sprint, on any map: its length is the first tiebreak key and each paid segment is a tiebreak point. Corpus check first: how many segments do queens (ours, top ten) pay per game? | our queens pay < 0.1 segment per game alive (nothing to fix), or a queen-no-pay arm moves queen len@490 by < 1 | corpus query, then pool s1–3 | analyst → tester |
| H-SZ22 cage at the cap | When the caged queen is at length 3 and a pearl can appear in its free cell, keep a unit slot free (cull a small ally at the cap) so the forced eat → split → child-suicide cycle stays legal. | cage deaths by invalid split at 64 units ≥ 1 per 40 games after the rule | 40 live-Schooltime games late (r ≥ 250) | tester |
