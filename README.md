# Pearl seeker

A C++17 bot for [UNSW Battlecode](https://game.battlecode.au/docs), using the documented wire protocol 2.1.0.

- Searches the current 7×7 view for the nearest reachable pearl and takes one step along a shortest path.
- Explores less-visited positions when no pearl is reachable, remembering visits between turns.
- Avoids kelp and all visible dragon segments, including its own tail. Handles wrapping and portals when both ends and the destination are visible.
- When no known safe move exists, requests `SPLIT length - 2`: the parent keeps two segments and the reversed tail becomes a child running the same bot.
- Splits only at length 4 or greater and below the team unit limit. If splitting is unavailable, tries an unknown portal before a doomed move.

“About to die” means there is no immediately safe move in the current view. This is a local survival heuristic, not a guarantee: unseen portal exits, future enemy moves, and longer-term traps cannot be predicted reliably. A split consumes the entire parent turn; it does not also move the parent. The child acts later that round.

## Build and test

Open this directory in CLion as a CMake project, or run:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
```

The executable reads game input from standard input; launch it through the game toolkit rather than interactively.

## Play and package

With the official `unswbc` toolkit installed and a map available:

```sh
unswbc run path/to/arena.map . .
zip pearl-seeker.zip bot.toml main.cpp
```

Upload the ZIP as C++ on the game's Submissions page. `bot.toml` must be at the ZIP root. No external C++ dependencies or helper library are required.

Rules used: [vision](https://game.battlecode.au/docs/vision), [movement](https://game.battlecode.au/docs/movement), [splitting](https://game.battlecode.au/docs/splitting), [execution order](https://game.battlecode.au/docs/execution-order), and [wire protocol](https://game.battlecode.au/docs/protocol).
