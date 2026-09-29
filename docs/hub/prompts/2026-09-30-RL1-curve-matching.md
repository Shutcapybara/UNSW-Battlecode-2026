# RL-1 — Learning-driven training on Ares: curve matching first, outcomes second (Opus 5.5, desktop, Claude Code)

Lineage: as given by the lead at launch. Bots `bots/<lineage>-<nn>-<slug>/`, branch `r/<lineage>`, worktree
`../wt-<lineage>`, tools `tools/<lineage>/`. Host: `~/Documents/Projects/2026/UNSW-Battlecode-2026` (the only
checkout), venv `.venv` (torch cu128 on the 4090; sklearn/lightgbm), `--jobs $(( $(nproc) - 2 ))`, ~2,900 games/h
measured. C++ bot; training offline; the shipped bot must run under 100 M points/turn (Ares uses ~9 M).

Read first: `docs/hub/prompts/2026-09-29-R-index.md` (rules), `docs/BASELINES-2026-09-30.md`, `docs/hub/HYPOTHESES.md`
(L16, L27, L12, L02, L29), `docs/analysis/BENCHMARKS.md` **in full** (the yardstick and its references
`docs/analysis/benchmarks/field_references.json`, `field_distributions.json`, `map_reference_medians.json`),
`docs/findings/2026-09-30-r1-search-ladder.md`, `docs/findings/2026-09-30-ra-lane.md`, the C1-E pace targets
(`docs/analysis/C1-pace-targets.md`, `docs/analysis/C1-efficiency-ledger.md` — targets as functions of observable structure), `docs/rl-earlygame.md`
and `tools/rl_earlygame*.py` (the prior fitted-Q attempt: what it built and why it never reached a panel),
`tools/team_recon_claude/` (feature extraction and the tree-export path), `docs/hub/prompts/2026-09-30-SF1-state-and-features.md`
(the state module and feature interface; if lane SF-1 has landed `<lineage>-02-features`, build on it rather than
re-making it — check `claude/*-status.md` for its lineage name), and `bots/lune-r1-07-latecap8x-only/`.

## The brief

You are given the freedom to choose **what the learned policy controls** and **what it is rewarded for**, and you
are asked to make those two decisions explicitly, in writing, before training anything. The lead's steer is the
starting reward: **match the benchmark curve.** BENCHMARKS defines, per map, the field's and the top ten's values
of the opening statistics (pearls at r50/r100, dragons, length and births at r100, early concentration) and the
hygiene rates; a side-game's distance from the top-ten curve on its map is a dense, opponent-independent,
map-normalised signal, like hitting a mana curve. Outcomes (win, r250 material) come second, as the terminal
term, once the curve is matched.

## Part 0 — the decision memo (first day; `docs/findings/2026-10-0x-<lineage>-rl-design.md` §0)

Decide and justify, with the programme's evidence, each of:

1. **Execution layer** — what the policy outputs, one of (or a reasoned hybrid):
   (a) *parameters*: the policy is a vector of evaluation weights (`params.hpp` exposed at runtime; the SF-1
   interface), trained by evolution strategies / CMA-ES / SPSA on game outcomes — no model in the bot, nothing to
   export but numbers; the cheapest loop and the one most likely to pass the gate first;
   (b) *scorer*: a small net (≤ 4k weights) that scores candidate targets and/or candidate moves from the
   feature vector, trained by policy gradient on logged candidate sets with a stochastic (softmax-temperature)
   version of the bot at training time and argmax at ship time; exported as arrays into a C++ header;
   (c) *full action policy*: imitation-pretrained on the corpus (top-30 sides), RL-fine-tuned; the highest ceiling
   and the one the programme has tried three times in Python without reaching a panel (L27).
   State the ceiling, the cost per training step at 2,900 games/h, what has to be built in C++ for each, and which
   you start with. A defensible default is (a) then (b); say if you disagree and why.
