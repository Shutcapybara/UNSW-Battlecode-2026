# Collection benchmarking

[`benchmark.toml`](../benchmark.toml) contains 24 curated reference opponents,
39 unresolved screening bots and 8 new stable candidates (71 total), on 33 maps.
The single-candidate [`comparison.toml`](../comparison.toml) still uses the
24-opponent curated pool and original maps.
See [the selection analysis](benchmark-pool-20260927.md) and
[every bot's status](benchmark-pool-status.json). The previous 286-bot default is
preserved in [`benchmark-all-20260927.toml`](../benchmark-all-20260927.toml).
The September 27 expansion replaces the 286-bot campaign with a new frozen plan;
the old campaign and its recorded results remain intact. The current campaign is
identified by `experiment_data/benchmark-current.json`.

Edit or copy a TOML; paths are relative to that file. The curated pool points to
the tested local snapshots, including frozen maps. Copy those snapshots when
sharing, or verify source fingerprints before substituting working directories.
The scaffold, profiling wrapper and diagnostic trace copies remain excluded.
Later-created bots are never silently added. The expansion inventory, aliases,
controls and deferred in-progress versions are recorded in
`experiment_data/benchmark-expansion-20260927.json`.

`context_manifest` preserves the previous roster's source identities as passive
rating context. Games against retired opponents still anchor the strength fit
and adaptive priority model, but those opponents cannot be scheduled. The latest
rating table shows only active bots; historical context is counted separately.
Planning freezes these identities, and an active version supersedes any older
version with the same name. Matching still requires map hash, source hash and
runtime identity; context does not relax provenance checks.

## Weighted maps

The 13 established maps share 50% of the target distribution equally. The 20 maps
in [`maps/new`](../maps/new/EXPLAINER.md) share the other 50% using the supplied
family-balanced recommended weights. The original/synthetic mixture is a working
choice, not an estimated finals probability. Change it in the benchmark TOML:

```toml
[map_distribution]
manifest = "maps/new/manifest.json"
mass = 0.5
```

The supplied manifest's `default_training_map_weight` matches the CSV's
`recommended_map_weight`. Planning validates map hashes and freezes the normalized
distribution, suite metadata and manifest. Without this section, weights are
uniform for backward compatibility. Existing frozen campaigns keep their weights.

Adaptive selection multiplies information gain by map weight; it is an adaptive
priority, not a strict frequency quota. Overall ratings average map predictions
with the same weights and both starting sides. Raw outcomes and fixture identities
in the shared Parquet are unchanged, and historical matches still count. The model
fits conditional game outcomes normally; weights specify the evaluation target,
not artificial repetitions of games. The optional suite `training_game_weights.csv`
applies to its historical smoke fixtures and is not reused for new games.

Ratings flag bots as sparse until observed maps cover at least 80% of target weight,
in addition to the existing game/opponent/map-count gates. Predictions for unplayed
maps borrow general strength and should not be treated as measured performance.
The older static coverage reports remain descriptive observed-fixture averages;
the continuously refreshed rating report supplies the weighted strength estimate.

The default `pairing = "adaptive"` selects informative missing matchups across
the roster. Set `pairing = "panel"` for uniform coverage against the configured
references, or `pairing = "round_robin"` for uniform coverage against everyone.
All modes use both sides and exclude self-matches.

## Adaptive selection

Every approximately 128 games, fit a regularized strength model with map and
starting-side effects to distinct recorded fixtures. Favor bots whose optimistic
strength estimate puts them near the upper fifth of the roster, and choose
opponents using predicted matchup closeness, approximate information gain and
existing opponent evidence. Downweight repeatedly testing the same opponent or
lineage, and favor maps with less information. Reserve one in five pair blocks
for the least-tested eligible bot, so uncertain newcomers and weaker bots remain
eligible. Available games include direct contender-versus-contender matches.

The uncertainty calculation is a cheap diagonal-information approximation;
this is a scheduling heuristic, not calibrated confidence intervals or the
final ranking model. Each batch accounts for already-planned games when choosing
the next pair. Finished games from other scripts are incorporated at the next
refresh. Both sides of a selected map are scheduled unless one is already known.
`adaptive-plan.json` records the latest choices, predicted scores, selection
reasons and model convergence. `progress.json` and `runner.log` report progress.
Adaptive runs skip automatic visual reports; they continue until stopped or
all eligible gaps are exhausted. The large possible-fixture count is the search
space, not a requirement to finish a full round robin before obtaining rankings.

## Run

Use the existing `.venv`. Adaptive selection additionally uses NumPy/SciPy;
one-time dependencies are pinned in `tools/requirements-benchmark.txt`.
From the repository root:

```sh
.venv/bin/python tools/benchmark.py plan --config benchmark.toml
# The command prints the newly created experiment_data/benchmark_TIMESTAMP path.
.venv/bin/python tools/benchmark.py run experiment_data/benchmark_TIMESTAMP --jobs 4
```

`plan` gathers existing results, freezes the selected bots and maps, and writes
the initial schedule (adaptive batches are generated during execution). `run`
resumes that directory automatically. Use
`--max-games 100` for a bounded batch. Replays and logs are retained under `games/`;
`--no-replays` saves disk space. On macOS, prefix the run command with
`caffeinate -i` to prevent idle sleep while it runs. Closing the lid can still
suspend the machine. Ctrl-C checkpoints completed games; run the same command
again to resume.

Uniform scheduling prioritizes the least-covered bots; adaptive scheduling uses
the rule above. Both spread games and keep opposite-side fixtures adjacent. A completed game from
another experiment can fill the same gap. The central ledger is checked at
startup and periodically; don't start overlapping campaigns deliberately.
One campaign cannot have two runners at once.

## Read the results

The continuously refreshed strength table is
[`experiment_data/bot-ratings/latest.md`](../experiment_data/bot-ratings/latest.md).
`latest.json` contains the same estimates plus map profiles, observed similarities,
head-to-head results and source fingerprints. `status.json` records refresh health;
check its timestamps if estimates seem stale. The earlier inline visualization is
a snapshot, not a live view.

Start the independent, single-instance refresher alongside the tournament:

```sh
caffeinate -i .venv/bin/python -u tools/benchmark_ratings.py --watch --interval 300
```

It checks every five minutes, refitting only when contributions or identity metadata
change, and follows `experiment_data/benchmark-current.json`. Each refresh rebuilds
the shared ledger from contribution Parquets, so matching historical results,
other comparison runs and contributions merged from Git all count. It ranks the
current campaign's frozen versions; other revisions remain in the ledger and are
not silently mixed. Latest-created bots require a new campaign roster.

Scores use the same reference opponents, the frozen map distribution and both sides.
The regularized model accounts for opponent, map and side; held-out opponent pairs
select whether matchup interactions improve predictions. Twenty-four opponent-pair
bootstrap fits provide sensitivity ranges, not calibrated confidence intervals.
The table flags sparse evidence and shows the nearest observed performance profile.
Failed fits preserve the last successful report and retry next interval. The worker
uses one numerical thread; temporary full-ledger snapshots are removed each time.
Omit `--watch` to refresh once. Match collection runs independently of this worker.

For panel/round-robin runs, open `index.html` in the run directory. It includes per-bot reference coverage,
paired scores and the matchup-coverage matrix. Refresh it while the run proceeds.
The underlying files are `coverage.csv`, `pairwise.csv`, `per_map.csv` and
`progress.json`. To refresh from the collective ledger without running games:

```sh
.venv/bin/python tools/benchmark.py report experiment_data/benchmark_TIMESTAMP
```

Paired score averages completed opponent/map cells after averaging the two
sides. Incomplete cells do not enter that score. Compare coverage alongside
performance: different missing cells can make two partial scores misleading.
Repeated identical fixtures contribute once to coverage; their outcomes are
averaged for scores. Missing fixtures and harness errors are never draws.
All-matching W/D/L counts also include games outside the reference panel.

This runner collects outcomes efficiently. Use `tools/compare_bot.py` for the
detailed replay-statistics graphs when investigating a particular matchup.
Native results do not establish compliance with judge CPU limits.

## Provenance, failures and sharing

Coverage requires matching source fingerprints, map contents, runtime mode and
toolkit version. README-only changes are merged only when packaging explicitly
excludes those files; other changed files conservatively create a new revision.
Editing a live bot does not alter a frozen campaign. Make a new plan to evaluate
the edited version.

`import_audit.json` inventories historical results. Current comparison results,
the partial original tournament and verified older lab snapshots enter the
shared ledger. Older files missing source/map fingerprints or toolkit versions
remain inventoried but cannot fill current-version gaps. Imported lab timestamps
are explicitly labelled estimates from manifest modification time; timestamps
never determine source identity. Parameter overrides retain their actual hashes.

Every finished game is immediately committed to `results.sqlite3`. Completed
outcomes are published to the central Parquet in batches of 32, every minute,
and on shutdown. Resume recovers any unpublished journal entries. Harness errors
block both participants in the campaign's `blocked-bots.json` to avoid repeatedly
failing games, including after a restart; inspect the logs, then resume with `--retry-errors` after fixing
the environment. Never modify frozen sources to fix a bot: create a new version
and plan instead.

Share `game_stats/runs/`, `game_stats/sources/` and `game_stats/imports/` in Git.
The latter two preserve source aliases and historical-import provenance across
machines. Rebuild `game_stats.parquet` with the existing
`tools/game_stats.py rebuild` command after merging contributions. Experiment
directories and the generated central Parquet remain local.
