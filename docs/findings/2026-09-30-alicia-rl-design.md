# RL-1 (Alicia) — learning-driven training on Ares: design memo

**Date:** 2026-09-30 · **Author:** Claude Opus 5.5 (lineage **Alicia**, branch `r/alicia`) · **Status:** §0 decided and
sent; the director may redirect within a day. The infrastructure (§1) is lineage-agnostic and is built while that
window is open. Training starts on the decisions below.

## §0 — Decisions

### 0.0 Base, and what was not there

- **Base (D-033).** `alicia-01-nodevil` is `lune-r1-07-latecap8x-only` with the three `W==32 && H==16` terms switched
  off (`Params::shape_terms = false`, the Renoir-23 patch). Every delta in this lane is measured against it.
- **SF-1 has not landed.** There is no `claude/*sf*-status.md`, no `2026-09-30-SF1-state-and-features.md` prompt and
  no `<lineage>-02-features` bot on origin or on any local branch. The runtime parameter override "already specified
  in SF-1/R-5" also does not exist; R-5's worktree is empty.
  - So this lane builds the smallest interface that layer (a) needs: `alicia-02-tunable` (below).
  - It is written so that SF-1 can adopt it or replace it. Its status file says so.
  - No state module or candidate dump is built here; that is SF-1's job, and layer (b) waits for it.
- **C1-E's structure-keyed targets were never delivered.** `C1-pace-targets.md` and `C1-efficiency-ledger.md` are
  per-map cohort tables with no fitted formula. `maps/new/manifest.json` carries structure features for the 20 new
  maps only, and the tool that produced them (`tools/map_discovery/coverage.py`) is not in the tree. This decides
  §0.2's off-pool question: see there.
- **`docs/BASELINES-2026-09-30.md` does not exist** on any branch. The baselines used here are the lanes' own
  findings (R-1, `ra`, D-032/D-033).

### 0.1 Execution layer: (a) parameters now, (b) scorer only if (a) shows the surface is not flat

**Decision: (a).** The policy is a vector of 24 evaluation weights and search caps. It is trained by antithetic
evolution strategies on paired fixtures. The trained vector ships as `params.hpp` defaults.

