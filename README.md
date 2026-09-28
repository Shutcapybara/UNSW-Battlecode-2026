# UNSW Battlecode bots

Each directory under `bots/` with a `bot.toml` is a standalone bot snapshot.
Most are preserved experiment versions so comparisons can use the exact source
that was measured. See [the artifact policy](docs/artifact-policy.md),
[current status](docs/ACTIVE.md), and the family notes under `docs/` before
changing a versioned bot.

## Run a bounded tournament

The tournament runner discovers bot manifests under `bots/` and map files
directly under `maps/`. Because this repository contains hundreds of historical
bot snapshots, select a small roster explicitly:

```sh
python3 bots/tournament.py \
  --bots hunter-v23-supported-arrival-feed gavroche-v66-supported-safe \
  --maps arena big_empty \
  --dry-run

python3 bots/tournament.py \
  --bots hunter-v23-supported-arrival-feed gavroche-v66-supported-safe \
  --maps arena big_empty \
  --no-replays \
  --output build/hunter-v23-vs-gavroche-v66
```

The dry run prints the match count. Add `--show-schedule` to list matches.
Runs above 10,000 matches require the explicit `--allow-large` flag; the full
historical round robin is intentionally not a safe default. Use `--focus-bot`
with `--bots` to compare one candidate against a selected pool. Results are
saved after each match and can be resumed with the same selections and
`--resume`.

## Compare one candidate

[`comparison.toml`](comparison.toml) is the small default opponent roster for
`tools/compare_bot.py`. Copy it for a custom roster; paths inside a comparison
file are relative to that file.
Historical family-specific comparison files are grouped under
[`configs/`](configs/README.md).

```sh
uv run tools/compare_bot.py bots/hunter-v23-supported-arrival-feed
uv run tools/game_stats.py summary --output /tmp/bot-pairs.csv
```

See [the bot workflow](docs/bot-workflow.md) and
[game statistics guide](game_stats/README.md) for experiment and ledger details.

## Build and check the C++ reference set

The CMake project builds a selected set of C++ reference bots. It does not
build every snapshot in `bots/`; Python bots are packaged from their own
directories with the installed `unswbc` toolkit.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
node --test browser-extension/tests/core.test.cjs
```

CTest runs the suites registered in `CMakeLists.txt`. Several Python suites in
`tests/` are standalone and are not included in CTest.

## Play and package

```sh
unswbc run maps/arena.map bots/hunter-v23-supported-arrival-feed bots/gavroche-v66-supported-safe
unswbc submit bots/hunter-v23-supported-arrival-feed
```

For a submission ZIP, archive the contents of one bot folder with `bot.toml` at
the ZIP root. Bot README commands should be run from that bot's folder unless
they explicitly use repository-relative paths.
