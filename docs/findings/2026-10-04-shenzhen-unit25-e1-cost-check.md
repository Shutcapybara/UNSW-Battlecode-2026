---
id: shenzhen-unit25-e1-cost-check
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator cost check (analysis copies only) for H-SZ50/H-SZ52
title: Unit 25 — the ungated E1 reserve is inert on Portals and Trauma (games identical: the cap is never reached), and costs Slithery about 7 % of total. H-SZ52 (E1 halves invalid deaths) is refuted on Slithery (−9 %)
evidence: unswbc 1.2.9; `c05e1` (carthage-05 + C + D + E1, no map gate) vs `c05d` (C + D); Slithery Fight, Portals, Trauma; seeds 1–3, both seats, 6 games per map
---

# 1. Result

| map | arm | wins | pool total | our invalid deaths | our wall deaths | queen alive at end |
|---|---|---|---|---|---|---|
| Slithery Fight | C+D | 4 | 741 | 1,836 | 292 | 0/6 |
| | C+D+E1 | 2 | 691 (−7 %) | 1,676 (−9 %) | 238 (−18 %) | 0/6 |
| Portals | both | 3 / 3 | 235 / 235 | 1,213 / 1,213 | 353 / 353 | 0/6 both |
| Trauma | both | 3 / 3 | 238 / 238 | 394 / 394 | 143 / 143 | 0/6 both |

On Portals and Trauma the E1 arm reproduces the parent move for move: units never reach limit − 1 there, so the reserve
never binds. (This repeats the unit-9 "vacuous parity" warning: parity on these maps says nothing about E.)

# 2. Reading

* **E1's cost lives on the cap maps.** In this lane's sims (units 24–25) the cap binds on Slithery and the big open maps.
  Slithery pays −7 % total and 2 fewer wins in 6. Around UNSW (unit 24) showed no cost (+35 %, n = 6). The sign is
  mixed and the samples are small. Rome's live-set pool cost (−7 pearls@250 for E1) remains the number to plan with.
* **H-SZ52 refuted where it could be tested.** Slithery's invalid deaths fall only 9 %, not ≥ 50 %. Most of the
  invalid deaths under C+D are not slot-starved splits: they are probe C's sealed-dragon culls by design (`SPLIT 99`
  for non-queens), which E1 does not touch. → H-SZ52 0.4 → 0.15.
* **H-SZ50 stands at 0.65** for its target (the Schooltime queen). The trade the Chair has to weigh is Schooltime
  (+2–3 queens per 6, wins 5–1 in sim; live −0.45 score on that map) against a few-percent total cost on cap maps.

# 3. Hypotheses

* **H-SZ53 (0.45, new) — reserve production, not escapes.** A headroom gate would be vacuous, because E1 binds only at
  limit − 1 anyway. What E1 also blocks is the escape splits: c05e1 lowers `w.limit` for the whole decision, so
  `tyr_escape_split` and probe C's sealed split see the reduced limit as well. Unit 10 found that this is how
  team-wide E3 raised trapped deaths at the cap on Slithery (+81 %). Rule: non-queens apply limit − 1 to production
  splits (`tyr_split_option`, `tyr_opening_split`) only, and keep the real limit for escape and sealed splits.
  Prediction: Schooltime queen alive stays ≥ 5/6 per variant, Slithery cost ≤ −3 %, wall/self deaths there not above C+D.
  Falsifier: the Slithery cost does not shrink, or the Schooltime queen falls back. Size: 12 sim games (Schooltime cage +
  Slithery). Suits this lane next unit.

**RL translation.** Observation: unit headroom. Action: whether to produce at headroom 1. Value: queen survival on cage
maps against production elsewhere: a context-dependent trade a learned value can price, and a fixed rule cannot.