| Layer | What it controls | Ceiling | Cost per training step | C++ to build | Status here |
|---|---|---|---|---|---|
| (a) parameters | 24 of V06's ~90 hand-set weights and caps, jointly | the best point of Ares's own evaluation surface: `ra` measured single knobs at +0.01–0.02 econ, 3–5× short of the gate; joint moves are untested (L04, L20) | one generation = 18 policies × 20 fixtures = 360 games ≈ 8 min at 2,900 games/h (≈ 15–20 min on today's shared host, load 90+) | a runtime override of `Params` (done: `alicia-02-tunable`, golden parity 0/30,558) | **start here** |
| (b) scorer | the choice among the target BFS's candidate targets (or the move candidates), ≤ 4k weights | the decisions V06's hand ranking gets wrong, still inside its candidate set | offline epochs are seconds; data is 1 game per ~1,000 logged decisions | the SF-1 candidate/feature/choice dump, a header-only scorer with a 20-line forward pass, a `POLICY_FILE` loader, softmax-temperature sampling, and golden parity with the net off | after (a), and only if (a) moves the curve (L16 trigger) |
| (c) full action policy | every move, imitation-pretrained on the top-30 corpus, then RL | highest in principle | imitation is cheap; RL on-policy in C++ is the full cost of (b) × horizon | a whole policy in C++ | not in this lane |

Why (a) first, and why not (c):

- **(c) has failed three times for reasons that still hold (L27).** `ouroboros-m01` was capped by its teacher.
  Loki's ranker did not transfer across hosts. `rl_earlygame.py` was a Python whole-policy opening component under
  the CPU wall, trained on one mid-field team, and never reached a panel.
  - Ares already sits at the top-ten level on the pool (R-1: p@100 0.94–1.03 of the top-ten median, field percentile
    0.55–0.60). An imitation start from the top-30 would begin *below* the base.
- **(a) is the only layer whose output can pass the gate this week.** There is no model in the bot and nothing to
  export but numbers. CPU is unchanged except where a search cap moves, and the probe covers that.
  - Its evidence is also the trigger L16 names: if the tuned vector beats hand weights, L16 → 0.6 and (b) is designed
    on the parameters that moved. If the surface is flat, L16 → 0.3.
- **Why ES, not SPSA or CMA-ES.**
  - Antithetic pairs (θ+σε, θ−σε) on common fixtures give one paired difference per direction. That is the lane
    rule's "never compare across seeds" built into the estimator.
  - Rank shaping makes it robust to the heavy-tailed per-game reward (eliminations).
  - SPSA is the special case with one pair per step; with 16 cores busy, 8 pairs per step uses the parallelism.
  - CMA-ES's covariance needs more samples per generation than a 360-game budget gives at 24 dimensions under
    this noise.
  - `pycma` is not installed in the shared venv, and the lane does not modify the shared environment.
- **Parameterisation.**
  - Each weight moves multiplicatively, θᵢ = θᵢ⁰·exp(uᵢ), with u bounded to |uᵢ| ≤ 1.2 (×0.3 to ×3.3). Scale-free
    weights then take equal steps.
  - Three weights are reparameterised so the step is meaningful: `target_gamma` through the horizon 1/(1−γ);
    `target_hysteresis` through its excess over 1; the discounts are clipped to ≤ 1.
  - Integer caps are rounded.
  - σ = 0.20 in u, the Adam step is 0.05, and there are 8 antithetic pairs per generation. The centre and the parent
    are evaluated on the same fixtures every generation for the learning curve.

The 24 dimensions are the target values (pearl, memory, bed, unseen, dive, horizon γ), target competition (own and
enemy discount, hysteresis, momentum, visit, goal), movement costs (sprint, crowd, trap, threat, bed-block, flank),
swarm density (ally, enemy), split and material value, and three search caps (opening, born, late). They are the
knobs with a measured non-zero slope in `ra` (threat, revisit, trap, unseen) plus the untested ones that the same
scorer reads.

The following are left out:

- Anything map-keyed: none remain after D-033.
- The escape block: its weights belong to R-3.
- Pure horizon limits whose effect R-1 already measured.

### 0.2 Reward: the curve term first, guards inside it, outcome on a schedule

For one side-game on map m, from the replay, by `tools.analysis.features` (the extractor BENCHMARKS uses):

**Curve term.** For each statistic s, pct_s is the side-game's mid-rank percentile among field sides on map m
(`field_distributions.json`, ties counted half):

 C = ½·mean(pct_p@50, pct_p@100, pct_p@150, pct_p@250) + ¼·pct_units@100 + ¼·pct_total@100

- **Percentile, not ratio to the top-ten median.** BENCHMARKS measures the percentile as the form that strips the
  most map and needs the fewest games (pearls@100: map share 0.22 vs 0.30, ~44 vs ~47 side-games). It is bounded, so
  one elimination or one runaway map cannot dominate a generation's gradient.
  - The top-ten curve enters as the *target level*: on the pool the top ten sit at percentiles 0.58–0.64 on these
    statistics.
  - A hinge at the top-ten level would have zero gradient on the pool, where the base is already there. The
    continuous percentile keeps pushing.
- **Units and length at r100 carry half the curve (L29).**
  - 38 % of what the base eats is ally corpses. A policy rewarded on pearls alone learns churn, as Renoir's 07a/07c
    did (+0.11 econ with ally head-on +51 % and units@100 down).
  - Giving units@100 and total@100 the same total weight as the four economy checkpoints makes feeding the swarm to
    itself cost reward directly.
  - Births@100 is reported but **not rewarded**. It rises under splitting-into-dust, which is exactly the churn
    failure BENCHMARKS warns about.
- **Early concentration** (`top1_share@100`) has no field distribution; it is reported, not rewarded.

**Guards: hinge penalties, computed per policy over its generation's fixtures, not per game.** The rates are counts
over dragon-turns, and per-game rates are too noisy.

 P = Σ_g max(0, rate_g / rate_g^parent − 1.10) for g ∈ {avoidable = wall + self + ally body + ally head-on;
 ally churn = ally body + ally head-on (L29); newborn deaths within 10 turns per 100 births}

- Training uses pooled groups, not the four rates separately. One generation's ~20 games give a policy only tens of
  deaths per cause, so a per-rate count carries about 15 % Poisson noise, and a +10 % hinge on each rate would fire on
  noise. The D-032 gate still checks every rate on its own.
- The parent's rates are measured on the same fixtures in the same generation.
- A 10 % excess is free, which is D-032's tier-2 bound. Beyond it, +20 % on one rate costs 0.10 of reward, the size of
  a whole percentile decile on the curve.
- The newborn-death rate is the churn guard BENCHMARKS names for splitting-into-dust.

**Terminal term.** T = ½·win + ½·total_share@250, where win is 1, ½ or 0 and total_share@250 is the length share at
r250 (log-odds 2.2 zoo / 2.4 field, the strongest single outcome proxy).

**Reward and schedule.** Per policy, R = mean over fixtures of [(1−β)·C + β·T] − P.

| Stage | β | Maps in training |
|---|---|---|
| 1 | 0 (curve only) | pool |
| 2 | 0 | pool + held-in off-pool maps |
| 3 | 0.25 for the first half of the stage, then 0.5 | pool + held-in |
| 4 | 0.5 | league, only if 1–3 produced a gate-passing policy |

**Off-pool maps: the base's own per-map numbers, on the pooled field scale.** C1-E's structure targets do not exist
(§0.0), and fitting structure → median on ten pool maps would be a ten-point regression that learns the pool. So for
a map without field references:

- m̂_s(map) = median_s^base(map) / ρ_s, where ρ_s is the base's pool-median ratio to the field median.
- pct_s = F_s(x / m̂_s(map)), where F_s is the pooled distribution of x / field-median over the pool maps.

This assumes the base sits at the same field-relative level off-pool as on the pool. It is a floor, and it is
optimistic: the base is weaker off-pool, 0.524 vs 0.762 win. That shifts only the absolute level, not the gradient,
because the mapping is monotone per map.

- The references are frozen from the base's own seed-1000 run before stage 2 starts. That run is disjoint from every
  evaluation seed.
- When C1-E's structure targets land, they replace m̂ with no other change.

**Which maps train, and which judge (out-of-sample rule).**

- The generalisation panel (`maps/new/*` 20, `maps/var/*_tr` 9, `maps/pub/*_rec` 2; the D-032/`rc` gen panel) is
  **never trained on**.
- Stage 2's held-in off-pool set is the six maps in `maps/` that are on neither panel: `arena`, `big_empty`,
  `Colosseum`, `default_small`, `stronghold` (base references) and `dilemma_10` (it has field references as
  "Prisoners Dilemma 10").
- The shipped bot reads no map identity; the parameters are global.
- Training seeds are 1000 + generation, disjoint from the evaluation seeds 1–3.

### 0.3 Opponents

- **Training:** the eight-bot zoo (`run_panel.ZOO`). Each fixture draws its opponent uniformly, stratified so that
  every generation sees each map in both seats.
- **Evaluation:** the D-032 panels exactly as the lanes run them: pool = zoo × 10 live maps × 2 seats; gen = the `rc`
  gen opponents × gen maps × 2 seats; seeds 1–3.
- **Self-play is excluded from stages 1–3.**
  - The curve reward is opponent-independent by construction, so self-play buys nothing for the curve.
  - Where it would matter, the terminal term, it is the known trap: the zoo shares Ares's habits, and a policy that
    beats its own lineage learns that lineage.
- **Stage 4** enters only if stages 1–3 produce a gate-passing policy. It is a league: frozen checkpoints make up at
  most 25 % of fixtures, and the zoo keeps at least 75 %.
- The gate never reads zoo win rate as the target. Win enters only as D-032's lower bound (> −0.02).

### 0.4 What "done" is

- **Accept** (D-032, per version against its parent, both panels):
  - paired seeds 1–3, both seats;
  - pool: bootstrap 90 % lower bound of Δecon~ > 0; units@100 and length@100 lower bounds ≥ −0.02; no tier-2 rate up
    > 10 %; win lower bound > −0.02;
  - generalisation: Δecon~ lower bound > −0.02.
  - Scored by `tools/rc/lane.py score` (copied verbatim from `r/rc`, so the lane and this one call the same code).
- **Promote** (D-032): the stack against Ares V06 at +0.05 economy on both panels.
- **The rejection rule this lane adds for itself.** A checkpoint whose training reward rises while its generalisation
  panel Δecon~ is negative has learned the training maps. It is rejected even if the pool passes, and the gap is the
  stage's first reported number.

## §1 — Infrastructure (built)

| Piece | Path | What it does |
|---|---|---|
| Tunable bot | `bots/alicia-02-tunable/` (`tune.hpp`) | `ALICIA_PARAMS="name=v;…"` overrides 89 exposed `Params` fields at boot. Unset, or in the sandbox (no environment), it uses the compiled defaults. An unknown name exits 3. Golden parity against `alicia-01-nodevil`: **0 divergent in 30,558 turns** (Trophy A, Schooltime B, mc26_archipelago A, seed 11). An override of `pearl_value` diverges at turn 18; the defaults passed explicitly are identical. |
| Environment | `tools/alicia/env.py` | runs paired fixtures `(policy, map, seat, seed, opponent)` through `unswbc run` with the policy injected by environment variable, harvests the replay, extracts features in process, and returns the reward terms and the full metric row. Resumable (a row per game in a JSONL cache), `--jobs`, no replays kept. |
| Reward | `tools/alicia/reward.py` | the curve term, guards and terminal term of §0.2; field percentiles for the pool, base-referenced pooled percentiles off-pool. |
| Optimiser | `tools/alicia/train.py` | antithetic ES with a checkpoint per generation, `--resume`, and a summary row per policy per generation in `game_stats/runs/alicia-train-*.jsonl`. |
| Scorecard | `tools/alicia/eval.py` | materialises a checkpoint as a bot directory (defaults compiled in), runs both D-032 panels through `tools/rc/lane.py` and prints its gate against the parent. |

## Ledger rows this memo touches

No weight moves on a memo. It commits to testing these rows:

- **L16** (0.5): the trigger is §0.1's outcome.
- **L04** (0.6): joint fitted weights vs hand weights.
- **L20** (0.15): not re-tested; joint moves are the route it names.
- **L29** (0.8): the guards are part of the reward.
- **L27** (0.5): layer (c) is not attempted, and the memo records why.
