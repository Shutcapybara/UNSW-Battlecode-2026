# Portal hunters

A standalone variant of `dragon-hunters`. Between portal trips it retains the
original attacks, swarm splitting, friendly face-off sonar, and exploration.

Before crossing a portal, it searches for a complete route that approaches the
entrance, collects pearls, returns through the same portal's far endpoint, and
continues for two clear moves beyond the exit. It prefers more pearls, breaking
ties in favour of shorter trips. Spawn countdowns count toward collection only
when the pearl should be available by arrival; a positive countdown cannot
produce a pearl on the current turn's first move. Movement loops can delay
arrival until a pearl spawns. Each pearl is counted once per plan.

A committed trip takes priority over attacking and splitting, including while
approaching the entrance and moving clear of the exit. The bot moves one tile
per turn and rechecks its remaining route against every new observation. If a
route is disrupted while inside, it searches for a short return route. If none
is currently verifiable, it chooses a local survival move and retries next
turn; emergency splitting remains possible when no movement is available.

The planner accounts for growth and the space occupied by its simulated body.
Observed own-body segments are conservatively reserved for a full grown body
length, since the input does not order them. Other observed bodies stay blocked.
Tiles within two moves of a visible enemy head are excluded from planned trips.
Ordinary hunter moves cannot enter portals without a checked trip.

Planning is bounded to 18 moves and 256 candidates per depth, retaining several
alternatives at each position and trip stage. This seeks a high pearl yield;
it is not an exhaustive proof of the maximum. Both portal ends and every route
tile must be visible. Unknown destinations are not assumed safe, and moving
enemies or newly revealed obstacles can still disrupt a trip. The exit is
checked against current knowledge, not guaranteed against future enemy moves.

From the repository root:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target portal_hunter
ctest --test-dir build -R portal_hunter --output-on-failure
unswbc run maps/queen_of_spades.map bots/portal-hunters bots/dragon-hunters
unswbc submit bots/portal-hunters
```
