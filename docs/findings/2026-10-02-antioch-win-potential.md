---
id: antioch-win-potential
author: antioch (P2-A Claude analyst)
kind: target + method
question: A shaped-reward and early-game benchmark that is more robust and better evidenced than the tempo metric — what should it be, and how well does it predict winning under the 1.2.3 rules?
evidence: s1 corpus store, ten ladder maps; post-change 2,433 games with checkpoints (1 Oct 09:23Z – 15:40Z), pre-change 39,110 games; server results as labels
queries: tools/antioch/value_target.py fit (leave-one-map-out); coefficients tools/antioch/phi_post_v1.json
---

## Answer

**Φ, a win-probability potential.** At each checkpoint (r10, 25, 50, 100, 150, 250, 400; linear between them):

```
Φ = σ( Σ β_k(regime, round) · (x_k − 0.5) )
```

- The **x** are five **opponent-relative shares**:
  - total length;
  - longest, as (L − L_opp) / max / 2 + ½;
  - pearls eaten;
  - BFS territory;
  - deaths.
- **No map identity, no team, no seat.** The β come in two regimes: elimination maps and round-limit maps.
- **Symmetric:** Φ(us) = 1 − Φ(them), and the field mean is ½.
- **As a shaped reward,** use potential-based shaping, F = γ·Φ(s′) − Φ(s). This form provably leaves the optimal policy
  unchanged (Ng, Harada & Russell 1999), so a wrong Φ only slows learning; it cannot change what is optimal.
- **As a benchmark,** report a panel's mean Φ@25/50/100/150 against the targets below.

## Evidence

**Out of sample by map.** Fit on nine ladder maps, score the tenth. This is the D-033 out-of-sample rule.

| post-change, LOMO AUC | r10 | r25 | r50 | r100 | r150 | r250 | r400 |
|---|---|---|---|---|---|---|---|
| Φ, elimination maps (6) | 0.61 | 0.78 | **0.86** | **0.93** | 0.96 | 0.97 | 0.99 |
| Φ, round-limit maps (4) | 0.48 | 0.59 | **0.63** | **0.68** | 0.70 | 0.74 | 0.84 |
| Φ pooled, one regime | 0.58 | 0.70 | 0.77 | 0.85 | 0.88 | 0.90 | 0.95 |
| total length share alone | 0.57 | 0.69 | 0.77 | 0.84 | 0.88 | 0.91 | 0.91 |
| own income only (the tempo family: opponent-blind, ÷ map median) | 0.51 | 0.59 | 0.64 | 0.67 | 0.70 | 0.72 | 0.72 |

- **Calibration is right only when the regimes are split.**
  - Regime-split LOMO calibration slopes are 0.97–1.14 from r25 on, where 1.0 is perfect.
  - A pooled Φ is miscalibrated per map: slopes 0.3 on Portals, 2.1 on Trophy.
- **The opponent-blind form is the weak link.** "Own income only" carries the same information as tempo. Its calibration
  slopes are 0.4–0.8, and its AUC trails Φ by 0.13–0.18 from r50 on. The result says *how* to improve on tempo: measure
  the state **relative to the opponent**, not against a fixed reference curve.
- **Robust across the rule change.**
  - A Φ fitted on pre-change games scores post-change games as well as a post-fitted one: AUC 0.777 vs 0.772 at r50.
    The ranking transfers.
  - Its calibration slope drops to 0.85–0.94, so refit β per era.
  - Coefficient drift between eras: early units weight falls (4.3 → 1.1 at r10); late longest weight stays large (4.5 at
    r400 in both).
- **Units share can be dropped at no cost** (AUC identical to three decimals). Units are the term an RL agent could
  inflate by splitting into dust (L29: `pearls@k` rewards churn), so Φ leaves them out.
- **Where Φ is weak: round-limit maps before r250.**
  - On Portals, Trauma, Slithery and Schooltime, early material decides little. Those games are decided late by longest
    and, now, the queen.
  - On those maps a shaped reward from early state will be noisy. The terminal win must dominate, and the queen term
    should be added.
- **The queen term.**
  - Adding queen-alive difference does not move AUC today (both queens are dead in most games).
  - Where it varies, its r400 coefficient is 2.8, comparable to longest.
  - Carry it in Φ from r250 on (`queen_diff`, coefficient to be refitted as queen-keeping spreads). This ties the shaped
    reward to H-Q1.

## Targets (post-change; Φ of the cohort, field = 0.5)

| regime | metric | r25 | r50 | r100 | r150 |
|---|---|---|---|---|---|
| elimination maps | top-10 mean Φ (median) | 0.569 (0.575) | **0.632 (0.684)** | **0.698 (0.847)** | 0.731 (0.932) |
| round-limit maps | top-10 mean Φ (median) | 0.523 | **0.546** | **0.570** | 0.590 |
| both | r11–30 mean Φ, elimination / round-limit | 0.553 / 0.509 | 0.580 / 0.522 | 0.606 / 0.535 | 0.614 / 0.551 |

These are in-sample means of the deployed coefficients over 2,433 games (465 / 377 top-ten side-games). Team 7 has no
post-change games. For our bot, score a tester's panel replays: Φ needs only the s1 series columns, and panel opponents
are not the field, so compare arms on the same fixtures.

## Hypothesis H-V1 (for testers and the learned track)

**Claim:** Φ is a better early-game gate guard and RL shaping signal than tempo.
- **Gate falsifier:** across the carthage and kyoto arms already run, ΔΦ@100 on the pool does not rank the arms' paired
  win changes better than Δtempo or Δeconomy (Spearman over arms).
- **RL falsifier (H-RL3):** a PPO run with Φ shaping does not reach the unshaped run's win rate in fewer samples.
- **Size:** the gate check is offline, on existing panels (cheap); the RL check is one pair of runs.

## Limits

- Six hours of post-change play (2,433 games). Refit β weekly as the field adapts; refit sooner if queen-keeping spreads.
- Opponent strength is not controlled: Φ predicts the result against whoever was played.
- Territory is sampled every 5 rounds; at r10 and r25 it carries the r10 / r25 sample.
