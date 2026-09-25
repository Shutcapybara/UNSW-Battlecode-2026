# avery-v10-safe-explore

**Lineage:** Avery · **Parent:** `bots/avery-v09-frontier-bfs` ·
**Status:** abandoned at fixture level (never benchmarked on the full
gauntlet); superseded by v11.

## Hypothesis and changes vs v09

v09's trauma fix (+3) came with regressions on queen_of_spades, default and
devil (−8): ungated exploration marched lone starters into enemy territory
(qos side-A wiped by r49, traced). v10 gates the exploration override:

1. fires only when the threat map is empty (no visible enemy head within
   sprint reach),
2. exploration targets capped at `expl_max_dist=10` BFS steps (local sweeps,
   no cross-map marches),
3. `expl_w_heat=2.0` penalty per enemy heat in the target's zone.

## Fixture results (deterministic, vs ouroboros-v10)

- queen_of_spades A: lost r169 (v09: r49; v08: **win**) — still a regression.
- queen_of_spades B: lost r212 by elimination.
- trauma A: lost on length; trauma B: won on length (1–1).

Conclusion: gating exploration by safety does not recover v08's qos
behaviour, because the problem is not (only) danger — it is that replacing
the zone waypoint removes swarm cohesion on open maps. v11 restructures:
exploration fires only when the waypoint is BFS-unreachable (the actual
maze condition), leaving v08 behaviour intact everywhere else.
