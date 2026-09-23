# Strategy Backlog

Priorities are ordered within each tier. Combat changes must remain conservative
when enemy size or team counts are uncertain.

## P0: Combat Advantage

1. [ ] Add lead-aware equal-size kamikaze attacks. Permit an attack against a
	 visibly equal-sized enemy only when the friendly team has a confirmed unit
	 lead, the target size is reliable, and the trade improves survival or team
	 control. Preserve route, body-collision, and retreat safety checks.
2. [ ] Add significant-lead kamikaze attacks against smaller enemies. Define
	 and tune a significant unit lead using both an absolute and relative margin;
	 never trade a dragon based only on an uncertain or stale enemy count.
3. [ ] Add combat regression tests for equal-size targets with and without a
	 unit lead, and for smaller targets under ordinary versus significant leads.
	 Validate both single-step and multi-step attacks.
4. [ ] Improve enemy team-size estimates and confidence tracking so kamikaze
	 decisions distinguish visible facts, sonar reports, and stale observations.

## P1: Team Coordination And Growth

5. [x] Add directional 64-bit sonar messages for teammate position, length,
	 and round.
6. [ ] Extend sonar state with role, pearl sightings, and portal discoveries
	 without suppressing safety signals such as `MOVE_ASIDE`.
7. [ ] Add persistent estimates of the team's longest dragon and friendly
	 dragon positions and lengths, including decay and conflict resolution.
8. [ ] Tune the growth transition using round, team size, largest-dragon length,
	 pearl availability, enemy threats, and map type instead of fixed thresholds.
9. [ ] Add threat-aware endgame behavior: when no nearby enemy threat exists,
	 route pearls toward the largest friendly dragon or protect its growth
	 corridor.

## P2: Exploration And Target Selection

10. [ ] Improve portal incentives so smaller dragons explore safely while the
		largest dragon grows when appropriate.
11. [ ] Compare portal-trip reward against ordinary pearl routes before
		committing to a portal journey.
12. [ ] Compare Manhattan teammate distance with known-map route distance before
		relying on closest-dragon pearl ownership.
13. [ ] Use remembered pearl observations for scoring while treating stale or
		unseen pearls as uncertain rather than guaranteed.
14. [ ] Improve segregated-map behavior with exploration and region-ownership
		heuristics, especially on `schooltime`.

## P3: Validation And Release

15. [ ] Run the two-run small tournament workflow after each strategy change:
		focus the newest and second-newest versions against the same three-version
		pool on every map.
16. [ ] Run medium and full tournaments before submission, comparing focused
		wins, draws, losses, points, and errors.

## Versioning

- `fry-v01-danger-levels` through `fry-v10-pearl-seeker-center`: earlier
	strategy snapshots and variants.
- `fry-v11-size-aware-hunters`: baseline size-aware hunter.
- `fry-v12-stateful-size-aware-hunters`: persistent map, pearl, and enemy memory.
- `fry-v13-stateful-size-aware-2`: pearl claims over sonar messages.
- `fry-v14-stateful-size-aware-3`: closest-visible-teammate pearl ownership without explicit claims.
- `hunter-v01-team-growth`: team-length estimates and endgame growth, copied from fry-v14.
- `hunter-v02-team-growth`: adaptive growth timing; the largest known teammate has pearl priority, with a two-segment safety buffer against known enemy size.
- `hunter-v03-team-growth`: smaller dragons may safely explore completed portal trips when at least four teammates are alive.
- `kraken-v01-roles`: fixed-role scouts, hunters, and gatherers relaying map memory over sonar.
- `kraken-v02-bigmap`: big-map production and endgame growth, brawl-mode small maps, ally-head collision guards, and metered BFS with portal-local cache invalidation.

## kraken family learnings (2026-09-24 session)

- The judge sandbox is the source of truth: the same bot/native-opponent mix can diverge from local runs, so every final claim needs a `--sandbox` tournament.
- Portal-rich maps exposed the worst CPU spikes because completing a portal pairing invalidated the whole destination cache. Invalidate only the cells touching that portal edge.
- Reusable BFS stamps and a 450-cell normal-map cap keep kraken-v02 below the 100M turn budget while preserving the full 26-0 sweep over fry-v03.

## hydra family learnings (2026-09-24 session)

- Judge budget: every stdout write costs 2.5M CPU points and the sandbox
  runs python unbuffered, so a turn's output must leave in ONE write
  (including the per-turn `PROTOCOL 3` handshake line).
- A fresh split child's first metered turn must be a cheap boot turn:
  interpreter boot + imports eat most of the 100M budget; full logic on
  turn one exceeded it and the kill-restart cascade took out parents too.
- Collision is checked before movement: stepping onto our own tail is
  always fatal. The body trail must record the midway cell of sprints and
  must not append on split (no-move) turns.
- The boot turn must check the edge on OUR side of the neighbour tile
  (`get_opposite`), not the far side.
- Portal gossip cannot hash portal ids: portal-mesh maps carry ~1500 ids
  and 16-bit hashes collide into poisoned pairings.
- fry-v03 does NOT sprint broadly (95% single steps); its economy edge on
  big maps is the plan_trip beam-search harvest plus constant splitting
  (children form even under threat). hydra still loses the length race
  there ~2:1; porting the trip planner is the main hydra-v03 item.
