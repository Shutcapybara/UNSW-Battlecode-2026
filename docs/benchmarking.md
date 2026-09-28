# Benchmarking and comparisons

This checkout has two supported comparison paths:

- [`tools/compare_bot.py`](../tools/compare_bot.py) compares one candidate with
  an explicit TOML roster and saves game logs, replays, summaries, and graphs.
  [`comparison.toml`](../comparison.toml) is the current five-opponent default.
- [`bots/tournament.py`](../bots/tournament.py) schedules ordered bot pairs on
  selected maps. Its default discovery includes every `bots/*/bot.toml` and
  every `.map` directly under `maps/`, so pass explicit selections for routine
  work. It does not discover `maps/new/` recursively.

The previous collection-wide campaign and rating instructions are preserved in
[the archived guide](archive/benchmarking-legacy-campaign-20260927.md). The
collector and rating scripts described there are not present in this checkout.
The [27 September pool report](benchmark-pool-20260927.md) is historical
analysis and does not define today’s default roster.

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
python3 bots/tournament.py \
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
