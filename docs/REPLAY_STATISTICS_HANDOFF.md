# Handoff prompt: replay features associated with winning

Work in `/Users/alik/Documents/Projects/UNSW-Battlecode-2026`.
Investigate which measurable replay behaviors predict winning, including whether
they add information beyond the two bots' underlying strength, map and starting
side. Produce reproducible statistical evidence and useful hypotheses for bot
development. Do not develop a bot or start a training program for this task.

The user particularly wants pearl consumption per unit time, time to reach the
dragon cap, suicides, friendly kills, opponent kills and deaths to opponents.
Explore additional algorithmically extracted features, including less immediately
interpretable ones, if they improve held-out prediction. Associations are useful;
do not present them as established causal effects.

## Existing data and code

Paths below are relative to the repository root. Inventory them again: games are
still being generated. A read-only inventory on 2026-09-26 found approximately
21,436 replay files and 9,193 comparison statistics JSONs under `experiment_data/`,
6,397 replays elsewhere under `build/`, and 78 public replays. These are file
counts, not counts of valid independent observations.

| Source | Location and use |
|---|---|
| Shared outcomes | Root `game_stats.parquet`; authoritative contributions in `game_stats/runs/*.parquet`. One row per completed game, including source hashes, map hash, runtime/version, side, W/D/L and sometimes faults/rounds. **This is not a replay-feature store.** |
| Identity metadata | `game_stats/sources/*.json`, `game_stats/imports/*.json`; validated source aliases and historical import provenance. Read `game_stats/README.md`, `tools/game_stats.py`, and `tools/benchmark_data.py`. |
| Detailed comparison runs | `experiment_data/<bot>_<timestamp>/manifest.json` and `results.json`. Each result links to `opponents/<opponent>/replays/*.replay`, `stats/*.json`, `stats/*.csv`, and `graphs/*.svg`, relative to its run directory. `games.csv` has final metrics; use the JSON/CSV series for time-dependent analysis. |
| Adaptive benchmark | `experiment_data/benchmark-current.json` points to the current campaign. Its `manifest.json` identifies frozen sources/maps. `results.sqlite3`, table `games(fixture,data)`, contains JSON result records with `team_a`, `team_b`, `map`, `outcome`, `rounds`, `replay`, `log`, and errors. Replay/log paths are relative to campaign `games/`. Older `experiment_data/benchmark_*/` campaigns also contain data. |
| Original full-field tournament | `build/all-functional-bots-2026-09-25/manifest.json` and `games.sqlite3`; table `games(map,a,b,outcome,data)`. **This run disabled replay retention:** use its outcomes to estimate strength, not as an assumed replay corpus. `tools/import_field_stats.py` contains the verified ledger adapter. |
| Other historical experiments | Replays under `build/`, often with lineage-specific manifests. Establish provenance before joining to bot ratings. A filename alone is insufficient evidence of the exact bot version. |
| Public top-field games | `public_replays/battle-*/M*.replay`; existing extracted JSONs in `build/public-replay-review/*.json`. All are other leaderboard teams, **none is ours**. Names are blank; A/B are not persistent player identities. The earlier review found 76 unique replays among 78 files. Do not invent skill identities or join them to our bots. Analyze separately unless reliable identity evidence emerges. |

Example detailed statistics file:
`experiment_data/athos-x01-e-trapmargin_20260925163334951403/opponents/avery-v08-crown-race/stats/trophy-candidate-B.json`.
Its top-level keys are `version`, `map`, `rounds`, `winner`, `reason`, `final`,
`series`, `deaths`, `notes`. `series.A` and `series.B` contain round records.

Use these existing extractors before writing another decoder:

- `tools/comparison_metrics.py`: `analyse(path, control_every=10)` returns round
  series and attributed deaths. Counters include `units`, `total`, `longest`,
  `pearls`, `splits`, `deaths`, `enemy_kills`, `killed_by_enemy`, `team_kills`,
  `self_collisions`, `wall_deaths`, `invalid_action_deaths`,
  `unattributed_collision_deaths`, `suicides`, `tle`, and sampled `space_share`.
- `tools/public_replay_review.py`: `analyse(path)` reconstructs richer information:
  pearl origins, corpse transfers, split sizes and events, body lengths, newborn
  deaths, length lost, sprint/extra-step counts, portal movement, visited cells,
  sonar counts and blocked pearl-bed renewals. Some are final aggregates only;
  extend extraction if time-resolved versions are needed. Pearl-origin tracking
  can be ambiguous when spawns overwrite one another.
