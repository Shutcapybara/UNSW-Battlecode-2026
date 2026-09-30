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
