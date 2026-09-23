# hydra-v01-core

First cut of the hydra family: a role-based swarm with a persistent shared
map, written in Python against protocol 3 (directional sonars + echoes).

## What it does

- **Persistent memory** per dragon process: kelp/portal edges (static, learned
  once), pearl fertility (`pearl_time >= 0` means a tile spawns), remembered
  pearls, and pearl spawn predictions from observed countdowns.
- **Roles decided at split time, encoded in the child's size**: a 2-segment
  child is a scout (chases the frontier), a 3-segment child is a hunter
  (chases known enemies, trades into much longer heads), anything else is a
  gatherer (chases pearls in safe fertile ground). Map-spawned dragons are
  gatherers.
- **Sonar gossip** on the new protocol: up to four uint64 sonars per turn.
  Packets carry a 12-bit tag (magic + payload checksum), a 4-bit kind, and a
  48-bit payload. Kinds: self report (id/pos/facing/length/role/round),
  enemy sighting, portal edge (id hash + location, so two dragons that each
  saw one end can pair it), and 6x6-block fertility digests. Heard packets
  are relayed with a TTL so facts diffuse dragon-to-dragon; a relay-stamp
  dedup keeps storms down.
- **Safety-first movement**: kelp/bodies/threat-map avoidance (enemy heads
  that act after us get a two-step reservation), flood-fill space checks,
  trap penalties, and the rule that collision checks precede movement, so
  stepping onto our own tail is always fatal and never attempted.
- **Exact own-body tracking** via the trail of head positions (one entry per
  actual move; split turns inject none), with time-aware occupancy in the
  searches: a trail cell at distance j stays blocked until future step
  k > L + 1 - j.

## Judge-budget engineering

The judge charges 100M CPU points per turn and 2.5M per stdout write; the
sandbox runs `PYTHONUNBUFFERED=1`, so a naive Python bot pays one write per
print. Accordingly:

- A turn's entire output (move, sonars, indicator) is assembled and leaves
  in a single write.
- A mid-game split child spends its first turn on a "boot turn": interpreter
  boot and imports eat most of a fresh process's first-turn budget, so it
  parses only the 3x3 around its head and takes the safest passable step.
  Initial map dragons run the full turn from round 0 (they boot before
  metered rounds begin).
- The full-map target search visits at most `bfs_cap` cells, and terrain
  step destinations are cached per cell (invalidated when a portal pairing
  completes).
- Stale memory (old spawn predictions, enemy sightings, ally reports) is
  pruned every 16 rounds.

Measured in the sandbox (`unswbc run --sandbox`): steady turns ~20-25M
points, p99 well under the 100M limit, full 500-round games on the largest
maps without metering deaths.

## Layout

- `main.py` — the whole bot; `CFG` at the top holds every tunable so
  parameter sweeps (by hand or by an LLM) only touch that block.
- `helper.py` — protocol-3 helper from `unswbc` 1.0.0 with one patch:
  `from __future__ import annotations` so it also runs on the system
  Python 3.9 used by local non-sandbox `unswbc run`.

## Results

Even with fry-v03-portal-hunters across all maps, both sides (see
`build/hydra-v01-vs-fry03*/standings.csv`): 13W-13L at the first checkpoint.
