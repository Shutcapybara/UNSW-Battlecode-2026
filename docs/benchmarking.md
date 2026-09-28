# Benchmarking and comparisons

This checkout has three supported comparison paths:

- [`tools/compare_bot.py`](../tools/compare_bot.py) compares one candidate with
  an explicit TOML roster and saves game logs, replays, summaries, and graphs.
  [`comparison.toml`](../comparison.toml) is the current five-opponent default.
- [`tools/benchmarking/tournament.py`](../tools/benchmarking/tournament.py) schedules ordered bot pairs on
  selected maps. Its default discovery includes every `bots/*/bot.toml` and
  every `.map` recursively under `maps/`, including the 20 custom maps in
  `maps/new/`. Pass explicit selections for routine work. Nested map selections
  use paths relative to `maps/`, such as `new/mc26_archipelago`.

Adaptive benchmark configs keep map names as file stems by default for
backward compatibility. Set `map_name_policy = "maps_relative"` when the
campaign needs canonical nested IDs such as `new/mc26_archipelago`; the runner
then preserves those IDs in its manifest and shared game ledger.
Verified historical packaged-source aliases can be recorded in a top-level
`[source_aliases]` table. The target fingerprint must belong to a selected bot,
and the frozen campaign stores the mapping in its own `aliases.json`.

The recovered adaptive collector and ratings tools are available again as
[`tools/benchmark.py`](../tools/benchmark.py) and
[`tools/benchmark_ratings.py`](../tools/benchmark_ratings.py). The third path is
the explicit 299-bot/33-map adaptive roster in [`benchmark.toml`](../benchmark.toml).
See [the adaptive benchmark guide](adaptive-benchmarking.md) for planning,
runtime modes, map weighting and limitations. It is separate from the small
comparison default. Existing frozen campaigns are not modified by a Git merge.

The [archived guide](archive/benchmarking-legacy-campaign-20260927.md) and
[27 September pool report](benchmark-pool-20260927.md) remain historical context.

## Compare one candidate

Copy `comparison.toml` and edit its `bots`, `maps`, or `[run]` values for a
focused experiment. Paths in the TOML resolve relative to that TOML file.

```sh
uv run tools/compare_bot.py bots/hunter-v23-supported-arrival-feed --dry-run
uv run tools/compare_bot.py bots/hunter-v23-supported-arrival-feed
uv run tools/compare_bot.py bots/hunter-v23-supported-arrival-feed --config configs/avery/gauntlet.toml
```

Use `--jobs N` to override concurrency. Set `sandbox = true` in the TOML for
judge CPU limits. The default comparison writes its experiment directory under
`experiment_data/`, which is local output and ignored for new files. Use
`--resume <run-directory>` to continue a saved comparison with its frozen inputs.

## Run a bounded tournament

```sh
python3 tools/benchmarking/tournament.py \
  --bots hunter-v23-supported-arrival-feed gavroche-v66-supported-safe \
  --maps arena big_empty \
  --dry-run
```

A dry run prints the count without materializing a large schedule. Add
`--show-schedule` to print each match. Executing or printing a schedule over
10,000 matches requires `--allow-large`; full repository discovery currently
produces over two million fixtures. See the runner help for timeout,
resume, worker, and replay options.

## Share outcome data

Completed comparison games are published as small contribution Parquets under
`game_stats/runs/`. Commit new contributions when sharing results. The root
`game_stats.parquet` is a generated local union; rebuild it after merging
contributions:

```sh
uv run tools/game_stats.py rebuild
uv run tools/game_stats.py summary --output /tmp/bot-pairs.csv
```

See the [game statistics guide](../game_stats/README.md) for imports, merging,
identity fields, and conflict handling. Raw replays and run directories remain
local unless a specific artifact is intentionally shared.

## Build a statistical frontier

Freeze a round-robin config with both sides and the complete shared map bundle.
The 16-bot panel used for [`FRONTIER.md`](../FRONTIER.md) is recorded in
[`configs/frontier/all-map-panel.toml`](../configs/frontier/all-map-panel.toml).
After its campaign has no missing fixtures, run:

```sh
python3 tools/frontier_panel.py experiment_data/benchmark_<run-id>
```

The analysis selects one record per directional fixture, fits a Bradley–Terry
rating with an A-seat term, scores each map with equal opponent-lineage weight,
and bootstraps paired lineage differences for dominance. It writes a Markdown
summary and full JSON intervals under the campaign's `frontier/` directory.
Campaign data stays local by default; copy concise reviewed results into
`FRONTIER.md` or a dated report under `docs/` when sharing them.

The later September 28 expansion adds 92 candidates from Bifrost, Ed, Fenrir,
Loki, Skadi, Spike, Tidus and Yuna, including the earlier deferred Ed/Yuna arms.
Tidus t08 and Yuna x35/x36 remain deferred. Tidus t07 is an unfinished scaffold;
Loki’s duplicate directory is represented by `loki-v01`. See the current
campaign’s `roster-expansion.json` for the complete inventory.

The next September 28 expansion adds 19 versions from Jet, Ouroboros, Spike,
Tidus and Yuna, including the previously deferred Tidus t08 and Yuna x35/x36.
Yuna v05-core is an exact runtime alias of x32; development controls v04-nonb
and v05-dev-base remain excluded. All earlier runtime holds are preserved.
