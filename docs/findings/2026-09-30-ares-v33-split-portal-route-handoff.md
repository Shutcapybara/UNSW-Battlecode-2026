---
id: 2026-09-30-ares-v33-split-portal-route-handoff
author: gpt/codex/2026-09-30
kind: experiment
title: Ares V33 hands a known portal edge to a newborn and reaches the pearl
task: Route the V28 replay child through the parent's known portal endpoint
supersedes: ""
evidence:
  - Public match replay 658574 and local decoded review at build/match-658574/review/658574.decoded.json
  - V33 parent run over the recorded round-0–15 observations
  - Replay-state simulation of the newborn with the split-turn radio deliveries replaced by V33's portal packet
---

# Ares V33 — split-time portal route handoff

## Issue and change

In [match 658574](https://game.battlecode.au/visualiser?match=658574), the split child moves east from `(4,34)` while the parent has already seen portal 1's entry edge at `(4,3)`. The child later sees the pearl at `(10,32)` on the far side but does not use the portal route.

V33 branches from V32. On a split, the parent selects the nearest known portal edge to the child head and sends its edge key and portal ID in a type-9 packet. This carries only one endpoint, which is enough to give the newborn a route even when the parent has not learned the complete pair. Newborns accept the edge at age 0 or 1, target a reachable side cell, and commit through it. The route is cleared after transiting the specified edge or after 12 rounds.

## Replay-derived verification

A single persistent V33 process received the recorded parent observations from rounds 0 through 15. It repeated the recorded parent moves and split at round 15. Its split-turn sonar packet was type 9, with portal ID 1 and edge key 954, corresponding to `(4,3)`, and was sent in all four directions.

The match event order confirms that the parent split event is followed by its sonar events, then the newborn's round-15 turn. The original replay has two parent-to-child sonar deliveries before that first child action. On the same round-15 child observation with the original packets, V32 chooses east toward cell 858. With the two deliveries replaced by V33's edge packet, V33 chooses south toward cell 79, the reachable side of the known edge. The child process stayed alive across the replay-derived turns and chose:

| Round | Move | Head after move | Result |
|---:|:---:|:---:|:---|
| 15 | S | `(4,0)` | Starts toward the parent's known portal edge |
| 16 | S | `(4,1)` | Continues to entry |
| 17 | S | `(4,2)` | Continues to entry |
| 18 | S | `(4,3)` | Reaches portal 1 |
| 19 | W | `(8,33)` | Crosses portal 1 |
| 20 | N | `(8,32)` | Moves toward pearl |
| 21 | E | `(9,32)` | Moves toward pearl |
| 22 | E | `(10,32)` | Collects the pearl; length becomes 3 |

This confirms the requested route in the target replay state: the child takes the parent's known endpoint, transits the portal, and collects the far-side pearl. The child movement is simulated from replay observations; the other actors and environment events are held to their recorded replay events. This target-case check is not a fresh full-match run. V33 was uploaded as submission v89 (ID 12584); the API reports it active. It remains experimental and outside `FRONTIER.md` locally.


## Four-version live-map screen

After submission, V33 was compared with V32, V28, and V19 using unswbc 1.2.2,
seed 1, sandbox execution, all ten live maps, every pairing, and both seats.
The 120-game run had no draws or runner errors. Records were V33 33–27, V32
32–28, V28 30–30, and V19 25–35. Direct results were V33–V32 10–10,
V33–V28 11–9, V33–V19 12–8, V32–V28 11–9, V32–V19 11–9, and V28–V19 12–8.
V33 swept Queen of Spades and scored 5–1 on Slithery Fight across its three
opponents, but lost all six Default games. Thus its overall lead over V32 is
one win and their direct matchup is even; this one-seed screen does not pass
the broader promotion gate. V33 remains experimental locally. The manifest,
standings, results, and logs are in
`build/ares-v33-v32-v28-v19-live10-seed1-20260930/`; no replays were saved.
