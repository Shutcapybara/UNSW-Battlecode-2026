---
id: shenzhen-unit29-cull-to-free-open-maps-and-p4-reading
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator screen (analysis copies only) + reading of the P-4 refutation (D-060 §B)
title: Unit 29 — cull-to-free (probe K) costs the open maps 15 % of total (Around UNSW −31 %). Freeing slots does not buy good children: under K, cap-born children live 24 rounds, not 51. P-4 reading — my unit-17 sim "strike" count pooled two event types
evidence: unswbc 1.2.9; `c05k` (carthage-05 + C + K + D) vs `c05d` (C + D); Around UNSW / Islands / Australia s1–3 both seats, 18 games; szheadroom.py on the K games; unit-17 replays re-cut by mover role (frame `mutual` flag)
---

# 1. Probe K on the open maps (H-SZ56)

| map | wins C+D–K | total C+D → K |
|---|---|---|
| Around UNSW | 4–2 | 1,374 → 948 (**−31 %**) |
| Islands | 4–2 | 713 → 638 (−11 %) |
| Australia | 3–3 | 834 → 899 (+8 %) |
| pooled | **11–7** | 2,921 → 2,485 (**−15 %**) |

The enemy's share of our corpse pearls falls (0.35 → 0.28; contact share 0.75 → 0.62), because culls happen away from
contact. The economy still shrinks. Children born at headroom 0–1 under K live a median **24** rounds (of 100) and eat 2.55
meals per 100 rounds, against 51 and 3.20 in the parent's games (unit 28). The slot K frees goes to a split decided under
churn, not to the well-fed parent that wins a slot after a natural death.

**H-SZ56 refuted (0.4 → 0.1).** The cap is not the open-map economy's binding constraint in a way a cull can unlock. Unit
28's "best children are born at the cap" is about which parent gets the slot, not about the slot being scarce. That
moves **H-SZ57 (slot claim by the best-placed dragon) up to 0.4**: it targets the selection, which is the part that matters.

# 2. Reading P-4 (D-060 §B: refuted, strike-hazard ratio 1.069 at m = 0)

My unit-17 prior said "m = 0 cut queen strikes 13 → 6". Re-cut by mover role (frame `mutual`: the dragon whose move
made the head-on), those 13 were **9 enemy strikes + 4 queen-initiated head-ons**, and the m = 0 arm had **5 + 1**. So
my count pooled the two event types that Asahi's frozen labeller separates. Asahi's panel finds the veto's effect is
on the queen-initiated deaths (225 → 53, all-cause hazard 0.703) with no strike change. My 9 → 5 enemy strikes at n = 18
is well within noise of no change. The panel result stands, and my prior overstated the strike effect. Lesson recorded: a
"strike" metric must condition on who moved.

# 3. Hypotheses

* **H-SZ56 refuted (→ 0.1).**
* **H-SZ57 → 0.4** (the selection of who splits into a freed slot is the lever, per units 28–29).
* **H-SZ58 (0.35, new) — the learned policy should see "who else can claim this slot".** For the R4 feature list: at
  headroom 0–1, the count of allied heads in view that could split this turn (length ≥ 4, not trapped), and own visible
  food. Prediction: in the store, the split-or-not label at headroom 0–1 is predicted better (AUC +0.02) with these two
  features than without. Falsifier: gain < +0.01. Size: R4 ablation on the existing BC data. Suits Learner/Data.

**RL translation.** Action label: split at headroom 0–1. Observation: own food in view, allied heads able to split.
Value: children born to well-placed parents at the cap are worth ~2× those born under churn (51 vs 24 rounds).
