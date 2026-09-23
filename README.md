# UNSW Battlecode bots

All committed branch strategies live together on `main`. Each directory under
`bots/` is a standalone bot with its own source and `bot.toml`.

| Folder | Source |
| --- | --- |
| `bots/pearl-seeker` | Original main / v5-single-child branch tip (two-child strategy) |
| `bots/danger-levels` | v13-danger-levels; also the root bot on dragon-hunter |
| `bots/dragon-hunters` | dragon-hunter |
| `bots/escorts` | dragon-hunter variant |
| `bots/kamikaze-swarm` | dragon-hunter variant |
| `bots/one-child` | dragon-hunter variant |
| `bots/two-children` | dragon-hunter variant |
| `bots/pre-swarm-defense` | dragon-hunter variant |
| `bots/pearl-seeker-center` | zach |

The original branches and existing stash are retained. The stash is unfinished
work and is not applied to these committed snapshots. Maps, browser extension,
and shared test tools remain at the repository root.

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
