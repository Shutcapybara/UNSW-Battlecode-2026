# SF-1 `maelle` status — Maelle lineage (Claude Opus 5.5, desktop)

State-and-features lane on Ares (prompt: SF-1). Branch `r/maelle`, worktree `../wt-maelle`, bots
`bots/maelle-<nn>-<slug>/`, tools `tools/maelle/`. Unit of experiment: one state variable plus its consumer, with
the weight fitted (`tools/maelle/fit.py` prior, `tools/maelle/tune.py` paired scan / SPSA), gated by D-032
(`tools/maelle/lane.py score`).

## Part 1 — platform

| Version | What | Evidence |
|---|---|---|
| maelle-00-base | `lune-r1-07-latecap8x-only` verbatim | golden: 38,429 turns / 1,130 dragons (schooltime A, portals B, trauma B, devil A; seed 1 vs yuna-v05-core), **0 divergent** |
| maelle-01-nodevil | D-033: `Params::map_identity_terms = false` (the three `W==32 && H==16` terms return 0) | golden vs lune-r1-07: schooltime/trauma 0 divergent; devil 335/5,731 and portals 709/9,641 divergent (both 32×16 — the terms firing, as intended) |
| maelle-02-features | `state.hpp` grids + scalars, feature interface on target and move scores, `MAELLE_PARAMS` runtime weights, L02 cap selector hook, `MAELLE_DUMP` decision dump | all weights 0: golden vs maelle-01, 61,667 turns / 1,247 dragons (+ big_empty B), **0 divergent**; dump on: 0 divergent; `wt_food=0.5`, `wm_ally=-1`, `capsel=1` each diverge (overrides bite) |

Feature scales (s in B/(B+s)) frozen from the first dumps (trauma B + schooltime A, 22k target decisions): nonzero
medians food 0.44, ally 0.21, enemy 0.20, threat 0.41, death 0.64 (3 % of candidates) — all inside (0, 1).

Parent arm for every Part 2 measurement: `maelle-02-features` with no overrides (= maelle-01 behaviour), pool +
gen, seeds 1–3, run with the decision dump (the training data for `fit.py selfplay`).

## CPU (sandbox judge pricing, 6 dense fixtures × both seats vs ares-v06)

| Build | p50 range | Max turn | Worst | Errors |
|---|---|---:|---|---:|
| maelle-01-nodevil (parent) | 4.50–5.18 M | 8.72 M | schooltime B | 0 |
| maelle-02 all-on probe (every `wt_*` = 0.3, move `wm_*` ±0.5, capsel 48→512) | 5.32–7.26 M | **11.98 M** | schooltime B | 0 |

The worst case of the whole feature set is under the 20 M lane ceiling; per-version probes still run for any
version that adds a grid.

## Host note

The desktop is shared with lanes hb1, rb, rc (load average 97–130 on 16 cores on 30 Sep morning): measured
85–240 s per heavy-map game, far below the 2,900 games/h figure; budgets below are sized for that.

## Part 2 — features (running table)

| Version | Feature | Ledger row | Fitted weight [interval] | Surface | Pool Δecon~ [90 %] | Gen Δecon~ [90 %] | Per-checkpoint | CPU max | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| maelle-03-foodfree | food_free = food_ew × (1 − ally_ew) on bed/unseen targets | L12 | −1.3 [−1.90, −1.00] (pool s1 scan) | plateau −2..−0.5 (dJ +0.03..+0.05 on seed 1), steep loss for w > 0 | −0.030 [−0.057, +0.000] | −0.019 [−0.041, +0.003] | pool p50 −0.061, p100 −0.041, p150 −0.001, p250 −0.015; gen p150 −0.045, p250 −0.033 | < 11.98 M (all-on probe) | **REJECT** (pool econ lb ≤ 0; units lb −0.040; pool win lb −0.050; gen econ lb −0.041; gen win −0.044) |
| maelle-04-allycrowd | ally_ew crowding cost on targets | L12 (S-1) | −1.4 [−1.55, −1.25] (pool s1+2 scan) | interior optimum; material/hygiene rise to −1.5, economy peaks −1..−1.5, −3 under-eats | −0.012 [−0.037, +0.011] (mean form +0.025 [−0.002, +0.051]) | −0.021 [−0.041, +0.007] | pool flat at every checkpoint; gen p50 0.000, p100 +0.002, p150 −0.025, **p250 −0.061** | < 11.98 M (all-on probe) | **REJECT** (pool econ lb ≤ 0; pool win lb −0.021; gen econ lb −0.041; gen win −0.069) — units/length@100 +0.04..+0.05 on both panels, every death rate down (gen self −27 %, ally-body −37 %) |

## Priors (fit.py, corpus, 30 Sep)

