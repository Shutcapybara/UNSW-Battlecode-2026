# Kanazawa unit 3: id-ordered re-sim of team-7 wall deaths (H-KZ7, H-KZ9)

Tool: `tools/kanazawa/q_trap2.py` (60 post-m2 team-7 games sampled, 57 had wall deaths, 3,620 wall deaths; 54 s on 4 jobs).
At dragon i's move, the board is rounds[r+1] bodies for ids < i (they have moved; children born this round included) and
rounds[r] bodies for ids > i. The own neck is blocked, and so is the own tail. The engine kills a mover that enters its own tail
before the tail moves (docs/BAHAMUT_HANDOFF.md, Movement).

## Results
| measure | count | share of wall deaths |
|---|---|---|
| ≥ 1 free neighbour on the start-of-round board | 538 | 14.9 % |
| still free after the id-ordered re-sim | 91 (+7 freed by lower movers = 98) | 2.7 % |
| of the 98, the only "free" cell is the dragon's own tail (2×2 or 3-cell coil) | 85 | — |
| **free at move time, own tail excluded** | **13** | **0.36 %** |
| fatal target was kelp | 3,617 | 99.9 % |

- **H-KZ7 falsified in substance.** 99.6 % of our wall deaths had no legal cell at move time. 447 of the 538 "free-cell" deaths
  from unit 2 were cells filled earlier in the same round by a lower-id mover. Bot-model errors are at most 13 deaths in 57 games.
  This makes unit 2's "trapped, not culled" reading stronger (87 % → 99.6 %).
- **H-KZ9 (split instead of dying when trapped) is small.** 465 trapped deaths had length ≥ 4, but 349 (75 %) happened with
  our side at the 64-dragon cap, so a split was not available. 63 were at 60–63 dragons and 53 had room. The upper bound is about 1–2 saves per game.
- Side observation: 75 % of split-eligible trapped deaths happen at the cap. This leads to H-KZ10 (a congestion regime at the cap).

## New hypotheses
- **H-KZ10 (blue-sky-ish):** at the 64-dragon cap, our per-dragon-round wall hazard rises steeply (crowding traps). A lower self-imposed cap
  (for example 48) would cut deaths without cutting pearl income. Falsifier: wall hazard per dragon-round at ≥ 62 dragons is ≤ 1.3× the hazard at 40–55
  on the same maps. Cost: one corpus pass. Suits Kanazawa (measurement), then a tester switch.
- **H-KZ11 (blue-sky):** an id-order-aware safety term. A dragon should count a cell's exits net of the cells that lower-id dragons can enter before its
  next turn. The 447 "filled by a lower mover" deaths are the ceiling (12 % of wall deaths). Falsifier: in < 30 % of the 447, the dragon had an
  alternative move at r−1 with ≥ 2 exits that no lower id could reach. Cost: corpus pass at r−1. Suits Kanazawa, then Claude tester.