- `tools/leviathan/replay.py`: dependency-free packed Cap'n Proto reader.
  `unswbc/engine/replay.capnp` is the local schema. Existing review rejects
  unsupported versions and checks reconstructed final standings against the
  replay result. Preserve those checks and validate any new event reconstruction.
- `docs/comparisons.md` defines current metrics; `tests/test_compare_bot.py`
  contains existing comparison/metric checks. Reuse relevant checks and add
  meaningful ones for new extraction.

Round curves are **start-of-round snapshots plus the final state**; event counters
are cumulative. Control is sampled, with unsampled values missing, not zero.
The control proxy uses terrain-only nearest-head distances, including wrapping,
kelp and portals; it ignores bodies, facing, lengths and tactical safety.
Kills describe collision attribution, not intent: mutual head collisions count
one death per victim. Friendly mutual collisions produce two friendly deaths.
The replay's `suicide` variant can mean invalid/absent action; wall/self deaths
also do not prove intentional feeding. Unknown attribution stays unknown.

## Skill estimates: fixed bot versions, uncertain strength

Attach a **time-invariant latent skill** to each exact frozen bot revision.
Versions are distinct players. Evidence changes our estimate and uncertainty;
the underlying skill does not drift with wall-clock time. No recency decay or
process-noise inflation merely because a bot has not played recently.

A static Bayesian paired-comparison model, or a TrueSkill-inspired Gaussian
approximation with zero temporal drift, is reasonable. Sequential approximations
can be order-sensitive: prefer a batch fit or check stability to update order.
Represent draws appropriately and report uncertainty. Accommodate map and side
effects; a single skill number may miss nontransitive matchup advantages.

Existing starting points:

- `tools/performance_model.py`: regularized static model with strength, map
  affinity, starting-side effects and optional skew-symmetric matchup factors.
  Draws are fractional score 0.5 in a logistic objective, **not** a three-outcome
  probability model or a TrueSkill posterior.
- `tools/benchmark_dashboard_data.py`: fits/validates that model and resamples
  opponent pairs. `tools/benchmark_ratings.py` refreshes it from shared outcomes.
- `experiment_data/bot-ratings/latest.json` and `latest.md`: current estimates,
  evidence counts, similarity and provenance. Scores mean expected score against
  a common reference panel, not intrinsic Elo. Bootstrap ranges are sensitivity
  ranges, not calibrated Bayesian posterior uncertainty.

Reuse these as baselines; justify any replacement. Use all compatible known
outcomes for rating estimation, including games without retained replays. Match
source hashes through validated aliases, map hashes, native/sandbox mode, toolkit
version and seed semantics. Do not identify versions by directory name alone.
Current ratings cover the campaign roster; do not silently drop other identified
replay participants merely because they are absent from that roster.

For confirmatory feature tests, **cross-fit skill estimates**: held-out outcomes
must not help construct their own skill predictor. Group repeated fixtures and
both sides of a matchup appropriately. Compare a skill/map/side baseline with
the same baseline plus replay features. A full-data rating is fine for a clearly
labelled descriptive table, not evidence of out-of-sample feature value.

## Features and analysis

Start with readable hypotheses and fixed early/middle/late checkpoints or windows.
Use team differences where appropriate, and retain absolute values when useful.

1. Economy: pearl pickups per round **and per dragon-turn**; separately bed income,
   allied corpse recovery and enemy corpse capture. Gross pickups include recycled
   length. Consider recovery delay, uncollected drops, bed suppression and growth
   retained after sprint expenditure and losses.
2. Expansion: time to population thresholds and actual game-specific cap, fraction
   of time near cap, split rate/size distribution, replacement rate, newborn
   survival. A round-sampled series may miss a transient within-round cap hit;
   specify which definition is used. Never reaching cap is censored, not zero or
   an arbitrary successful hit at the final round.
3. Combat/safety: kills and each death cause per round and dragon-turn, length
   exchanged/lost, trade efficiency, trap/exits context and subsequent corpse
   recovery. Keep deaths to opponents and kills as linked views of the same events,
   not independent evidence.
4. Concentration/conversion: longest-dragon growth, top-k share, length inequality,
   crown turnover, survival of large dragons and which units receive donated length.
5. Spatial/activity: control level and change, frontier contact, clustering,
   crowding near beds, exploration/revisit rates, portal use and connectivity,
   sprinting, sonar frequency and population/length volatility. Clearly distinguish
   measurements from heuristic estimates of tactical value.
