---
id: shenzhen-unit19-room-veto-does-not-bind
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator probe + replay anatomy (analysis copies only)
title: Unit 19 — the queen room veto (H-SZ42) almost never fires; the parent's own flood says the queen has room until the turn she is sealed. One anatomy case is a growth trap; across 30 sealed queen deaths, growth explains only 13 %
evidence: unswbc 1.2.9; `c05s` = Q + R + probe S (H-SZ42) vs carthage-05 + C+D (`c05d`), Around UNSW seed 1 with logs; tools/shenzhen/szgrowtrap.py over the unit-17/18 games (36 + 18 games)
---

# 1. Exposure

Probe S: if the queen's planned move leaves less than `need` cells of the parent's own time-aware flood room
(`room_for_body`, others' parts free at `vac`, own segments free at i + 2, a one-step head block), take the safe single
step with the most room.

| need | fires in one 500-round game | queen death |
|---|---|---|
| 2 × L | **0** | r199, `body` |
| 4 × L + 8 | **1** | r203, `self`, length 11 |

The dial does not reach (Nara's rule: a dose with no exposure is "did not reach", not "does not work"). The 18-game run
was stopped, because it could only reproduce the Q + R result. **H-SZ42 as specified is void on this parent**: by the
parent's own model the queen is never short of room until she is sealed.

# 2. Anatomy of the case (Around UNSW s1, our queen id 0)

Rounds 195–202: the queen eats on 7 of 8 turns along a corpse trail (2 ally corpses, 3 enemy corpses, 2 bed pearls),
growing 6 → 11. Her tail does not move while she eats. At r202 she turns into a one-cell notch against kelp at (31, 33).
At r203 her only exits are her own body (north) and her own neck (south), and she dies `self`. The flood had credited
her own segments freeing at i + 2. That is wrong while she grows: a meal on every step freezes the tail.

# 3. How common is the growth trap? (`szgrowtrap.py`, 54 sim games)

Meals in the 5 rounds before death:

| who | death group | n | mean meals | share with ≥ 3 meals |
|---|---|---|---|---|
| queen | sealed (self, wall) | 30 | 0.83 | **0.13** |
| queen | head-on | 60 | 0.63 | 0.05 |
| queen | rest (invalid, body) | 16 | 3.0 | 0.62 |
| others | sealed | 4,991 | 0.54 | 0.05 |
| others | head-on | 19,090 | 0.58 | 0.05 |

Sealed queens eat more just before death than other dragons do. Feeding is a factor, but only 4 of the 30 sealed queen
deaths are clear growth traps. The other 26 seals come from something the flood also does not see. The queen's "rest"
deaths (invalid, body) follow heavy feeding (3.0 meals, 62 % ≥ 3): a queen that has just grown long is where both
the production split at the cap (H-SZ40) and body collisions happen.

# 4. Hypotheses

* **H-SZ42 void** on carthage-05 (zero exposure). A room veto must use a pessimistic flood, not the parent's.
* **H-SZ44 (0.25) — growth-aware flood.** Freeze the tail for each pearl on the path, so own segments free at
  i + 2 + meals. It fixes the anatomy case but covers ≤ 13 % of sealed queen deaths. Falsifier: sealed queen deaths not
  −10 % in a stacked sim. It is a cheap component for the Learner's room feature, not a lever by itself.
* **H-SZ45 (0.45, new) — the flood is optimistic about moving bodies.** The parent's flood frees other dragons' parts at
  `vac` and blocks only one step around other heads, so a queen among moving bodies is sealed by cells the flood
  counted as free. Test with no bot change: log the flood room the turn before every queen death in 18 sim games and
  compare it with the room actually reachable then (replayed from the frame). Prediction: estimated room ≥ 2 L in
  ≥ 70 % of the sealed cases while the true room is < L. Falsifier: estimate < 2 L in most sealed cases (the veto would
  then have fired). Suits this lane (sim logs) or the Learner, as the R4 room feature.
* **H-SZ41 (stack)** stays at 0.4 but loses its third piece until H-SZ45 says what the seal is.

# 5. Caveats

One logged game for the exposure count. Meal counts use the frame's eat events by dragon id. The baseline is the parent's
own bodies, not the field's.

**RL translation.** Observation: a flood room that counts growth and other dragons' motion, not the parent's optimistic
one. Action: the queen's step choice. Value: queen survival time. Demonstration: field queens survive on contact maps
(0.18–0.29); their room at the death-adjacent turns is a store query once a room feature exists.
