# UNSW Battlecode bots

An experimental archive of bots, maps, benchmarking tools, and measured
results for UNSW Battlecode 2026. The repository keeps versioned bot snapshots
alongside the tooling used to compare them, so an experiment can be reproduced
from the same source and map inputs.

## What is here

- [`bots/`](bots/) contains standalone bot snapshots. Most are frozen controls;
  copy a snapshot to a new versioned directory before changing its behaviour.
- [`maps/`](maps/) contains the shared map bundle, including maps under
  [`maps/new/`](maps/new/).
- [`tools/`](tools/) contains tournament runners, comparison scripts, replay
  analysis, statistics, and campaign-specific utilities.
- [`configs/`](configs/) contains focused comparison rosters and validation
  fixtures.
- [`docs/`](docs/) records workflows, experiment protocols, family notes, and
  artifact rules.
- [`FRONTIER.md`](FRONTIER.md) is the current candidate and deployment-status
  registry.
- [`FINALS_WORKING_MEMORY.md`](FINALS_WORKING_MEMORY.md) is the compact handoff
  for the active qualifier campaign.

The repository is intentionally snapshot-heavy: it contains historical
versions used as exact experimental controls. Routine comparisons should name
an explicit bot roster and map set rather than discovering every snapshot.

## Requirements

- Python 3
- CMake 3.16 or newer and a C++17 compiler for the selected C++ reference set
- [`uv`](https://docs.astral.sh/uv/) or another environment manager for the
  Python tooling
- The `unswbc` toolkit for local game execution and optional submissions

Install the pinned Python environment used by the repository with:

```sh
uv venv
uv pip install --python .venv/bin/python -r requirements.txt
```

Some analysis and training tools have additional requirements documented beside
the tool or in the relevant file under [`docs/`](docs/).

## Build and test

The CMake project deliberately builds a selected C++ reference set, not every
bot snapshot:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
```

Additional Python tests under `tests/` can be run directly, for example:

```sh
python3 tests/test_von_neumann.py
```

## Run a bounded comparison

Start with a dry run so the fixture count is visible. The tournament runner
discovers all bot manifests and maps by default, so select a small roster for
normal development:

```sh
python3 tools/benchmarking/tournament.py \
  --bots hunter-v23-supported-arrival-feed gavroche-v66-supported-safe \
  --maps arena big_empty \
  --dry-run
```

To execute the same selection and keep output under the ignored `build/`
directory:

```sh
python3 tools/benchmarking/tournament.py \
  --bots hunter-v23-supported-arrival-feed gavroche-v66-supported-safe \
  --maps arena big_empty \
  --no-replays \
  --output build/hunter-v23-vs-gavroche-v66
```

For a candidate comparison using the default five-opponent roster, see
[`comparison.toml`](comparison.toml):

```sh
uv run tools/compare_bot.py bots/hunter-v23-supported-arrival-feed --dry-run
uv run tools/compare_bot.py bots/hunter-v23-supported-arrival-feed
```

Read [`docs/benchmarking.md`](docs/benchmarking.md) and
[`docs/bot-workflow.md`](docs/bot-workflow.md) before starting a larger
campaign. Results can be resumed with the same selections and `--resume`.

## Run or package a bot

Each runnable bot directory has a `bot.toml` at its root. With the `unswbc`
toolkit installed, a local match can be launched with:

```sh
unswbc run maps/arena.map \
  bots/hunter-v23-supported-arrival-feed \
  bots/gavroche-v66-supported-safe
```

To create a submission archive for a bot, package the contents of its directory
with `bot.toml` at the archive root. Server submission commands require your
own authenticated `unswbc` account and are intentionally not part of the
automated test suite.

## Results and generated files

Small shared result contributions live under `game_stats/runs/`. The root
`game_stats.parquet`, build output, experiment directories, replay payloads,
and local hub state are generated or machine-specific and are ignored by
default. See [`docs/artifact-policy.md`](docs/artifact-policy.md) and
[`game_stats/README.md`](game_stats/README.md) before adding experiment data.

Never commit `.battlecode-api-key`, environment secrets, replay credentials,
or generated run payloads. The local API-key file is ignored by Git.

## Further reading

- [Bot workflow](docs/bot-workflow.md)
- [Benchmarking and comparisons](docs/benchmarking.md)
- [Adaptive benchmarking](docs/adaptive-benchmarking.md)
- [Finals campaign index](docs/finals-campaign/README.md)
- [Comparison configurations](configs/README.md)
- [Bot snapshot index](bots/README.md)
