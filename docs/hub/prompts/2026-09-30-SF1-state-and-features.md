# SF-1 — State and features: a representation lane on Ares (Opus 5.5, desktop, Claude Code)

Lineage: as given by the lead at launch. Bots `bots/<lineage>-<nn>-<slug>/`, branch `r/<lineage>`, worktree
`../wt-<lineage>`, tools `tools/<lineage>/`. Host: `~/Documents/Projects/2026/UNSW-Battlecode-2026` (the only
checkout), venv `.venv`, `--jobs $(( $(nproc) - 2 ))`, 4090 available (`torch` cu128) for the fitting steps that want it.

Read first: `docs/hub/prompts/2026-09-29-R-index.md` (rules), `docs/hub/HYPOTHESES.md` (rows L02, L03, L12, L13, L27, L29
are this lane's territory), `docs/findings/2026-09-30-r1-search-ladder.md` §"What to read from it",
`docs/findings/2026-09-30-ra-lane.md` §"What kinds of mechanism paid", `git show origin/r/sciel:claude/sciel-status.md`
(the 03a result and the 03b proposal), `docs/hub/prompts/2026-09-29-R5-eval-tuner-opus.md` (this lane absorbs R-5),
`bots/lune-r1-07-latecap8x-only/{world,policy,params}.hpp`, `docs/analysis/BENCHMARKS.md`.

## Why this lane exists

The programme's record: 33 rule and parameter moves on the Tyr evaluation, none accepted; one state variable
(Sciel's decayed food-density grid), economy +0.067, the only bar-clearing result. Lune: the next lever is what the
search values. The hand-set evaluation is at a local optimum for rule-shaped changes; the gains are in the
representation. **This lane's unit of experiment is a state variable plus its consumer, with the weight fitted,
never typed.** No rule tweaks, no threshold sweeps.

## Part 1 — the state module and the feature interface (first two days)

Base `<lineage>-00-base` = `lune-r1-07-latecap8x-only` verbatim (golden parity), then `<lineage>-01-nodevil`
(the `W==32 && H==16` terms inactive; D-033) as the parent of everything. Then build, behind switches, in
`state.hpp` (new) and `params.hpp`:

1. **Per-dragon decayed grids** over the bot's own cell index (the `NC` cells `world.hpp` already indexes), each a
   `float` per cell with a decay constant in `params.hpp`: `seen_age` (rounds since seen), `food_ew` (Sciel's: +1
   per pearl seen or eaten, ×λ per round), `ally_ew`, `enemy_ew` (+1 per visible ally/enemy part per round, ×λ),
   `threat_ew` (+1 per enemy head within k, ×λ), `death_ew` (+1 at every observed death cell, ×λ — the ledger's
   trapped/portal leak as a map). Smoothing: a 3×3 or 5×5 box-blur view read at query time, not stored (CPU is
   free: R-1 measured 9 M of 100 M points; keep it under 20 M anyway and probe).
2. **Scalars**: momentum (Ares has it), local pearl sparsity (pearls seen inside the last search horizon), units in
   view, clock (round / 500 and its square), own length, pending-split state.
3. **The feature interface.** Every place the policy scores a candidate target cell or a candidate move gets a
   feature vector `f(cell)` / `f(move)` assembled from the grids and scalars, and the score becomes
   `existing_score + Σ w_i · f_i` with every `w_i` a runtime-overridable parameter (`ARES_PARAMS`-style env
   override for local games, compiled defaults for shipping — the R-5 Part 1 design). With all `w_i = 0` the bot
   is byte-identical in behaviour to the parent: prove it with the golden harness. That is version
   `<lineage>-02-features` and it is the platform for everything after.
4. **A feature dump.** A build flag that logs, per decision, the feature vector of every candidate and the one
   chosen, to a compact binary/parquet under `build/<lineage>/` — the training data for Part 3. Off in shipped bots.

## Part 2 — one feature at a time, weight fitted (the loop)

For each feature (order: `food_ew` with the ally-saturation discount Sciel proposed; `ally_ew` as a crowding
cost; `enemy_ew` as a risk cost on routes and targets; `death_ew`; local sparsity as the search-cap selector
(L02: the cap scales with sparsity, no round threshold); `threat_ew`; the clock terms; then interactions):

1. Add the feature (a switch). Expected sign and the ledger row stated before any run.
2. **Fit the weight, don't guess it.** Two fitters, both in `tools/<lineage>/`:
   - `tune.py`: SPSA (or CLOP) over the one weight (later, the active set) on paired fixtures, objective = the
     D-032 accept statistic (bootstrap lower bound of Δeconomy on the pool with the guards), seeds 1–3, pool +
     generalisation panel. At ~2,900 games/h a 2,000-game sweep is ~40 min; log every evaluation.
   - `fit.py`: a supervised fit where a clean label exists — for target choice, the corpus' winners (top-30 sides in
     `public_replays/corpus`) give "which visible/remembered target did a winning side move toward"; a logistic or
     GBT on the feature vector gives a weight (or a scorer) directly, which SPSA then refines. The
     `tools/team_recon_claude/` extractors and `export_hgb.py` are the starting point.
3. Measure the fitted weight against the parent on the D-032 gate. Accept → new parent; hold → queued to stack;
   reject → the weight and the surface go in the table anyway (a zero-weight optimum is a finding about the
   feature, not a failure).
4. Every fifth feature, re-tune the whole active set jointly (SPSA over the vector); report whether joint beats
   sequential.

## Part 3 — the learned scorer (when Part 2 has ≥ 3 accepted features)

Replace the linear `Σ w_i f_i` for the target scorer with a small learned scorer trained on the feature dump
plus outcomes: first a GBT (exported to a C++ header via `export_hgb.py`'s path), then, if it beats the linear
form at equal CPU, a tiny MLP (≤ 4k weights, exported as arrays; the 4090 trains it in minutes, the bot runs it in
microseconds). Targets: (a) supervised on top-30 corpus choices, (b) self-play regression — the pearl and survival
outcome over the next 20 rounds of the chosen target, from the bot's own games. Gate as always; also report the
scorer's fidelity to the linear one on held-out decisions so the gain is attributable.

## Rules

D-032 gate for every accept (paired seeds 1–3, pool + generalisation panel, interval form, per-checkpoint).
Out-of-sample rule: features are measured structure only; never dimensions, names or hashes. One feature per
version. Parent reproducible from the same source with the weight at its old value. CPU probe
(`arena.py --sandbox`, dense fixtures) on every version that adds a grid. Never commit the feature dumps.
`claude/<lineage>-status.md` after every version (running table: version, feature, ledger row, fitted weight and
its interval, surface summary, pool Δ with interval, generalisation Δ, per-checkpoint, CPU max, verdict).
`docs/findings/2026-10-0x-<lineage>-state-features.md` at Part 1 done, at every fifth feature, and at Part 3, each
ending with the ledger rows touched and proposed weights. `CANDIDATE.toml` on every accepted version
(`language = "c++"`, `lineage_parent` = previous accepted). Commit and push `r/<lineage>` after every version. Do
not register. Do not read lane `rb`. Coordinate with lane `rc` only through the ledger: if `rc` has already run
the ally-saturation discount, start from its result rather than repeating it.
