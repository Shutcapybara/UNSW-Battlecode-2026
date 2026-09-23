# Strategy Backlog

- [ ] Add persistent estimates of the team's longest dragon and friendly dragon positions/lengths.
- [ ] Tune the growth transition using round, team size, largest-dragon length, pearl availability, enemy threats, and map type instead of a fixed threshold.
- [ ] Improve portal incentives so smaller dragons explore safely while the largest dragon grows when appropriate.
- [ ] Add threat-aware endgame behavior, especially on segregated maps such as `schooltime`.
- [ ] Design compact sonar messages for teammate position, length, role, pearl sightings, and portal discoveries.
- [ ] Preserve `MOVE_ASIDE` semantics when adding state sharing.
- [ ] Compare Manhattan teammate distance with known-map route distance for pearl ownership.
- [ ] Use remembered pearl observations while treating stale pearls as uncertain.
- [ ] Compare portal-trip reward against ordinary pearl routes.
- [ ] Run small tournaments during development, then medium/full tournaments before submission.

## Versioning

- `fry-v01-danger-levels` through `fry-v10-pearl-seeker-center`: earlier strategy snapshots and variants.
- `fry-v11-size-aware-hunters`: baseline size-aware hunter.
- `fry-v12-stateful-size-aware-hunters`: persistent map, pearl, and enemy memory.
- `fry-v13-stateful-size-aware-2`: pearl claims over sonar messages.
- `fry-v14-stateful-size-aware-3`: closest-visible-teammate pearl ownership without explicit claims.
- `hunter-v01-team-growth`: team-length estimates and endgame growth, copied from fry-v14.
- `hunter-v02-team-growth`: adaptive growth timing; the largest known teammate has pearl priority, with a two-segment safety buffer against known enemy size.
- `hunter-v03-team-growth`: smaller dragons may safely explore completed portal trips when at least four teammates are alive.
