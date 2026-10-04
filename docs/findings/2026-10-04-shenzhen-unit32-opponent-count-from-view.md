---
id: shenzhen-unit32-opponent-count-from-view
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: log pass over existing simulator replays (no new games) — H-SZ60
title: Unit 32 — a single dragon's view says little about the opponent's unit count (ρ 0.19); the whole team's pooled view says a lot (ρ 0.83), but in self-play our own count already predicts theirs (ρ 0.87), so the sim cannot show what the pooled view adds live
evidence: tools/shenzhen/szoppcount.py over 30 sim games (units 18, 22, 23 arms; open maps), rounds 150..end step 10, both sides; single-dragon pass over 20 games (up to 8 dragons per side per round)
---

# 1. Result

| estimator of the opponent's unit count | rows | ρ with the true count |
|---|---|---|
| one dragon's 7 × 7 view (enemy heads within Chebyshev 3) | 11,172 | **0.19** (mean 0.56 heads seen) |
| union over all our dragons' views (as if fully shared) | 2,100 | 0.83 (within-game median 0.88) |
| our own unit count (no view at all) | 11,172 | **0.87** |

# 2. Reading

* One dragon's view barely tracks the opponent's size. That is the legal per-dragon observation, and its ρ of 0.19 sits
  between H-SZ60's falsifier (0.15) and its bar (0.3).
* The team-union estimate looks strong, but in self-play both teams move together, and our own count predicts
  theirs better (0.87) with no view at all. The sim cannot separate what the pooled view adds from the symmetry. Live
  opponents are not mirrors, so this number would not carry over.
* **H-SZ60 → 0.2.** A pooled estimate would need the radio, and its value can only be measured on live replays, where
  both counts are known and play is asymmetric. That is a store query for Data, not a sim question.
* Side lesson for any sim-based feature check: in self-play, team-level quantities on the two sides are strongly
  correlated, so a "predicts the opponent" result needs asymmetric games (mixed opponents) before it means anything.

# 3. Hypotheses

* **H-SZ60 → 0.2** (per-dragon signal weak; pooled signal unmeasurable in self-play).
* **H-SZ61 (0.35, new) — on live replays, the headroom difference matters more than own headroom.** Store test,
  ranked post-m2 class-B maps: logistic of win on (length share at r200, own headroom, opponent headroom). Prediction:
  opponent headroom carries a coefficient of similar size and opposite sign to own headroom (both "recent loss"
  signals). If it does, the opponent-count estimate is worth building. Falsifier: the opponent headroom coefficient is
  below half of own headroom's. Size: about 2,000 games. Suits Data/Learner.

**RL translation.** Observation: own headroom is cheap and legal. An opponent-size estimate needs pooled views over
the radio and is unproven. Leave it out of R4 until H-SZ61 says it pays.
