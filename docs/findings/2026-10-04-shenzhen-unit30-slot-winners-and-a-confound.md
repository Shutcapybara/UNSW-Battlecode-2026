---
id: shenzhen-unit30-slot-winners-and-a-confound
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: log pass over existing simulator replays (no new games); correction of the unit-28/29 mechanism
title: Unit 30 — the parent that wins a slot at the cap is not better fed than its teammates (2.78 vs 2.87 meals/20 r; top eater only 14 %). Unit 28's "best children at the cap" is a state confound — the team is at 64 units most of the game, and slack only appears after death waves
evidence: tools/shenzhen/szslotwin.py over units 18, 22 and 24 sim replays (carthage-05 family, open maps); team unit counts from frame snapshots (the cap is 64 per team, reached in both teams)
---

# 1. Who wins a slot

| headroom at the split | splits | parent meals (prev. 20 r) | other eligible allies (len ≥ 4) | parent length | others | parent is the top eater |
|---|---|---|---|---|---|---|
| 0–1 | 10,309 | 2.78 | 2.87 | 5.3 | 6.0 | **0.14** |
| ≥ 10 | 6,242 | 3.09 | 3.21 | 4.7 | 5.0 | 0.40 |

At the cap the splitting parent is slightly *less* fed and shorter than its eligible teammates, and rarely the best
eater. **The mechanism I proposed in units 28–29 (a well-fed parent wins the freed slot) is wrong.**

# 2. What the headroom split actually measures

In a sample game (Around UNSW, c05x vs c05d) team A sits at headroom 0 in 237 of 400 rounds after r100, and at 1 in 39 more.
Headroom ≥ 2 happens only right after the team loses dragons, which on these maps means after a contact fight. So
"children born at the cap live longer" (unit 28) compares children born in calm stretches with children born just
after a death wave, near the enemy. The comparison is confounded by team state, and does not show that the cap slot
is special.

What still stands:

* Unit 25/27's E1/E1p cost on the open maps (measured directly, against C+D).
* Unit 29's cull-to-free refutation (measured directly). Its explanation ("selection, not scarcity") is withdrawn.
  The culled-slot children died young (24 rounds), but they too were born in the churn K creates.

# 3. Hypotheses

* **H-SZ57 → 0.2** (there is no evidence that slot allocation picks badly or well; the premise is gone).
* **H-SZ58** stands at 0.35 as a feature test, re-worded: at headroom 0–1, does "allied heads able to split" plus own
  visible food improve the split-label model? That is a learner question about label noise, not about value.
* **H-SZ59 (0.4, new) — headroom is a proxy for "just lost a fight".** For the Learner's features: team headroom
  (observable through `get_unit_count`) carries recent-loss information that the 7 × 7 view does not. Prediction: adding
  headroom to the R1/V or R2 feature set improves the value AUC at r100–r250 by ≥ +0.01 on class-B maps. Falsifier:
  gain < +0.005. Size: R4 ablation on existing rows. Suits Learner/Data.

**RL translation.** Observation: team unit headroom, a legal and cheap scalar that reads as "how many we just lost".
Precedent: unit counts are standard in Lux AI value features.

# 4. Process note

Since D-05x ("one path for the BOARD"), lanes append to the main checkout's BOARD.md and do not commit it on their branch.
I had been committing mine on `r/shenzhen`, so my 09:45–21:00Z lines were not on the main board. I appended them at
21:30Z, and `r/shenzhen` no longer carries BOARD.md changes.
