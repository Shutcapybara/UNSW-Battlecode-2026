---
id: shenzhen-unit20-seals-close-in-two-moves
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator logging (no behaviour change; identical outcomes to the unit-18 arm) + reading of Asahi P-A01
title: Unit 20 — sealed queens: two rounds out, 6 of 10 are already in a small pocket (≤ 32 cells) that the parent's flood still scores as open; the other 4 have the whole board and are sealed within two moves. H-SZ45 refuted as stated; the lever is a gate test
evidence: `c05rl` = Q + R + LOG SZROOM (parent `room_for_body`, need 400, every queen turn) vs carthage-05 + C+D; Around UNSW / Islands / Australia s1–3 both seats, 18 games (outcomes identical to `c05r`, unit 18: logging changes nothing); tools/shenzhen/szroom.py (true room = static BFS on the frame snapshot, all bodies block, kelp from the frame's `nbr`)
---

# 1. Room before each queen death (18 games, k = rounds before the death round)

| death | n | k | parent estimate ≥ 2L | static true room < L | median estimate | median true room |
|---|---|---|---|---|---|---|
| sealed (self, wall) | 10 | 3 | 8 | 1 | 400 (cap) | 404 |
| | | 2 | 5 | 3 | 305 | **32** |
| | | 1 | 1 | 6 | 0 | 2 |
| enemy head-on | 6 | 1–3 | 6 | 0 | 400 | 412–429 |
| body | 2 | 1–3 | 1–2 | 0–1 | 400 | 419–446 |

# 2. Reading

Per-death detail at k = 2 (length L, true room, parent estimate): (2, 403, 305), (2, 416, 400), (3, 6, 400), (3, 404, 400),
(4, 2, 1), (4, 413, 1), (5, 4, 400), (8, 11, 1), (8, 32, 1), (11, 2, 1). The median of 32 hides two groups:

* **6 of 10 are already in a pocket two rounds out** (true room 2–32). For 2 of them (lengths 3 and 5) the parent's flood still says
  400: it counts cells behind moving bodies and its own tail as free. For the other 4 it already says 1.
  The queen has entered a dead end (a pocket or a notch) and has at most two moves left.
* **4 of 10 still have the whole board two rounds out** (403–416 cells), and are sealed within two moves. A body crosses
  the gate, or her own turn closes it.
* **H-SZ45 refuted as stated** (prediction: estimate ≥ 2L while true < L in ≥ 70 % of seals; observed 1/10 at k = 2,
  0/10 at k = 1). The flood is optimistic in some cases (2/10 at k = 2), not systematically.
* Either way the decisive step is **entering** a region joined to the rest of the board through a narrow gate, at
  k = 2–3. Room counts at the moment of entry are large, so a room test cannot see it. A cutset test can.

# 3. Hypotheses

* **H-SZ46 (0.5, new) — two-gate rule for the queen.** The queen does not move into a cell whose reachable region,
  with the cell just behind her removed, is joined to the large component only through a gate of width ≤ 2 (one
  articulation pair on the static occupancy), unless that region holds ≥ 4 L cells. Falsifier: queen sealed deaths not
  halved in a Q + R + two-gate stack (18 sim games), or total < −5 % (Islands canary). This is the general form of
  Kanazawa's pocket veto (H-KZ12, baited dead ends): a gate test, not a room test.
* **H-SZ47 (0.35, blue-sky) — gates are where the field's queens differ.** Live, top-ten queens should cross fewer
  narrow gates per 100 rounds than ours. Store query: the frame occupancy plus `maps/live/` kelp give gate crossings
  per queen; about 200 post-m2 games on Around UNSW, Australia, Islands, Maze. Suits Data (Kageyama).

# 4. Reading P-A01 (Asahi, C+D with E = 0, seed 1)

Agreed with Asahi's last sentence. Schooltime queen alive@RL 4/15 with E = 0, against Rome's C+D+E1 11/16, fits this
lane's engine fact (unit 9): a sealed-cage split at 64 units is invalid, so probe C's cage split works only when a unit
slot is free. **E is the cage lever, not just a tax** — it buys the slot. H-SZ22 stays as it was: reserve only while our
queen is caged, which keeps E's cost (pearls@250 −7 to −11) off the other maps. Kageyama's open-4 Schooltime variant
(half of live games) and the 10-dragon Prisoners Dilemma variant are the two files in `tools/shenzhen/maps_live/` on r/shenzhen
since unit 7: `schooltime_variant_open4.map`, `dilemma_10_live.map`.

**RL translation.** Observation: a local gate/cutset feature around the queen (width of the narrowest gate to the main
region), plus room. Action: the queen's step. Value: queen survival. Demonstration: field queens' gate crossings (H-SZ47).
