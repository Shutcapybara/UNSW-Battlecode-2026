---
id: maelle-sf1-01
author: claude-opus-5.5/maelle (SF-1, desktop)
kind: lane report (SF-1 state and features), report 1 — Part 1 done, first five features
evidence: claude/maelle-status.md; game_stats/runs/maelle/*.json; build/maelle/{runs,tune,fit}/ (local); branch r/maelle
---

# Maelle report 1 — the state platform, and five fitted features on Ares

**Short version.** The platform exists and is exact: `maelle-02-features` adds per-dragon decayed grids and a
feature interface on both scoring sites, every weight runtime-overridable, and at zero weights it replays its
parent's transcripts with 0 divergent turns out of 61,667. Five features have been fitted on it (weights from
paired scans, priors from the corpus and from the bot's own decision dumps). **None passes D-032.** Three have a
zero-weight optimum (enemy target risk, death route cost, and — across seeds — food density); the L02 sparsity
selector loses from the opening; and one, the **ally-density crowding cost, is a real lever**: +0.04 to +0.05
units and length at r100 on both panels (pairs p < 0.001), every death rate down (off-pool self −27 %, ally-body
−37 %), economy flat — rejected because it gives the late economy back off-pool (gen p@250 −0.061, win −0.069).

## Part 1 — platform

| Version | What | Evidence |
|---|---|---|
| maelle-00-base | `lune-r1-07-latecap8x-only` verbatim | golden 0 / 38,429 turns divergent (4 maps × seat, seed 1) |
| maelle-01-nodevil | D-033: the three `W==32 && H==16` terms off | diverges only on the 32×16 maps (devil, portals) |
| maelle-02-features | `state.hpp` grids (food, ally, enemy, threat, death; seen age), scalars (sparsity, units in view, clock), target score × exp(Σ wt·f), move score + Σ wm·g, `MAELLE_PARAMS`, L02 cap-selector hook, `MAELLE_DUMP` | all weights 0: golden 0 / 61,667 vs maelle-01, dump on or off; each override bites |

Features are bounded in [0, 1] (box mean then B/(B + s)), so the target search's value-bound prune stays exact under
the feature factor (bound × exp(Σ max(0, wt))). CPU (sandbox pricing, 6 dense fixtures × both seats): parent max
8.72 M points/turn; every feature on at once 11.98 M; no errors.

## Fitting method

- **Priors.** `fit.py clogit`: 108 top-30 sides in the local 817-replay corpus, each dragon's grids rebuilt from its
  own 7×7 views; "which known pearl did it eat first" as a conditional logit; implied bot weight
  w = b·log 0.93 / b_steps. `fit.py selfplay`: the parent's own dumps (4.07 M chosen targets), Poisson on pearls over
  the next 20 rounds and logistic on death.
- **Fit.** `tune.py scan`: paired grid over the weight (value 0 = the parent arm), quadratic on the per-game
  objective J = econ + 0.5·mean(units, length)@100 − 0.08·ally head-on/1k, bootstrap interval of the argmax.
- **Gate.** D-032 in `lane.py score` (pool + gen, seeds 1–3, paired bootstrap lower bounds).
- **Method lesson (feature 1).** A single-seed (160-fixture) scan cannot see +0.03: maelle-03's seed-1 plateau
  (dJ +0.03..+0.05) was noise; across seeds its economy was +0.005 / −0.019 / −0.083. Scans since use seeds 1+2.

## Results

| # | Feature (consumer) | Ledger | Prior | Fitted weight [90 %] | Gate / outcome |
|---|---|---|---|---|---|
| 1 | `food_free` = food·(1 − ally) on bed/unseen targets | L12 | self-play: food pays pearls (+1.75) and deaths (+2.42) | −1.3 [−1.90, −1.00] (seed 1) | **REJECT**: pool Δecon~ −0.030 [−0.057, 0.000], gen −0.019; w > 0 loses steeply (+1.5: −0.17) |
| 2 | `ally` crowding cost on targets | L12 / S-1 | corpus winners −0.067; self-play pearls −0.42 | **−1.41 [−1.55, −1.25]** | **REJECT**: pool Δecon~ −0.012 [−0.037, +0.011] (mean form +0.025 [−0.002, +0.051]); gen −0.021; units/length@100 +0.043/+0.044 pool, +0.052/+0.053 gen; gen p@250 −0.061, win −0.069 |
| 2b | ally × clock (fade the cost late), on #2 | L03 | — | no optimum (convex; +2.8: econ +0.016, win −0.011) | not gated |
| 3 | `enemy` risk cost on targets | L12 / S-1 | corpus −0.025; self-play pearls −0.19 | ≈ 0 (−0.02 [−0.53, +0.50]) | zero-weight optimum; −1.5: econ −0.054, win −0.086 |
| 4 | `death` cost on moves | L12 | corpus +0.016 (corpse food) | ≈ 0 (flat inside ±0.75) | zero-weight optimum; −2: p@250 −0.082 |
| 5 | L02 cap = 48 + (hi − 48)·sparsity, no round threshold | L02 | R-1: late cap pays, early wide hurts | loses at hi = 160, 384, 768 | econ −0.020..−0.031 from the opening (p@50 −0.014..−0.019) |

## What to read from it

- **The sign of "go where the food is" is negative on this parent.** Sciel-03a's +0.067 does not reproduce as a
  feature on the nodevil, late-cap host. The self-play fit says why: food-dense targets pay in pearls and in deaths
  in about equal measure (the churn trade, L29). Steering exploration toward them buys churn; away from them buys
  nothing across seeds.
- **Crowding is the live lever, and it is phase-shaped.** Pricing ally density on targets spreads the swarm: more
  units and length, the largest hygiene gain the programme has recorded on Ares, flat early economy — and a late,
  off-pool economy loss. A clock fade does not fix it, so the late cost is probably map-structural (concentrated late
  food) rather than a round effect. This is the first feature worth stacking with something that restores late
  economy.
- **The pearl-scoped risk features are already priced.** Enemy density and deaths add nothing the bot's enemy target
  discount and threat cost do not already carry: zero-weight optima, as the corpus priors' small size predicted.
- **The gate's economy statistic matters at this effect size.** For maelle-04 the median form (econ~, D-032) and the
  per-game-mean form disagree in sign on the pool (−0.012 vs +0.025). Material-shifting mechanisms move the
  distribution's shape; the director may want the mean form reported beside econ~ in D-032 (both are in the JSON).
- **Corpus priors are small in bot units** (|w| < 0.1 for every feature): top sides are distance-dominated
  (−1.24 per step). Useful for signs, not for magnitudes.

## In progress

Joint re-tune (SPSA over wt_ally, wt_food_free, wt_ally_clock, wt_enemy from ally −1.4; pool + gen, seeds 1–3,
12 × 96 games) on `maelle-05-joint`; the L02 variant with the opening floor kept (capsel_lo = 160). Remaining
single features: threat (move cost; self-play death prior +0.85), clock terms, momentum (L13). Part 3 (learned
scorer) waits for three accepted features, per the prompt; none yet.

## Ledger rows touched (proposed weights)

| Row | Current | Proposed | Why |
|---|---|---|---|
| L12 | 0.7 | **0.6** | two rejections on the right host (food_free, ally crowding) plus two zero-weight optima (enemy, death); kept above 0.5 because ally crowding moves material and hygiene strongly — the density idea is live, the food half is not |
| L02 | 0.7 | **0.6** | a pure sparsity selector loses to the round schedule from the opening; the floor-kept variant is running |
| L03 | 0.7 | 0.7 | ally × clock is a weak test (two points, no optimum); not moved |
| L27 | 0.5 | 0.5 | the corpus → state → conditional-logit pipeline exists and runs in minutes; its priors had the right signs (ally, enemy) but small magnitudes; no C++ decision measured from it yet |
| L29 | 0.8 | 0.8 | confirmed indirectly: food-seeking features trade pearls for deaths one for one |

Proposed next weights: `wt_ally −1.4` held for stacking with a late-economy restorer; every other feature at 0.
