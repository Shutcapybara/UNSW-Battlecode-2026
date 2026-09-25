# avery-v01-safe-swarm

**Lineage:** avery (codename Avery) · **Parent:** none — built from
`examples/bahamut-scaffold/` (`main.py` hooks + untouched `protocol.py` adapter).

## Hypothesis

Exact move simulation + flood-fill trap avoidance + tunnel lookahead + a
modest split economy beats careless swarm bots. Conservative movement
(unknown edges are walls, unpaired portals are walls) trades map coverage
for near-zero self-inflicted deaths. First baseline for the lineage; later
versions tune against the gauntlet.

## Implemented layers

- **State** (`update_state`): persistent edge map (open/kelp/portal, portal
  pairing with destination-cache invalidation), per-cell unknown-side counts,
  pearls with freshness, fertile cells with spawn-time predictions, own body
  trail (rebuilt after unpaired-portal dives), ally/enemy reports with age.
- **Encoding** (`decode_messages`, `construct_messages`): salted
  check 8 | kind 4 | payload 52 packets — SELF (id/pos/len/units/facing),
  BED (pearl bed + spawn round), ENEMY (id/pos/len), PORTAL (paired ends).
  One rotating gossip ray, self reports on the other three. Relay queue with
  TTL and 20-round dedupe.
- **Features**: enemy sprint-reach threat map, reachable-space flood fill
  (own body frees from the tail), permanent-trap (`doom`) region test with
  cyclicity check, 1-wide tunnel walk (`tunnel_ahead`: head/body/unknown
  ahead), zone enemy heat with ~30-round half-life.
- **Decision** (`decide`): one scored evaluation over simulated candidates —
  single steps, sprints (only when an enemy is near or step one eats a
  pearl), strikes with a trade margin, voluntary splits, emergency splits,
  unpaired-portal dives when idle. Terms: material, head risk, space/trap,
  doom, tunnel, exit freedom, goal progress (reverse BFS to target), ally
  traffic, crowding, anti-dither visits, sprint cost.
- **Execution** (`execute_action`): Intent -> engine MOVE (multi-letter
  sprint strings) / SPLIT; least-bad-step fallback when every option is fatal.

## Key safety rules learned during smoke tests

- Following any dragon into a 1-wide corridor is near-certain death (must
  move every turn; the cell ahead is occupied on our turn): heavy
  `w_tunnel_head`/`w_tunnel_body` penalties on entry.
- Split children are born at the parent's tail — often inside corridors:
  `split_value` rejects child exits with any tunnel occupant or doomed
  region.

## Borrowed components

Architecture pattern (module-level state, gc off, packet layout idea,
tunnel/doom/flood formulations) adapted from `bots/ouroboros-v10-beacon`
(Claude line) — re-implemented in avery's own layered structure with a
simpler role-less decision (no gather/hunt/scout/crown roles, no feeding
behaviour yet).

## Known gaps (v02 candidates)

- No roles / crown / endgame feeding; round-500 length race handled only by
  `split_stop=380` and the length-value ramp.
- No crown-kill or deliberate trading policy beyond a static margin.
- Corridor follow rules do not yet exploit ID-order (safe to follow
  lower-id allies).
- Unpaired portals are walls except idle dives; no portal exploration value.
- Sonar echoes unused.

## Results

**Baseline vs the cycle-0 gauntlet** (`comparison.toml` defaults, native,
both sides, all 11 maps; run `experiment_data/avery-v01-safe-swarm_20260925043324465527`):
**66–40–1 (62%)**, with 3 additional whole-game 600 s wall-clock timeouts
vs ouroboros-v10 on big_empty ×2 and schooltime ×1 under heavy machine
contention (runtime_faults = 0; not judge failures).

| Opponent | W–L–D | Score |
|---|---|---|
| ouroboros-v10-beacon | 8–11 (+3 timeout) | 0.42 |
| hunter-v14-cpp-hybrid-route-spacing | 14–8 | 0.64 |
| hunter-v20-portal-scouts | 11–11 | 0.50 |
| fry-v14-stateful-size-aware-3 | 17–5 | 0.77 |
| kraken-v04-eval | 16–5–1 | 0.75 |

Death attribution across completed games (candidate columns): friendly-fire
(`team_kills`) was the dominant loss source — default 237, queen_of_spades
190, devil 352 cumulative; self-collisions concentrated on corridor maps
(devil 157, queen_of_spades 157, schooltime 81). Zero invalid-action and
zero wall deaths: wire parsing and edge learning are sound. This motivated
v02's ID-order corridor discipline.

Smoke tests during development (native, single games vs ouroboros-v10-beacon):
arena W (3 rounds, vs scaffold), devil W/L on length at round 500 both
observed — high variance; devil death mix improved from 166/54/43
(dragon/self/head-to-head) to 136/53/44 after split-exit and tunnel fixes.