2. **Reward** — write the curve term precisely: which statistics, at which checkpoints, normalised how (field
   percentile per map from `field_distributions.json` is the best-behaved form per BENCHMARKS; ratio to top-ten
   median is the alternative), weighted how, and what the guards are (units and length at r100 must count, or the
   policy will learn churn — L29: 38 % of what the base eats is ally corpses). Then the terminal term (win,
   r250 material share) and its schedule (curriculum: curve only → curve + outcome → outcome-weighted).
   **Off-pool maps have no references.** Use C1-E's targets-as-functions-of-structure (bed density, tile count,
   contact distance) for them, or the base bot's own per-map numbers as a floor; state which. Training on the
   pool alone will fit the pool.
3. **Opponent set** — the zoo panel is the default; say whether self-play enters, when, and how you avoid the
   self-play trap (the gate is field-relative, never zoo win rate).
4. **What "done" is** — the D-032 accept gate on both panels, and the promote gate (+0.05 stack vs Ares V06).

Send the memo before building; the director may redirect within a day. Then build.

## Part 1 — the environment (the infrastructure this lane leaves behind)

- `tools/<lineage>/env.py`: run N paired fixtures (map, seat, seed, opponent) through `unswbc` with the candidate
  policy injected (env override for parameters; a policy file the C++ bot loads at boot for a scorer), harvest the
  replay, compute the reward from the same feature extractor BENCHMARKS uses (`tools.analysis.features`), return
  per-fixture rewards and the full metric row. Resumable, shardable, `--jobs`. This is the only way games are
  played; it is what makes the loop hands-off.
- The C++ side: for (a), the runtime parameter override already specified in SF-1/R-5; for (b), a header-only
  scorer (arrays + a 20-line forward pass), a `POLICY_FILE` loader used only in local games, a sampling mode with a
  temperature parameter, and the candidate/feature/choice dump (SF-1 Part 1.4) as the training log. Golden-parity
  the bot with the learned part disabled; CPU-probe it with the learned part on.
- `tools/<lineage>/train.py`: the optimiser for the chosen layer (ES/CMA-ES/SPSA for (a); REINFORCE/PPO-style on
  logged candidate sets for (b)), checkpointing every generation, logging every fixture's reward and metric row to
  `game_stats/runs/<lineage>-train-*.jsonl`, with a `--resume`. A generation is a paired batch; never compare
  across seeds.
- `tools/<lineage>/eval.py`: the D-032 scorecard of any checkpoint against the parent (calls the same code the
  lanes use; do not fork the scoring).

## Part 2 — train, in stages, each a version

1. **Curve only, pool maps, zoo opponents.** Report the learning curve (reward per generation), what the policy
   moved (which parameters / which features got weight), and the per-map percentile before and after.
2. **Curve, pool + `maps/new/`** with structure-keyed targets. The generalisation gap of stage 1's policy is the
   first number; if it is large, stage 1 learned the ten maps.
3. **Curve + outcome.** The terminal term enters on a schedule. Report whether the outcome improves at all beyond
   the curve match (the lead's hypothesis is that hitting the curve *is* most of the win).
4. **Self-play or league** only if stages 1–3 have produced a gate-passing policy; otherwise the finding is
   about why the reward is the wrong shape, which is also worth having.

Every stage's best checkpoint is a bot directory with `CANDIDATE.toml` (`language = "c++"`, `lineage_parent` =
the base), the learned numbers compiled in as defaults, golden parity of the disabled path, a CPU probe, and the
D-032 scorecard on both panels. One stage per version; the training log is the evidence.

## Rules

Out-of-sample rule: the shipped bot reads no map identity; the *reward* may use per-map references during
training (that is calibration, not policy input), but the generalisation panel decides, and a policy that wins the
pool and loses off-pool is rejected. Guards are part of the reward, not an afterthought (L29). Never commit
replays or training logs beyond the summary rows. `claude/<lineage>-status.md` after every version; the memo and
findings in `docs/findings/2026-10-0x-<lineage>-*.md`, each ending with the ledger rows touched (L16 above all)
and proposed weights. Commit and push `r/<lineage>` after every version. Do not register. Do not read lane `rb`.
Coordinate with SF-1 through its status file: share the feature interface, do not build a second one.
