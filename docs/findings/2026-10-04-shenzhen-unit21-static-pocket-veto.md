---
id: shenzhen-unit21-static-pocket-veto
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator screen (analysis copies only) + one council reading
title: Unit 21 — a static pocket veto for the queen halves sealed queen deaths (10 → 5) and raises pool total +15 %, but it overrides the strike veto and strikes come back (6 → 11). The queen still does not survive; the three queen rules must be one decision, not three overrides
evidence: unswbc 1.2.9; `c05g2` = Q (H-KZ26 m0) + R (H-SZ40) + G (H-SZ46a, below) vs carthage-05 + C+D (`c05d`); Around UNSW / Islands / Australia s1–3 both seats, 18 games; tools/shenzhen/szqdeath.py, szleak.py
---

# 1. Probe G (H-SZ46a, the cheap form of the gate rule)

The queen does not end her move where her **static** room is below 4L + 16 cells. Static room means a BFS over the board
with every dragon part blocking, the queen's own simulated body blocking, kelp blocking and unknown edges open. If her plan
lands below that, she takes the safe single step with the most static room, when it has more. This is pessimistic where
the parent's flood is optimistic (unit 20). The gate is not computed: a region with a narrow exit shows up as low static
room once the exit is occupied. G fires 16 times in the logged game. G sits after Q in the code, so G can override Q's
strike-veto step.

# 2. Result (18 games; queen deaths of our side)

| arm | enemy head-on | wall | self | ally body | invalid | mean death round | alive at end | wins | pool total |
|---|---|---|---|---|---|---|---|---|---|
| c05d (this set) | 14 | 2 | 2 | 0 | 0 | 178 | 0 | 6 | 2,503 |
| Q + R (unit 18) | 6 | 6 | 4 | 2 | 0 | 197 | 0 | 7 | 2,547 |
| **Q + R + G** | **11** | **4** | **1** | 2 | 0 | **217** | 0 | **12** | **2,883 (+15 %)** |

Per map total: **Around UNSW +26 %**, **Islands +37 %**, Australia −13 %. The enemy's share of our corpse pearls is
unchanged (0.32 vs 0.34).

# 3. Reading

* **Sealed deaths halve** (wall + self 10 → 5 against Q + R), and the queen lives longest of any arm so far (r217). This
  meets H-SZ46's falsifier bar. Pool total is up 15 % with Islands up, so it passes the H-SZ37 screen. The Australia −13 %
  is the cost to watch.
* **Strikes come back** (6 → 11): G's room-maximising step ignores Q's reach slack. The queen escapes the pocket into a
  striker's reach. Each override removes one hazard and opens another (unit 18), and G re-opened Q's.
* Queen alive at the end is still 0/18. The next probe must choose the queen's step once, over all three constraints:
  strike slack > 0, no split at the cap, static room ≥ 4L + 16. Among safe steps, take the one that is best on the
  worst-violated constraint, not apply three overrides in sequence. This is a small evaluation function for the queen
  (the chess-bot framing): one score per candidate step.

# 4. Hypotheses

* **H-SZ46 → 0.6**, in its static form (H-SZ46a): sealed deaths halved, total +15 %.
* **H-SZ48 (0.5, new) — the queen's step is one lexicographic choice.** Among simulate-OK single steps (and the
  parent's plan), pick by (no strike reach, static room ≥ 4L + 16, the parent's score). Prediction: queen alive at end
  ≥ 3/18 on the three open maps, total ≥ parent. Falsifier: alive ≤ 1/18, or strikes and seals not both below
  c05d's in the same arm. Size: 18 sim games. Suits this lane next unit, then a tester on `LIVE_MAPS_M2`.
* **H-SZ49 (0.3, blue-sky) — the same three terms make a learned queen value.** The Learner's queen block needs exactly
  these observations: strike slack under B(L), static room, unit headroom. An R4 feature block of the three should
  beat the parent's flood on queen-survival AUC at r100–r250 (store, LOMO). Falsifier: the AUC gain is below +0.02.

# 5. Reading Sugawara's P-sugawara-01 (map-size gate for E)

Sugawara's mechanism finding is right: "while our queen is caged" is not observable by the non-queens that must hold the
reserve. But a 60 × 40 gate is map identity by another name: the card says it is unique across `maps/live/`, new, m2tr
and var. The common rules forbid map identity in bots (structure only). Its known cost, the open-4 variant at ≈ 47 % of
live Schooltime, shows the problem: the gate keys on the map name, not on the cage. Two legal observables do the same job:

1. **Initial dragons can see the cage at r0.** A starting non-queen that has the queen's head (id 0/1, visible) in its
   7 × 7 view at r0 with no legal exit (all four kelp or body) knows the queen is caged. Whether one does on the live
   cage is a one-replay check, and I have not made it. This is the
   same test probe C uses on itself.
2. **The bit can be relayed.** Carthage's radio already carries typed sonar messages (`send_radio`, types 1/2/4).
   One more type, "queen caged", relayed dragon to dragon, reaches newborns within a few rounds. A newborn without the
   bit applies no reserve, which is cheap: E's cost lies in the many rounds it holds, not in a few rounds of delay.

I suggest the card be amended to "E while a relayed cage bit is set (r0 observation)" before any run. The parity check
on non-Schooltime maps then tests the observation (it should never fire there), not a map name.

**RL translation.** Observation: strike slack, static room, unit headroom, and a relayed cage bit. Action: the queen's step
(one choice), and the reserve. Value: queen survival, with total as a guard. Demonstration: field queens (Chongqing unit 5:
0.18–0.29 alive on contact maps).
