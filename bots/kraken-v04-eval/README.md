# kraken-v03-judge-safe

Fresh-build role-based swarm on protocol 3 (directional uint64 sonars +
echoes), self-contained in one `main.py` (no helper import, lean parsing,
one stdout write per turn).

## Design

- **Roles encoded in split size**: 2-segment child = scout (frontier
  exploration + radar), 3-segment = hunter (chases sightings, sprint-strikes
  enemy heads), anything larger = gatherer (pearls in safe fertile ground).
  Map-spawned dragons are gatherers.
- **Persistent memory per dragon process**: kelp/portal edges (static once
  seen, portal pairing with cache invalidation), pearl beds with spawn
  predictions from observed countdowns, remembered pearls, enemy sightings,
  ally self-reports.
- **Radar sonar policy**: one rotating directional sonar per turn. Echo
  counts are aggregated over all sonars sent in a turn, so a single cast is
  the only way to attribute an echo to a direction. The cast doubles as the
  gossip carrier (self reports, enemy sightings, portal edges, pearl beds,
  relayed with TTL + dedup).
- **Combat**: stepping onto the tile an enemy head currently occupies kills
  both dragons and cannot be dodged (our MOVE resolves atomically), so
  hunters and scouts sprint-strike up to 3 steps when the trade is
  favorable; everyone strikes in the endgame. Later-acting enemies (higher
  id) get a 3-step threat reservation; already-moved enemies only own their
  head tile.
- **Safety**: exact own-body tracking via the head trail (collision is
  checked before the tail moves, so every body tile is fatal for step 1),
  flood-fill trap checks, kelp/portal-aware BFS compass with capped
  expansion.

## Judge budget

Boot turn for mid-game split children (interpreter boot eats the first-turn
budget), one buffered write per turn, BFS capped at `bfs_cap` cells, stale
memory pruned every 16 rounds.

## Tuning

All knobs live in the `CFG` dict at the top of `main.py`.


## kraken-v04-eval

base: kraken-v03-judge-safe; params: unchanged
hypothesis: parameterisable eval baseline; behavior identical to v03