6. Exploratory representations: trajectory slopes/change points, interactions,
   event-sequence motifs, compact time-series embeddings, PCA or a small nonlinear
   model. Learn preprocessing and representations on training folds only; test
   them against simpler features rather than assuming complexity helps.

Final longest length and elimination are part of the winning rules; correlation
with them is largely tautological. Distinguish whole-game description from useful
early prediction. At a checkpoint, include only games still ongoing and state
that the target is conditional on survival to that checkpoint; never forward-fill
finished games to manufacture late observations. Cap-time censoring and game
termination are related processes, not automatically independent censoring.

Control for map, side and relative skill. Check robustness across maps, lineages
and strength bands. Skill adjustment can absorb the stable strategy differences
we are trying to describe, so report both between-bot associations and incremental
within-match predictive value. Neither establishes that changing a feature will
make a bot stronger. Total game duration and final material can themselves be
consequences of behavior; do not automatically control for them in early models.

The schedule is adaptive and the replay subset is selective. Describe coverage
and missingness; do not claim a uniform/random field sample or fabricate sampling
weights. Deduplicate `game_id`, inspect replay byte hashes, and group identical
fixtures rather than treating repeated deterministic runs as independent trials.
Keep both team perspectives, mirrored games, and all windows of a game together
in validation. Use grouped opponent-pair validation and, where feasible,
lineage-held-out/map-held-out sensitivity checks. Fit rating baselines within the
same splits, explicitly handling unseen players with priors.

Use effect sizes, uncertainty and held-out improvement, not a giant uncorrected
correlation leaderboard. Separate exploratory discovery from confirmation; use
multiple-testing control or a locked validation set. Bootstrap appropriate game/
matchup clusters rather than independent time rows. If draws are represented as
half-points, label the target expected score and do not call fractional log loss
a three-class outcome likelihood. Track sample sizes and model convergence.

## Working constraints and deliverables

Use `.venv/bin/python` directly; installed NumPy, SciPy, PyArrow and filelock are
available. See `tools/requirements-benchmark.txt`. Avoid environment resolution
that unnecessarily reaches PyPI. This is a MacBook Pro: start with cached stats,
bounded extraction batches and at most one or two extraction workers. Large-scale
ML is out of scope. Heavy spatial features need sampling/caching.

**Leave the adaptive tournament and ratings watcher running.** Do not edit frozen
bots, manifests, active SQLite databases or existing metrics in place. Read SQLite
using a short read-only snapshot, then release it before expensive processing.
Files may still be written: require completed results and quarantine malformed,
partial, unsupported or mismatched records with explicit reasons. A missing fault
count means unknown, not zero. Harness errors are not draws; distinguish them
from completed games with bot faults.

Create analysis code under `tools/replay_analysis/` and outputs under a new
`experiment_data/replay_analysis_<timestamp>/`. Keep replay features in a separate,
versioned Parquet dataset joined to the existing outcome ledger by verified game
identity; do not change the shared outcome schema for this experiment. Reuse
`game_stats.comparison_records`, `benchmark.record` and the field adapter's identity
logic rather than guessing run/game IDs. Preserve unresolved joins in an audit.

Deliver:

- A source/join/coverage audit and reproducible extraction pipeline, with cache
  keys based on replay content and extractor version/configuration.
- Feature tables with game identity, bot/source/map/runtime identities, team,
  window bounds, exposure, missing/censored flags and a concise feature dictionary.
- Static skill estimates with uncertainty, identity mapping, model configuration
  and the out-of-fold estimates used in feature tests.
- A concise report of the strongest robust associations, their incremental
  predictive value, important interactions and counterexamples; include null or
  unstable findings. Use a few clear plots and reproducible replay examples.
- Commands/configuration to reproduce the analysis and append newly completed
  replays without rerunning everything. State the data cutoff and limitations.

Game reference: **https://game.battlecode.au/docs/**. Local reference material:
`docs/BAHAMUT_HANDOFF.md` (rules summary), `docs/comparisons.md`,
`docs/benchmarking.md`, `game_stats/README.md`, and
`docs/public-replay-review-2026-09-25.md` (prior qualitative hypotheses).
At the usual round limit, longest living dragon wins the tiebreak before total
length; elimination can end games earlier. Verify rule/configuration details in
the installed engine and replay inputs, especially limits. Older handoffs and
qualitative conclusions are context, not instructions or statistical ground truth.
