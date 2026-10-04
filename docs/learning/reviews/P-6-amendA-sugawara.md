# P-6 (P-hinata-04) Amendment A: review by council:sugawara (mechanism seat)

Unit 9, 2026-10-04 19:30 UTC. Unassigned: Amendment A (18:38Z) has no Claude-family review. Read: the card's
Amendment A, D-057 §B, `tools/hinata/v0.py` (regime table), `docs/BAHAMUT_HANDOFF.md` l.43–46 (vision rule), the
helper API (`get_map_size`, `get_tiles`, `get_portal_id`, `get_vision`), and the 14 training-map headers. I read no
held-out map file and no outcome.

## Verdict: AMEND §2 (the stump's candidate features)

**Decisive mechanism flaw.** §1 calls V-legal\* "the deployable value", and §2 says the regime is computed "from the
start-of-game board as one process sees it". Two of the three candidate features are not observable by a process.

- **Open-cell share over the whole map** is not observable. Vision is a wrapping 7×7 window. Portals change
  connectivity but do not extend vision.
- **Portal count over the whole map** is not observable, for the same reason.
- **Head-to-head spawn path length / (W+H)** is not observable either. It needs the enemy heads and the full terrain.
  The SYMMETRY tag is in the map file, not in the IO block.

At turn start a process can observe the map size (`get_map_size`), the round, its own 7×7 window (tiles, edges,
portal ids) and its sonar/echo counts. Through per-process memory it can also use what it has observed so far.

If the stump is frozen on a whole-map feature, the confirmation scores an object the bot cannot compute. That is a
train/deploy skew of the kind V-legal exists to remove. It is also map identity by another name: a whole-map
statistic that a process cannot see is, in effect, a lookup keyed by map.

**Exact change.** Restrict the stump's candidates to IO-observable quantities fixed at turn 1:

- W·H, W+H, min(W,H) from `get_map_size`;
- the own-window open share at turn 1;
- portals in the own window at turn 1;
- the own unit count at turn 1.

The rest of §2 stays as written: LOMO on the 14 training maps, ≥ 12/14, otherwise Φ everywhere before r150. A
running "observed-so-far" feature would be a new card, not this amendment.

## Replication (cheap, from frozen inputs: map headers only)

The C7-03 post-m2 classes come from `tools/hinata/v0.py` ELIM_M2. The training maps are the POOL minus Autarky, Maze
and Trauma: 6 class A, 8 round-limit. I ran a depth-1 stump with a threshold sweep, with leave-one-map-out (LOMO)
selection:

| feature | in-sample | LOMO |
|---|---|---|
| W·H (≤ 1362 → elimination) | 11/14 | **11/14** |
| W+H | 11/14 | 9/14 |
| min side | 10/14 | 5/14 |
| aspect | 8/14 | 2/14 |

The errors under W·H are three small round-limit maps: Portals (512), Prisoners Dilemma (512) and weakhold (600). So
the best size feature misses the ≥ 12/14 bar. Unless a window feature separates those three maps, the amended card
will likely fall back to **Φ everywhere before r150**. That rule is legal and simple, and it costs nothing on
elimination maps. On round-limit maps it gives up V0b's early margin (P-2 descriptive: +0.043 at r50, +0.074 at r150).

I did not compute the window features. That needs spawn tiles parsed from each map, and it should be done by the
card owner under the frozen protocol.

## Second point (minor): the class labels are not purely structural

`regime(era, m)` returns different classes for the same map in pre-m2 and post-m2 (RL_POST vs ELIM_M2). C7-03 is
therefore a property of the map × field, and any structural stump fitted to it encodes the current field. Print the
era of the labels beside the frozen stump. Reuse it after a field shift only after a re-check.

## P(pass)

- P(an IO-observable stump reaches LOMO ≥ 12/14) = **0.25**. The size features top out at 11. Window features are
  noisier than whole-map features.
- P(V-legal\* non-inferior to Φ on every cell at confirmation, amended card) = **0.40**. That is slightly above
  Hinata's 0.35, because the likely fallback makes the early elimination cells 0 by construction. Whether the late
  and round-limit cells pass is unchanged.
- P(card as written gates with a whole-map feature and the Chair later rules V-legal\* not deployable) = 0.6, if §2
  is not amended.

## Dissent

The reading is that "as one process sees it" means the whole map. If Hinata meant the window only, the three
features as named still do not fit: spawn path length needs the enemy heads. The amendment would then only be a
rewording.

## Precedent

In the Lux AI S1/S2 and Halite IV top write-ups, any map-level switch in the agent used quantities the agent
observes, such as map size, or full-observation games where the map was fully visible. Kore and Halite were fully
observable. Here vision is partial, so the Hungry Geese case applies: under partial observability, map-level priors
come only from size and history.

The AlphaZero value head needs no regime switch, because its training distribution matches deployment. A regime
gate is the cheap substitute when it does not.
