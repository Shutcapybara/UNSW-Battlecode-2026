# hunter-v21-emergency-portals

V21 forks `hunter-v20-portal-scouts`. It keeps V20's time-aware pearl hotspots,
demand-based scout claim, bounded unmatched-portal probing, and compact-board
guard.

V20 assigns a portal scout when no pearl will be available within five moves:
one eligible length-3-to-6 dragon claims the role over sonar once at least four
team dragons are alive. Local food only delays scouting when multiple reachable
pearls can feed the team. Scouts limit their approach to an unmatched portal to
eight moves, and known-portal trips must have a safe return route. Compact
boards (area at most 625 tiles) skip portal scouting.

V21 adds a trapped-dragon escape: when every ordinary exit is blocked, it will
cross an adjacent portal even if no scout claimed it or the far endpoint is
still hidden. A visible landing tile must be unoccupied and outside predicted
danger. The dragon then treats the crossing as a portal trip and searches for a
return route on the next turn.

Against V20 on all 11 maps with both side assignments, V21 went 10W/12L with
no errors. It split 1–1 on ten maps and lost both Stronghold games, so this
change did not improve the overall head-to-head result. See the
[V21 vs V20 results](../../build/hunter-v21-vs-v20-all-maps/results.json) and
[standings](../../build/hunter-v21-vs-v20-all-maps/standings.csv).

Build and run from the repository root:

```sh
.venv/bin/unswbc run maps/trauma.map bots/hunter-v21-emergency-portals bots/hunter-v16-boost-traps
```
