---
id: shenzhen-unit33-headroom-robustness
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: log pass over existing simulator replays (no new games) — robustness of unit 31 (H-SZ59) and a new test (H-SZ62)
title: Unit 33 — with one row per game and a game bootstrap, the headroom signal survives at r300 (−0.0053 per slot, 95 % CI −0.0084 to −0.0023, negative in 14 / 14 leave-one-arm-out fits) but vanishes at r100 (+0.0006, CI ±0.007). Unit 31's r100 result is withdrawn. Headroom is not just "units lost in the last 20 rounds": both carry separate information at r300
evidence: tools/shenzhen/szheadboot.py and szdelta.py over 276 sim games (14 bot pairs of the carthage-05 family, units 15–29 arms; Around UNSW, Islands, Australia); team A seat only, so no symmetric duplicate rows; 2,000 game-level bootstrap resamples
---

# 1. Robustness of the headroom coefficient (H-SZ59)

Model: final total share of team A ~ length share at round k + headroom difference (A's free slots − B's).

| round | games | coefficient per free slot | 95 % CI (game bootstrap) | negative when one arm is left out |
|---|---|---|---|---|
| 100 | 276 | +0.0006 | −0.0071 to +0.0078 | 1 / 14 |
| 200 | 276 | −0.0030 | −0.0066 to +0.0009 | 14 / 14 |
| 300 | 276 | **−0.0053** | **−0.0084 to −0.0023** | 14 / 14 |

Unit 31 reported −0.011 per slot at r100 on 144 games with both seats as rows. That doubled every game and the effect
does not hold on the larger set. **I withdraw the r100 claim.** The r300 effect holds: one more free slot than the
opponent at r300 costs about half a point of final share, beyond what length share already says.

# 2. Level or recent change? (H-SZ62, new and tested here)

If headroom only meant "just lost a fight", the recent change in unit count should replace it. Recent change =
(own units at k − own units at k−20) − (the same for the opponent).

| round | R² length share | + headroom | + 20-round change | + both | corr(headroom, change) |
|---|---|---|---|---|---|
| 100 | 0.014 | 0.014 | 0.026 | 0.029 | −0.37 |
| 200 | 0.070 | 0.080 | 0.071 | 0.084 | 0.00 |
| 300 | 0.271 | **0.301** | 0.296 | **0.313** | −0.27 |

At r300 each adds about the same, and together they add more than either alone. The level is not reducible to the last
20 rounds' losses. It also carries older losses that were never refilled. **H-SZ62 (headroom = recent losses only):
refuted (0.3 → 0.1).** For the Learner, both scalars are legal: a dragon can read `get_unit_count` each turn and keep the
previous value.

# 3. Reading

* H-SZ59 stays at 0.5, but it is now a **late-game** feature in the sim. If the R4 ablation pools all rounds, the effect
  will be diluted. Read the AUC gain by round bucket.
* Caveats: one bot family, three open maps, one seat per game. These are sim checks only, and the live ablation decides.

# 4. Hypotheses

* **H-SZ59 → 0.5, scoped to r ≥ 250** (unit 33 bootstrap).
* **H-SZ62 refuted (→ 0.1)**: headroom ≠ the 20-round unit change; both carry information at r300.
* **H-SZ63 (0.45, new) — the headroom value gain is late-game.** In the R4 value ablation, the AUC gain from adding
  team headroom is < +0.003 at r100–150 and ≥ +0.01 at r250–350 on class-B maps. Falsifier: the early-bucket gain is ≥
  the late-bucket gain. Size: the R4 ablation split by round bucket, no new data. Suits Learner.
* **H-SZ64 (0.3, new, blue sky) — a dragon's own unit-count history is a usable "are we winning" signal.** Every dragon
  can read its team's unit count, so it can tell whether the team is winning without the radio. That makes a cheap
  trigger for switching roles (for example, gatherer to hunter when the team is ahead). Prediction: in ranked live games,
  a logistic of win on own-team-only unit features at r300 (level, 20-round and 100-round change) reaches AUC ≥ 0.62.
  Falsifier: AUC < 0.56. Size: one store query over about 2,000 ranked class-B games (unit counts per round are in the
  frames). Suits Data, then the Learner if it holds.

**RL translation.** Observation: own unit count and its 20-round change, both as scalars, weighted toward the late game
(or with round as an input). Value: headroom difference, late only. Do not expect an early-game gain.
