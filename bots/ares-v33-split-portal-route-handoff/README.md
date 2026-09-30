# Ares V33 — split-time portal route handoff

V33 branches from V32 to fix the child route first seen in [match 658574](https://game.battlecode.au/visualiser?match=658574). The parent had already discovered portal 1's edge at `(4,3)`, while the child moved east after birth and later died without taking the portal route toward the pearl at `(10,32)`.

On a split, V33 broadcasts the nearest known portal edge and ID in a type-9 radio packet. A newborn accepts that endpoint at age 0 or 1, records it in its portal map, routes to the reachable side, and commits into the portal. The waypoint clears after the child crosses that edge or after 12 rounds. The message carries one edge, so this works when the parent has not yet discovered the other endpoint.

## Replay-derived verification

The V33 parent process was run persistently over the recorded parent observations from rounds 0–15. It repeated the recorded moves and, at the split, broadcast portal ID 1 / edge key 954 (`(4,3)`) in all four sonar directions. In match 658574's event stream the parent split occurs before the child's round-15 turn, and two parent-to-child sonar deliveries arrive before that turn.

On the same round-15 child observation with the original packets, V32 chooses east toward cell 858. Replacing the two deliveries with V33's packet makes V33 choose south toward cell 79, the reachable side of the known portal edge. The child was then run persistently on the replay-derived observations with those two deliveries replaced by V33's packet. The route was:

| Round | Move | Head after move |
|---:|:---:|:---:|
| 15 | S | `(4,0)` |
| 16 | S | `(4,1)` |
| 17 | S | `(4,2)` |
| 18 | S | `(4,3)` |
| 19 | W through portal 1 | `(8,33)` |
| 20 | N | `(8,32)` |
| 21 | E | `(9,32)` |
| 22 | E, collects pearl | `(10,32)`, length 3 |

This is a replay-state route simulation: other actors and map/resource events follow the saved replay, while the child follows V33's output. It establishes that the handoff and path reach the pearl in the target state. It is not a fresh full-game replay or a broad matchup result. V33 was uploaded as submission v89 (ID 12584), which the API reports active. The local candidate remains experimental and has not been admitted to `FRONTIER.md`.
