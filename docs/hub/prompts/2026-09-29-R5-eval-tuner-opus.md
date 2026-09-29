# R-5 — Parameter exposure and a tuner over Ares's evaluation weights (Opus 5.5)

Branch `r/r5`, worktree `../wt-r5`. Bots under `bots/r5-<nn>-<slug>/`, tools under `tools/r5/`. Read first:
`docs/hub/prompts/2026-09-29-R-index.md` (rules), `bots/ares-v06-expanded-search-support/params.hpp` and
`policy.hpp`, `docs/analysis/BENCHMARKS.md`, `claude/r1-status.md` (base choice), `docs/design-framework.md`.
Start when R-1's step 0 has named the base; until then, build the tooling against V06.

## Why

Ares's policy is already a bounded search over candidate moves with a hand-weighted cost (`params.hpp`:
`pearl_value 10`, `bed_value 8`, `split_value 8`, `dive_cost 4`, `crowd_weight 0.6`, `momentum_weight 0.6`,
`target_gamma 0.93`, some forty more). Every one of those numbers was set by a person reading a replay. This is
the chess-engine situation before automated tuning: the evaluation is the right shape and the weights have never
been fitted. R-1 measures what more search buys; this task measures what better weights buy, and builds the
machine that fits them so that the loop no longer needs a person per number.

## Part 1 — expose (a day)

1. Copy the base to `r5-00-exposed`. Turn every `static constexpr` in `params.hpp` that the policy reads at
   decision time into a runtime-loadable value with the same default: a single `Params` struct filled from
   compiled defaults and then overridden from an environment variable `ARES_PARAMS` (`name=value,…`) read once at
   boot. The contest sandbox has no env, so the shipped bot is the compiled defaults; the tuner sets the env in
   local games only. Cost: prove with `arena.py --sandbox` that the per-turn max moves by less than 1 % and
   golden-harness that `r5-00` with no override has parity with the base.
2. Classify the parameters: **search budget** (R-1's knobs — frozen here at R-1's recommendation), **structural
   thresholds** (`split_min_len`, `grow_from`, `opening_*`, TTLs — integer, few values), and **evaluation
   weights** (the doubles). List them in `tools/r5/params.json` with type, default, a sane range, and which
   ledger row or tier-1 metric each is expected to move. The tuner works on the third class first.

## Part 2 — the tuner

`tools/r5/tune.py`: SPSA over the evaluation weights (the method chess engines use for exactly this; CLOP is the
alternative if SPSA's noise is unmanageable — say which and why). Objective = the BENCHMARKS tier-1 objective, not
win rate: the mean of the four map-normalised economy checkpoints, with r100 dragons and length as constraints
(a step that lowers either by more than its resolution in BENCHMARKS' table is rejected) and the tier-2 rates as
a guard (>10 % up on any = rejected). Games: paired (candidate vs base on the same map, seed, and seat) on the
z1 fixtures, atlas off, so the noise is the paired residual, not the raw variance. Use the resolution table in
BENCHMARKS §"How to use it" to size iterations; log every evaluation to `game_stats/runs/r5-tune-*.jsonl`
(params, fixture, all metrics) so the surface can be re-analysed without re-playing.

Run it on **one** map family first (the Schooltime-class maps, grouped by tile count and bed density, not by
name) to see whether it converges at all, then on the full ten, then confirm the found weights
on the generalisation panel. A weight set that wins on the pool and loses on `maps/new/` has been fitted to the
pool; report it as such.

## Part 3 — what the surface says

The finding's value is as much the surface as the optimum:

- Which weights matter (sensitivity: objective change per unit step at the default). Expect a few to dominate;
  say which, and whether they are economy or retention weights.
- Whether the optimum is one point or a ridge (if `pearl_value` and `bed_value` only matter as a ratio, say so;
  that is design information for the policy).
- Whether the optimum moves with observable structure (tile count, bed density, unit count): if the best weights
  on tiny maps differ from Schooltime-class, the OOS rule says the policy should key the weight on the structure
  feature — propose the function, do not hard-code the map.
- The clock: whether the optimum moves with round number (S-4/S-5 in the ten-day plan asked for time as an input;
  a weight schedule fitted here is the first evidence either way).

## Deliverables

`r5-00-exposed` (parity proven), `tools/r5/` (params.json, tune.py, README with the exact commands), the tuned
candidate `r5-01-tuned` with its weights in `params.hpp` defaults and a `CANDIDATE.toml` (`language = "c++"`,
lineage `ares`, `lineage_parent` = base) if it passes the BENCHMARKS gate on both panels,
`docs/findings/2026-09-3x-r5-eval-tuner.md` with the surface, `claude/r5-status.md`. Do not register. Do not
touch `bots/ares-*` or other lanes' trees.

Budget: Part 1 ~100 games; Part 2 is the expensive one — plan for ~2,000 paired games and say in the status
file how many the tuner has used every 200.
