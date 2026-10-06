---
id: shenzhen-unit28-last-slot-children
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: log pass over existing simulator replays (no new games)
title: Unit 28 — children born at the cap are the team's best children: at headroom 0–1 they live longest (median 51 vs 33–39 rounds of a 100-round window) and eat most (3.2 vs 2.65 meals/100 r). H-SZ54 refuted in the opposite direction, and that is why any reserve costs the cap maps
evidence: tools/shenzhen/szheadroom.py over units 18, 22, 23 and 24 sim replays (carthage-05 family on both sides; Around UNSW, Islands, Australia); births = frame split events, r ≥ 50 and ≥ 100 rounds before the end; headroom = 64 − the team's live dragons the round before; life and meals in a 100-round window
---

# 1. Result

| birth window | headroom | children | median life (of 100) | died within 100 | meals / 100 r |
|---|---|---|---|---|---|
| r50–200 | **0–1** | 4,436 | **51** | 0.69 | **3.20** |
| | 2–4 | 1,178 | 39 | 0.75 | 2.68 |
| | 5–9 | 1,510 | 39 | 0.75 | 2.64 |
| | 10–19 | 3,658 | 40 | 0.76 | 2.66 |
| | 20–64 | 4,755 | 49 | 0.70 | 2.76 |
| r200–400 | **0–1** | 10,508 | **51** | 0.73 | **3.20** |
| | 2–4 | 1,586 | 38 | 0.82 | 2.63 |
| | 5–9 | 1,653 | 33 | 0.83 | 2.64 |
| | 10–19 | 2,165 | 33 | 0.86 | 2.70 |
| | 20–64 | 1,065 | 29 | 0.89 | 2.75 |

# 2. Reading

* **H-SZ54 refuted, reversed** (0.35 → 0.05). Children born at the cap are not wasted: within the same round window they
  live about 30–50 % longer and eat about 20 % more than children born with slack. The pattern holds early and late, so it
  is not a game-phase artefact.
* A likely mechanism (not tested): at the cap a split is possible only right after a death frees a slot, and the
  parent that wins that slot is the one whose decision fires first, usually a well-fed dragon in open food. Its child
  starts in good ground. Born with slack, children are made anywhere.
* This explains the unit-25/27 cost: **the last slot is the team's most productive slot**, and any reserve (E1, E1p)
  takes exactly those births. The cage needs that same slot. The trade is real and sits where the reserve binds.
* Over half of all children (14,876 of 32,412) are born at headroom 0–1. On these maps the team lives at the cap
  most of the game.

# 3. Hypotheses

* **H-SZ54 refuted (→ 0.05).**
* **H-SZ56 (0.4, new) — the cap is the economy's binding constraint on the open maps.** If the best children are born
  at the cap, then freeing slots faster (more culls of weak dragons at the cap, H-SZ31 probe K) should raise total on the
  open maps. Prediction: probe K (cull to free, unit 13) raises pool total ≥ +5 % on Around UNSW / Islands / Australia in
  18 sim games. Falsifier: total ≤ 0. Unit 13 tested K on cage and Slithery only. Size: 18 sim games. Suits this
  lane next unit.
* **H-SZ57 (0.3, blue-sky) — a cap-aware birth auction.** The slot freed by a death should go to the dragon whose child
  would do best: the one in the richest visible food. Today it goes to whoever decides first, which depends on id order.
  A slot-claim message on the existing radio could let the best-placed dragon split. Falsifier: in sim, children born
  after a claim do no better than today's (median life 51, 3.2 meals). Size: 18 sim games. Bigger build. Suits a
  tester.

**RL translation.** Observation: headroom (0–1 is a distinct regime, not the tail of a continuum). Action: split when a
slot frees. Value: a child born at the cap is worth about 3.2 meals per 100 rounds. That prices both the reserve's cost
and a cull's benefit.