Conditional logit over "which known pearl a top-30 dragon ate first" (candidates: pearls it knows within BFS 20;
features rebuilt from its own 7×7 views with state.hpp's rules; controls: steps, visible, ally/enemy head nearer).
Implied bot weight w = b · log(0.93) / b_steps (bootstrap by game, 90 %). Pearl targets only — says nothing about
bed/unseen targets (`food_free`'s scope).

| Feature | top-30 sides (106 games, 107,939 decisions) | winning top-30 sides (56 games, 74,526) |
|---|---|---|
| steps (b) | −1.24 [−1.30, −1.15] | −1.29 [−1.35, −1.20] |
| food | −0.082 [−0.170, +0.022] | −0.087 [−0.163, +0.011] |
| ally | −0.061 [−0.143, +0.016] | **−0.067 [−0.175, −0.006]** |
| enemy | **−0.025 [−0.033, −0.018]** | **−0.027 [−0.036, −0.016]** |
| threat | +0.008 [−0.005, +0.031] | +0.006 [−0.004, +0.030] |
| death | +0.006 [−0.004, +0.014] | **+0.016 [+0.005, +0.023]** |
| food·ally | +0.040 [−0.042, +0.126] | +0.044 [−0.027, +0.153] |

Reading: top sides are distance-dominated; conditional on distance they shade away from ally- and enemy-dense
pearls (the crowding / risk costs have the expected sign) and slightly toward death cells (corpse food). All
implied weights are small in bot units (|w| < 0.1), so the scans centre near zero for pearl-scoped features.

## Feature 1 — `food_free` (L12; maelle-03-foodfree), scan in progress

Feature: food_ew box mean on bed/unseen target candidates × (1 − ally_ew), log-linear on the target value.
Expected sign before the run: positive (Sciel-03a +0.067 econ with a positive food weight), with ally head-on not
rising. Scan 1, pool seed 1, 160 paired fixtures per value vs maelle-02 (w = 0):

| w | dJ | d econ | d p50 | d p100 | d p150 | d p250 | d units@100 | d length@100 | d win | d ally h2h /1k |
|---|---|---|---|---|---|---|---|---|---|---|
| −0.5 | +0.030 | +0.023 | −0.003 | +0.008 | +0.026 | +0.059 | +0.001 | +0.009 | +0.031 | −0.06 |
| +0.75 | −0.092 | −0.070 | −0.109 | −0.067 | −0.040 | −0.065 | −0.061 | −0.070 | 0.000 | −0.14 |
| +1.5 | −0.225 | −0.172 | −0.176 | −0.191 | −0.158 | −0.165 | −0.140 | −0.158 | −0.050 | −0.27 |

The expected sign was wrong: on this parent, pulling exploration toward food-dense uncrowded beds/unseen cells costs
economy monotonically; the optimum is at the negative edge of the range. Extended:

| w | dJ | d econ | d p50 | d p100 | d p150 | d p250 | d units@100 | d length@100 | d win | d ally h2h /1k |
|---|---|---|---|---|---|---|---|---|---|---|
| −2.0 | +0.040 | +0.011 | +0.029 | +0.010 | +0.012 | −0.007 | +0.040 | +0.041 | +0.038 | −0.11 |
| −1.0 | +0.048 | +0.017 | +0.013 | +0.040 | +0.022 | −0.007 | +0.041 | +0.043 | 0.000 | −0.12 |

Surface: quadratic dJ = −0.035 w² − 0.092 w; argmax **−1.3, bootstrap 90 % [−1.90, −1.00]** — a plateau from
−2 to −0.5 (dJ +0.03..+0.05), steep loss for w > 0. The gain is material and hygiene (units/length +0.04, ally
head-on down), not churn. Compiled into `maelle-03-foodfree` (wt_food_free = −1.3); D-032 gate running (pool + gen,
seeds 1–3, vs maelle-02-features w = 0).

## Priors (fit.py selfplay, parent maelle-02 pool dumps, seeds 1–3)

Chosen target's features vs its outcome over the next 20 rounds; 4,071,445 decisions; controls: base log-score,
steps, target type; bootstrap by game (30), 90 %. Off-policy and confounded — a sign prior, not a weight.

| Feature | pearls eaten (Poisson, log-rate) | died (logistic) |
|---|---|---|
| food | +1.75 [+1.66, +1.84] | +2.42 [+2.36, +2.49] |
| food_unseen | −0.81 [−0.89, −0.74] | −1.27 [−1.34, −1.18] |
| food_free | −0.02 [−0.08, +0.06] | +0.11 [+0.05, +0.16] |
| ally | **−0.42 [−0.46, −0.39]** | +0.01 [−0.03, +0.04] |
| enemy | −0.19 [−0.24, −0.14] | −0.01 [−0.07, +0.07] |
| threat | −0.00 [−0.05, +0.03] | **+0.85 [+0.81, +0.90]** |
| death | −0.01 [−0.04, +0.03] | −0.01 [−0.04, +0.01] |
| age | −0.32 [−0.37, −0.29] | +0.40 [+0.35, +0.49] |

Reading: food-dense targets pay in pearls and cost in deaths (the churn trade, L29) — consistent with the negative
food_free optimum; crowded targets pay less (supports a negative wt_ally); threat is the death signal (for the move
consumer, wm_threat).

## Feature 2 — `ally` crowding cost on targets (L12/S-1; wt_ally), scan on the maelle-03 base

Pre-registered sign: negative (corpus winners −0.067; self-play pearls −0.42). Pool seed 1, 160 paired fixtures
vs maelle-03-foodfree (wt_ally = 0):

| w | dJ | d econ | d p50 | d p100 | d p150 | d p250 | d units@100 | d length@100 | d win | d ally h2h /1k |
|---|---|---|---|---|---|---|---|---|---|---|
| −1.5 | **+0.130** | **+0.067** | −0.023 | +0.068 | +0.097 | +0.124 | +0.116 | +0.113 | +0.044 | −0.08 |
| −0.5 | +0.068 | +0.046 | −0.005 | +0.039 | +0.064 | +0.084 | +0.066 | +0.049 | +0.053 | +0.08 |
| +0.5 | −0.012 | +0.016 | −0.020 | +0.010 | +0.012 | +0.062 | −0.010 | −0.045 | −0.063 | +0.18 |

Monotone, optimum at the edge (−1.5); extending to −3, −5. Largest effect in the lane so far, with material and
win rate rising with the economy.

### maelle-03 verdict (D-032, seeds 1–3, 480 pool + 744 gen paired fixtures): REJECT

Per seed (pool, per-game-mean econ): s1 +0.005, s2 −0.019, s3 −0.083. The seed-1 scan's plateau was inside
single-seed noise (and J's gain was mostly the material terms, which did not hold: units@100 +0.003, length +0.013).
Surface kept: the weight's sign is not positive on this parent (w > 0 loses steeply on seed 1) and its negative
optimum does not pay across seeds — **a zero-weight optimum for food_free**. Method change from here: scans use
pool seeds 1+2 (320 paired fixtures per value; the parent already has seeds 1–3).

Feature 2's scan was run on the maelle-03 base (−1.5: dJ +0.130, econ +0.067, units +0.116); with 03 rejected
it is being re-run on the parent (maelle-02, w = 0), values −3, −1.5, −0.5, seeds 1+2.

### Feature 2 on the parent (pool seeds 1+2, 320 paired fixtures per value vs maelle-02 w = 0)

| w | dJ | d econ | d p50 | d p100 | d p150 | d p250 | d units@100 | d length@100 | d win | d ally h2h /1k |
|---|---|---|---|---|---|---|---|---|---|---|
| −3.0 | −0.047 | −0.112 | −0.068 | −0.071 | −0.113 | −0.195 | +0.060 | +0.071 | −0.084 | −0.39 |
| −1.5 | **+0.126** | +0.030 | +0.014 | +0.063 | +0.041 | +0.002 | **+0.141** | **+0.146** | −0.009 | −0.31 |
| −0.5 | +0.036 | +0.015 | +0.014 | +0.014 | +0.021 | +0.012 | +0.030 | +0.038 | +0.011 | −0.05 |

Surface: dJ = −0.063 w² − 0.179 w; interior argmax **−1.41, 90 % [−1.55, −1.25]**. Economy peaks near −1 to
−1.5 (+0.03); material and ally head-on improve strongly to −1.5; beyond that the swarm under-eats (−3: econ
−0.11). Compiled into `maelle-04-allycrowd` (wt_ally = −1.4, parent maelle-02); D-032 gate running.

### maelle-04 verdict (D-032, seeds 1–3): REJECT, with a phase signature

The crowding cost buys material (units/length@100 +0.04..+0.05, pairs p < 0.001 on both panels) and the largest
hygiene gain in the lane (gen self −27 %, ally-body −37 %, wall −11 %), with economy flat early and **late economy
lost off-pool** (gen p@250 −0.061 [−0.090, −0.026], gen win −0.069). Per-seed pool mean-form econ +0.060 / +0.013 /
+0.002; gen econ~ +0.000 / +0.018 / −0.046. Reading (L03): spreading pays in the opening and midgame and costs late,
when food is scarce and concentrated. Next: the clock interaction on the same feature — target term
ally·(wt_ally + wt_ally_clock·round/500) — scanned on top of maelle-04 over pool + gen, seeds 1+2.

### Feature 2b — clock interaction on the crowding cost (wt_ally_clock on maelle-04; pool + gen, seeds 1+2, 816 paired)

| w | dJ | d econ | d p50 | d p100 | d p150 | d p250 | d units@100 | d length@100 | d win | d ally h2h /1k |
|---|---|---|---|---|---|---|---|---|---|---|
| +1.4 | −0.049 | −0.013 | −0.003 | −0.010 | −0.023 | −0.015 | −0.052 | −0.058 | −0.015 | +0.11 |
| +2.8 | +0.016 | +0.016 | +0.008 | +0.013 | +0.009 | +0.036 | +0.003 | +0.004 | −0.011 | +0.03 |

Not monotone, convex fit, both points near noise: fading the crowding cost with the clock does not repair
maelle-04's late loss (win stays negative). Not gated. L03 is not supported for this feature; the late cost is
likely map-dependent rather than a clock effect.
