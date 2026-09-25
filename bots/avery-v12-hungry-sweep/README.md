# avery-v12-hungry-sweep

**Lineage:** Avery · **Parent:** `bots/avery-v11-maze-sweep` ·
**Status:** abandoned at fixture level (never gauntlet-run).

## Hypothesis and change vs v11

v11's sweep preempted the waypoint on open maps because "waypoint
BFS-unreachable" is not maze-specific. The actual trauma signal is
starvation (37 pearls in 500 rounds). v12 gates the sweep by hunger: it
fires only when the waypoint is unreachable AND this dragon has not grown
for `starve_rounds` (length growth is observed directly from the
observation stream; newborns get a full grace period). Fed dragons keep
exact v08 behaviour.

## Fixture results (deterministic)

`starve_rounds=60`: qos-A **won** (v08 behaviour restored), devil-A won,
schooltime-A won — but trauma-A and trauma-B both lost on length (v11 won
trauma-B).

`starve_rounds=100`: trauma-A/B still lost; qos-B won; devil-B vs tew lost
(already lost in v08).

## Why abandoned

Corner-trapped dragons on trauma eat a trickle (a pearl every <100 rounds),
which resets the hunger timer, so the sweep never fires often enough to
expand territory. The v09/v11 trauma wins came from *fed* dragons sweeping
too — collective coverage, not individual hunger. Gating exploration by
individual hunger removes exactly the coverage that made it work.

## Exploration-line summary (v09–v12, all rejected)

The frontier sweep reliably fixes trauma (+3) and reliably costs more
elsewhere (−3 to −8) whenever it preempts v08's zone-waypoint behaviour on
open maps. No gate tried (threat-map-empty, distance cap, zone heat,
waypoint-unreachability, individual starvation) separated the two regimes.
Remaining untried: team-level starvation signals via sonar gossip, or a
bed-camping role (park beside slow beds) instead of sweeping. The tip
remains v08.
