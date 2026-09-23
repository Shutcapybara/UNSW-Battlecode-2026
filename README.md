# UNSW Battlecode bots

All committed branch strategies live together on `main`. Each directory under
`bots/` is a standalone bot with its own source and `bot.toml`.

| Folder | Source |
| --- | --- |
| `bots/pearl-seeker` | Original main / v5-single-child branch tip (two-child strategy) |
| `bots/danger-levels` | v13-danger-levels; also the root bot on dragon-hunter |
| `bots/dragon-hunters` | dragon-hunter |
| `bots/portal-hunters` | Dragon hunters with planned pearl-collecting portal round trips |
| `bots/escorts` | dragon-hunter variant |
| `bots/kamikaze-swarm` | dragon-hunter variant |
| `bots/one-child` | dragon-hunter variant |
| `bots/two-children` | dragon-hunter variant |
| `bots/pre-swarm-defense` | dragon-hunter variant |
| `bots/pearl-seeker-center` | zach |

The original branches and existing stash are retained. The stash is unfinished
work and is not applied to these committed snapshots. Maps, browser extension,
and shared test tools remain at the repository root.

## All-bot tournament

Run every bot against every other bot on every map, with sides swapped:

```sh
python3 bots/tournament.py
```

The script discovers `bots/*/bot.toml` and `maps/*.map` automatically. With 10
bots and 11 maps, it runs 990 matches, excluding self-matches. By default it
runs up to four matches concurrently, capped at the detected CPU count. Set
`--jobs 8` (or `-j 8`) for eight simultaneous matches, or `--jobs 1` for a
sequential run. Each worker has its own bot builds and reuses them across
matches. Each run gets a new folder under `build/tournament-TIMESTAMP/` with
replays, match logs, `results.json`, and a `standings.csv` leaderboard. Wins
earn 3 points and draws 1; failed matches are recorded separately and do not
count as losses. Results are saved after every match, and failures do not stop
the remaining matches. The script exits with status 1 if any matches failed.

Preview the schedule, or run a smaller selection:

```sh
python3 bots/tournament.py --dry-run
python3 bots/tournament.py --bots dragon-hunters portal-hunters --maps arena queen_of_spades
python3 bots/tournament.py --jobs 8 --output build/all-bots-parallel
```

To test one bot against every other bot on every map, with sides swapped:

```sh
python3 bots/tournament.py --focus-bot portal-hunters --jobs 8 --output build/portal-hunters-tournament
```

This runs 198 matches with the current 10 bots and 11 maps. `--maps` still
limits the maps; `--bots` limits the participating bots and must include the
focus bot. Resume with the same `--focus-bot` setting. In this mode, opponents
only play the focus bot, so leaderboard point totals cover unequal match counts.

For a full tournament with a chosen output folder:

```sh
python3 bots/tournament.py --output build/all-bots
python3 bots/tournament.py --output build/all-bots --resume
```

Resume skips successful matches and retries failed ones. Use the same bot/map
selection and replay settings; changed source files, maps, or runner scripts
require a fresh results folder to avoid mixing versions. The `--jobs` setting
can change when resuming. Ctrl+C stops all running matches and preserves saved
results. Add `--no-replays` to reduce
disk usage or `--timeout 300` to change the default 180-second match timeout.

## Build and test all bots

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
node --test browser-extension/tests/core.test.cjs
```

## Play and package

Choose bot folders explicitly with the installed `unswbc` toolkit:

```sh
unswbc run maps/arena.map bots/dragon-hunters bots/pearl-seeker-center
unswbc submit bots/dragon-hunters
python3 bots/compare.py
```

For a submission ZIP, archive the contents of the chosen bot folder with
`bot.toml` at the ZIP root. Bot README commands should be run from that bot's
folder unless they explicitly use repository-relative `bots/` paths.
