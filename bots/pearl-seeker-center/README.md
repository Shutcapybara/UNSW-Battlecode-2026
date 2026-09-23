# Pearl seeker

This fork preserves the original bot's behavior while making unexplained
exploration prefer the map center and positions farther from visible kelp.

A C++17 bot for [UNSW Battlecode](https://game.battlecode.au/docs), using the documented wire protocol 2.1.0.

- Searches the current 7×7 view for the nearest reachable pearl and takes one step along a shortest path.
- Each dragon first creates two children as soon as legally possible, splitting off two segments per child (one child per turn). Children repeat this rule. Dragons below length four collect pearls until they can split; the team unit limit is respected. After these two children, normal movement and emergency splitting continue.
- Explores less-visited positions when no pearl is reachable, remembering visits between turns.
- Avoids kelp and all visible dragon segments, including its own tail. Handles wrapping and portals when both ends and the destination are visible.
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

## Play and package

From the repository root, with the official `unswbc` toolkit installed and a map available:

```sh
unswbc run path/to/arena.map bots/pearl-seeker-center bots/pearl-seeker-center
(cd bots/pearl-seeker-center && zip ../../pearl-seeker-center.zip bot.toml main.cpp)
```

Upload the ZIP as C++ on the game's Submissions page. `bot.toml` must be at the ZIP root. No external C++ dependencies or helper library are required.

Rules used: [vision](https://game.battlecode.au/docs/vision), [movement](https://game.battlecode.au/docs/movement), [splitting](https://game.battlecode.au/docs/splitting), [execution order](https://game.battlecode.au/docs/execution-order), and [wire protocol](https://game.battlecode.au/docs/protocol).
