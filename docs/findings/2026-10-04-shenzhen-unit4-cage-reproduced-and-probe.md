---
id: shenzhen-unit4-cage-reproduced-and-probe
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator check (analysis copy, not a candidate)
title: Unit 4 — the Schooltime cage reproduced locally with unswbc 1.2.9; the only survival is split + child suicide; a 14-line probe wins 11/12 seat-games
evidence: cloud workspace, unswbc 1.2.9 (engine wasm byte-identical to 1.2.3), carthage-05-free-sprint copied unchanged, maps from unswbc 1.2.9 / 1.2.3 templates; seeds 1–6, both seats
patch: tools/shenzhen/probes/h-sz1-cage-main.cpp.patch
---

# 1. Reproduction (answers Chongqing H-C1 "check first whether the local fixture reproduces it")

carthage-05 vs itself, `unswbc run`, seeds 1–3:

| map | queen (ids 0/1) dies at round 0 | cause |
|---|---|---|
| unswbc 1.2.9 `templates/maps/schooltime.map` (live) | **6/6** | hit itself |
| unswbc 1.2.3 `templates/maps/schooltime.map` = repo `maps/` (old) | 0/6 | — |

The local fixture reproduces it only with the 1.2.9 map.

# 2. Mechanism, from the bot's own simulator and the engine

At round 0 the queen's head is at cell 123 with body 122, 62, 63 (tail first) and every direction simulates DEAD,
including W into its own tail (cell 122). Forcing W (probe B) dies the same way ("hit itself"): **in this engine a
dragon cannot step into the cell its own tail is leaving.** So a 4-long dragon in a sealed 2×2 has no legal move; the
base falls through to its facing (N) and dies.

Splitting is the only survival (probe A): the queen keeps a 2-cell head. But the 2-cell child is sealed too, acts later
in the same round, and moved E into the queen's head; the head-on killed both ("lost a head-to-head"). The working
sequence (probe C): queen splits keeping 2; a sealed non-queen dragon of length < 4 sends an invalid command and dies
alone, leaving the queen in the cage. This matches the top ten's trace on live Schooltime (split at r0, child gone at
r1, queen circles) and Chongqing's anatomy of our live deaths (child invalid/self, queen self).

# 3. Probe C result (live Schooltime, carthage-05 + 14 lines vs carthage-05, seeds 1–6, both seats)

| seat | wins | how |
|---|---|---|
| probe as A | 5/6 | 5 by **queen tiebreak 2–0**; seed 3 lost on longest (probe queen died r132) |
| probe as B | 6/6 | 6 by queen tiebreak (2–0 ×5, 3–0 ×1) |

11/12. The probe touches only turns where every direction simulates DEAD; parity on the other maps and the r132 death
are untested here (the bots' RNG is not seeded outside `--sandbox`, so exact replay parity needs the desktop harness).

# 4. Hypotheses added

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ1 (sharpened) | The cage rule above, as written in the patch. | live-Schooltime queen alive@r10 < 0.95 over 40 games, or parity broken on the old panel (expected 0 divergent turns: the rule fires only when every move is fatal) | 40 games live Schooltime + golden parity | any tester; **ready to build** |
| H-SZ18 sealed-dragon rule | Generalise: any dragon whose four moves all simulate DEAD splits if length ≥ 4, otherwise dies by invalid command — never by a move into an ally head. Expected to remove a share of our "h2h with ally" deaths everywhere, not only on Schooltime. | count of our ally-h2h deaths where the actor had no non-fatal move < 1 per 10 games on the panel (nothing to fix) | corpus count first, then the panel | analyst → tester |
| H-SZ20 cage growth | After the cage split, the queen should eat the child's corpse (+2) instead of staying at 2; the top ten's caged queens end at length 3. A length-4 caged queen wins the Schooltime queen tiebreak against them. | caged queen length at r490 ≤ 3, or Schooltime queen-decided record vs top ten not ≥ .5 | live-Schooltime games vs a keeper proxy | tester, after H-SZ1 |
