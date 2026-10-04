---
id: shenzhen-unit23-queen-in-the-crowd-sim
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator screen (analysis copies only) + a prior for the approved P-4 screen
title: Unit 23 — keeping the queen next to an ally head (H-SZ43, sim form) does not keep her alive (0/18) and costs total −10 % (Islands −48 %). For P-4, the sim prior is that m = 0 beats m = 1
evidence: unswbc 1.2.9; `c05y` = c05x (R + Q + X, unit 22) with an "ally head within Chebyshev 3" term inserted in X's order after the room term; vs carthage-05 + C+D; Around UNSW / Islands / Australia s1–3 both seats, 18 games
---

# 1. Probe Y

X's lexicographic order becomes (1) out of B(L) reach, (2) static room ≥ 4L + 16, **(3) an ally head within Chebyshev 3
of the end cell**, (4) keep the plan, (5) room, (6) slack. The queen prefers steps that keep her beside a teammate's
head, the sim form of "the queen in the crowd".

# 2. Result (18 games)

| arm | head-on | sealed (wall + self) | other | alive at end | mean death round | pool total | UNSW / Islands / Australia |
|---|---|---|---|---|---|---|---|
| c05d (this set) | 16 | 1 | 1 | 0 | 165 | 2,821 | — |
| X (unit 22, other set) | 9 | 6 | 2 | 1 | 197 | +15 % | +20 / +11 / +12 % |
| **Y = X + ally term** | 11 | 4 | 3 | **0** | 172 | **2,550 (−10 %)** | +1 / **−48** / +18 % |

# 3. Reading

* **H-SZ43's sim form refuted**: alive 0/18, the queen dies at the same time (r172 vs r165), and Islands collapses
  again (−48 %, as both contact probes of unit 16 did). On Islands an ally head nearby means a
  contested island, not a screen.
* Staying close to an ally does not protect the queen. Live, field queens may survive because of where their team as
  a whole plays, not because the queen holds a station. That stays a store question (H-SZ43 as originally written, for
  Data), not a step rule. → **H-SZ43 back to 0.35.**
* Taking units 17–23 together: across six queen-step arms on three open maps, queen alive at end is 0–1/18 in every
  arm. The sim queen's survival is not reachable by local step rules on this parent. The levers that moved total were
  the strike veto at m = 0 (unit 17) and the one-choice step X (unit 22).

# 4. Prior for P-4 (Sugawara's H-KZ26 screen, D-054 §C: m ∈ {off, 0, 1})

My unit-17 sim on the same mechanism (carthage-05 + C+D, three open maps, 18 games per dose): **m = 0 cut strikes 13 → 6
with pool total +3 % (Islands +32 %); m = 1 cut them only 12 → 9 with total −10 %**. Queen alive at the end did not move
at either dose (0–1/18), because the avoided strikes became seals and invalid splits (unit 18). Two suggestions for the
screen's reading: score the strike column and pool total per map (Islands as the canary), and do not expect the queen
tiebreak to move on contact maps from the veto alone. These are sim priors, not a replacement for the screen.

# 5. Hypotheses

* **H-SZ43 → 0.35** (sim form refuted; the store form stands for Data).
* **H-SZ51 (0.4, new) — the open-map queen is a total play, not a tiebreak play.** On Around UNSW, Australia and Islands
  the live field keeps the queen only 0.18–0.29 (Chongqing unit 5). Our best arms raise total 15 % and leave the queen dead. Prediction: on
  these maps the live win rate tracks total share, not queen survival. Test with the store, ranked post-m2: a logistic
  of win on (queen alive, total share) per map class B. Falsifier: queen alive carries more weight than total share there.
  Size: ~2,000 games. Suits Data/Learner (V0 already fits something like this).

**RL translation.** Value: on class-B maps, weight total share above queen survival. Observation: ally head proximity is
not protective, so leave it out of the queen block.
