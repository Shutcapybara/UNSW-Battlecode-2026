# Pearl seeker

A C++17 bot for [UNSW Battlecode](https://game.battlecode.au/docs), using the documented wire protocol 2.1.0.

- Searches the current 7×7 view for the nearest reachable pearl and takes one step along a shortest path.
- Each dragon first creates one two-segment child as soon as legally possible. Children repeat this rule. Dragons below length four collect pearls until they can split; the team unit limit is respected. Normal movement and emergency splitting continue afterward.
- Explores less-visited positions when no pearl is reachable, remembering visits between turns.
- Avoids kelp and all visible dragon segments, including its own tail. Handles wrapping and portals when both ends and the destination are visible.
- Favours a four-step buffer from reachable enemy heads over contested pearls. Kelp and body segments block the approach-distance search.
- When all normal moves are threatened, can spend one segment on a two-step escape into an unthreatened visible tile with an onward exit and room to move. It checks both steps, the new neck, and the sprint cost (including a pearl collected on the first step). It conservatively treats the old tail as blocked throughout.
- When no known safe move exists, requests `SPLIT length - 2`: the parent keeps two segments and the reversed tail becomes a child running the same bot.
- Splits only at length 4 or greater and below the team unit limit. If splitting is unavailable, tries an unknown portal before a doomed move.

The bot predicts tiles other visible heads could reach in one or two moves and favours less threatened directions. These predictions only affect movement: nearby dragons do not trigger splitting. Splitting happens when no known move is available or every available move leads into a physical dead end with no visible onward exit. It ignores pearl targets covered by a dragon. A split consumes the entire parent turn; it does not move the parent or guarantee the child's survival. The child acts later that round.

## Build and test

Run the CMake commands below from the repository root.

From the repository root, build all bots with:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
```

The executable reads game input from standard input; launch it through the game toolkit rather than interactively.

The test opponent in `bots/fry-v05-kamikaze-swarm` repeatedly splits and deliberately
chases enemy heads, including short attack sprints. `bots/fry-v08-pre-swarm-defense`
preserves the main bot before these defense changes. For a manual comparison:

```sh
unswbc run maps/arena.map bots/fry-v01-danger-levels bots/fry-v05-kamikaze-swarm
unswbc run maps/arena.map bots/fry-v08-pre-swarm-defense bots/fry-v05-kamikaze-swarm
```

`tests/benchmark_swarm.py` runs both defenders on both sides of three maps using
the official engine. Run it with the Python interpreter from the installed
`unswbc` tool environment. Replays and results go to `build/swarm-benchmark/`.
Metrics include peak observed dragon length, exact final total team length,
head-on deaths, and the original dragon's death round. This is a small test
against a synthetic opponent, not a guarantee against other teams or longer sprints.

## Play and package

From the repository root, with the official `unswbc` toolkit installed and a map available:

```sh
unswbc run path/to/arena.map bots/fry-v01-danger-levels bots/fry-v01-danger-levels
(cd bots/fry-v01-danger-levels && zip ../../fry-v01-danger-levels.zip bot.toml main.cpp)
```

Upload the ZIP as C++ on the game's Submissions page. `bot.toml` must be at the ZIP root. No external C++ dependencies or helper library are required.

Rules used: [vision](https://game.battlecode.au/docs/vision), [movement](https://game.battlecode.au/docs/movement), [splitting](https://game.battlecode.au/docs/splitting), [execution order](https://game.battlecode.au/docs/execution-order), and [wire protocol](https://game.battlecode.au/docs/protocol).

## Browser extension

The [Battlecode Bot Version Filter](browser-extension/README.md) adds a bot-version
filter to your online battle history in Chrome and Firefox. See its README for
installation, usage, and verification status.
