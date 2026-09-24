# hunter-v22-frontier-exploration

V22 forks `hunter-v21-emergency-portals` and changes its no-food fallback to
favor map frontiers over teammate distance and stale pearl sightings. Revisited
tiles receive a stronger penalty, so dragons keep advancing into unknown area
instead of orbiting a familiar boundary.

V22 also assigns a small deterministic group of portal scouts when nearby
pearl opportunities cannot support much of the team. The group grows with team
size, up to four scouts; the sonar claim still coordinates non-scouts and keeps
an active trip alive. Compact-board portal policy and V21's emergency trapped
dragon escape remain in place.

In a 22-game tournament on all 11 maps with both side assignments, V22 went
9W/13L against V21 with no errors. It swept queen_of_spades, while V21 swept
default_small, devil, and stronghold. The remaining seven maps split 1–1.
Results are in [the tournament standings](../../build/hunter-v21-v22-all-maps/standings.csv)
and [match records](../../build/hunter-v21-v22-all-maps/results.json).

Build and run from the repository root:

```sh
.venv/bin/unswbc run maps/trauma.map bots/hunter-v22-frontier-exploration bots/hunter-v21-emergency-portals
```
