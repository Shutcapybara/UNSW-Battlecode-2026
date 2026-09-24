# Bot design framework

> **Superseded (2026-09-25)** by `docs/macro-spec.md`, the four-line
> evidence-based build spec. This document remains as the hydra series'
> original theory; its §5 "pearl draws are seeded per invocation" claim is
> wrong for the local runner (deterministic per (map, botA, botB) — see
> `docs/cross-line-review.md` §1).

The shared theory of the hydra (and, by observation, kraken) series. The
iteration loop (`tools/evolve.py`, `tools/autopsy.py`) exists to serve this
framework; every change should be expressible inside it.

## 1. The core loop of a dragon

Every dragon, every turn, runs the same five stages:

1. **Perceive** — fold the 7x7 window into persistent memory. Terrain
   (kelp/portal edges) is static and learned once; pearls, spawn
   predictions, enemy sightings and ally self-reports are dynamic and
   expire. Beyond the window, knowledge comes from sonar gossip.
2. **Model** — compress memory into potential fields over the whole map:
   a pearl-value field (pearls now, spawns soon, fertility camping), a
   threat field (enemy head reach, hard and soft), a frontier field
   (unseen tiles), an ally-claim field (who owns which food). Fields are
   the map-control abstraction: "space control" is just the sum of fields.
3. **Generate** — enumerate legal actions, chess-style movegen: single
   steps that are not kelp, not any current own-body tile (collision is
   checked before movement), not another dragon's part; plus gated
   multi-step sprints whose every intermediate tile is also legal.
4. **Evaluate** — score each candidate with the linear evaluation
   function (section 3) and take the argmax (with a tiny per-dragon
   jitter to break lockstep).
5. **Broadcast** — sonars out after the action: status, gossip relay,
   radar (echoes come back next turn).

Splitting is not part of the loop: it is a *policy* decision (who
reproduces, when) that preempts the loop for one turn.

## 2. Roles

Roles are decided at creation and encoded in the split size (zero latency,
un-fakeable): a 2-segment child is a **scout**, a 3-segment child is a
**hunter**, larger children and map-spawned dragons are **gatherers**.
One dynamic role is elected at runtime: the **crown** — the largest known
living dragon after the freeze round, whose only job is to survive and
grow for the endgame length tiebreak.

The unifying idea: **a role is a weight vector, not a code path.** All
roles run the same evaluation function; scouts load frontier-heavy
weights, hunters load enemy-attraction and trade weights, gatherers load
pearl-field and space weights, the crown loads survival weights (danger
and trap terms multiplied up, split forbidden). Roles are like chess
phases (opening / middlegame / endgame): same movegen, same eval, tuned
weights.

## 3. The evaluation function

Like a chess eval: `E(a) = Σ wᵢ · fᵢ(a)` over per-action features, with
hard legality as a filter, not a term. Features (all bounded and cheap
enough for the 100M-point turn budget):

**Material (immediate)**
- `pearl` — a pearl on the landing tile
- `spawn_soon` — predicted spawn on/near the landing tile, scaled by
  countdown freshness
- `trade` — landing tile is an enemy head we want dead (size-gated; a
  mutual head-to-head is a trade of our length for theirs plus the pearls
  their body drops)

**Position (field gradients, from one capped BFS)**
- `pearl_field` — value of the best reachable pearl/spawn target through
  the chosen step, minus distance cost
- `frontier_field` — unseen-tile attraction (scouts multiply)
- `enemy_field` — attraction to fresh, outsize enemy sightings (hunters;
  repulsion for gatherers/crown)
- `ally_claim` — penalty for food a nearer/bigger teammate owns

**Safety (survival is lexicographic, approximated as large weights)**
- `danger` — landing inside the hard threat reservation (enemy sprint
  reach); `soft_danger` for the outer ring
- `space` — flood-fill freedom after the step, capped at length+slack;
  `trap` cliff when space < length
- `exits` — onward-move count from the landing tile
- `body_time` — time-aware own-body occupancy: a trail cell at distance j
  is lethal until step k > L + 1 - j

**Tempo / noise**
- `momentum` — small facing bonus (anti-dither)
- `visits` — per-visit penalty (exploration decay)
- `jitter` — seeded per dragon id (breaks lockstep without randomness)

Design rules: every feature is dimensionless and bounded (usually 0..1 or
a capped count); every weight lives in `CFG` so sweeps only touch that
block; adding a feature never changes movegen; role differences are
weight differences.

## 4. The iteration loop (between games)

```
   observe ──▶ hypothesis ──▶ weight/code change ──▶ versioned bot dir
      ▲                                                   │
      │                                                   ▼
   improve ◀── keep/drop decision ◀── arena ◀── (repeat x2: seeds vary)
                    │
                    └──▶ autopsy losses ──▶ new hypothesis
```

- **Arena**: `tools/evolve.py arena <bot>` runs both-sides focus
  tournaments against a pool and aggregates W-D-L per opponent. Runs are
  tagged and appended to `build/evolve/INDEX.md` so versions are
  comparable across time. Repeat a run before trusting a small delta:
  pearl seeds differ per invocation.
- **Autopsy**: `tools/autopsy.py <a> <b> --map m` plays one verbose match
  and reports outcome, death causes per team, unit and max-length curves,
  split counts — the difference between "we died" and "we starved".
- **Versioning**: every kept change is a new `bots/<name>-vNN-<trait>/`
  directory, committed with its result in the message. Dropped
  experiments are deleted; their lessons go in the README or
  `docs/strategy-backlog.md`.
- **Baseline pool**: `hunter-v03-team-growth` (the given target),
  `fry-v14-stateful-size-aware-3` (field leader), `kraken-v03-judge-safe`
  (rival series — benchmark against, never modify), plus the previous
  hydra version.

## 5. Known engine facts that shape everything

- Collision checks precede movement: own tail tile is always fatal; the
  trail records sprint midways and never appends on split turns.
- 100M CPU points per turn; every stdout write costs 2.5M points; one
  buffered write per turn including the `PROTOCOL 3` handshake.
- A fresh split child's first turn is a boot turn (interpreter start
  eats the budget); initial map dragons boot before metered rounds.
- Pearl draws are seeded per invocation: single games mislead.
- Turn order is ascending id: lower ids act on staler world state in
  contacts; higher ids get wider threat reservations.
