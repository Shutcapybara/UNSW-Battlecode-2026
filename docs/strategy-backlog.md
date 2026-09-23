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
- `fry-v14-stateful-size-aware-3`: closest-visible-teammate pearl ownership
	without explicit claims.
- `hunter-v01-team-growth`: team-length estimates and endgame growth, copied
	from fry-v14.
- `hunter-v02-team-growth`: adaptive growth timing for the largest teammate,
	with a two-segment safety buffer against known enemy size.
- `hunter-v03-team-growth`: smaller dragons may safely explore completed portal
	trips when at least four teammates are alive.
- `hunter-v04-team-state-sonar`: directional 64-bit shared dragon state.
