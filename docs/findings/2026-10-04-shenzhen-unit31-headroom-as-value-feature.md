---
id: shenzhen-unit31-headroom-as-value-feature
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: log pass over existing simulator replays (no new games) — a sim-side check of H-SZ59 for the Learner
title: Unit 31 — team unit headroom adds to length share in predicting the final total share (R² +0.045 / +0.018 / +0.057 at r100 / r200 / r300), with the sign of "just lost a fight": each extra free slot relative to the opponent costs ~0.4–1.1 points of final share
evidence: tools/shenzhen/szheadval.py over 144 simulator games (units 15–29 arms, carthage-05 family on both sides; Around UNSW, Islands, Australia); two symmetric rows per game (n = 288); OLS of final total share on (current length share, headroom difference = own free slots − opponent's)
---

# 1. Result

| round | rows | R² length share only | R² + headroom difference | coefficient per free slot |
|---|---|---|---|---|
| 100 | 288 | 0.010 | **0.055** | −0.0112 |
| 200 | 288 | 0.089 | 0.107 | −0.0042 |
| 300 | 288 | 0.323 | **0.380** | −0.0075 |

# 2. Reading

* Headroom carries information that length share does not, at every checkpoint. The sign is negative, so a team with more
  free slots than its opponent ends with less of the total. This matches unit 30: slack means recent losses, and recent
  losses predict the end beyond what current length shows.
* Caveats: self-play of one bot family, symmetric rows (effective n = 144 games), no game-clustered interval, and
  length share is a weak predictor at r100 in these sims (R² 0.01), so the relative gain there is inflated. This is a
  sim-side plausibility check, not the R4 ablation.
* **H-SZ59 → 0.5.** The live-data test stays with the Learner: add team headroom (legal: `get_unit_count`) to the V/R2
  feature set and read the AUC change at r100–r250 on class-B maps.

# 3. Hypotheses

* **H-SZ59 → 0.5** (sim support; live ablation pending).
* **H-SZ60 (0.35, new) — opponent headroom is partly observable, and worth estimating.** The opponent's unit count is
  not given, but visible enemy heads and the radio can bound it. Prediction: on class-B maps, the visible enemy-head count in
  a dragon's 7 × 7 view, averaged across our team's reports, correlates with the opponent's true unit count at
  r ≥ 150 (ρ ≥ 0.3 in sim). Falsifier: ρ < 0.15. Size: sim log pass. Suits this lane next unit; if it holds, the
  feature goes to the Learner.

**RL translation.** Observation: own unit headroom (scalar) now, and an estimated opponent unit count later. Value:
the headroom difference as a recent-loss signal. Precedent: unit counts are standard value-net inputs in Lux AI.
