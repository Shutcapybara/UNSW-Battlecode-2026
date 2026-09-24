# hydra-v06-echo

The hunter-killer: hunter-v03-team-growth forked onto protocol 3, keeping its
whole battle-tested core (portal trips, spread foraging, designated grower,
size-gated multi-step attacks) and adding the sonar layer it never had.

Beats hunter-v03-team-growth 13W-2D-11L over all maps, both sides
(three consecutive identical results; `build/hydra-v06-vs-hunter03-r*/`).

## What the fork adds

- **Protocol 3 output**: the team-status sonar fires in all four directions
  instead of one - four times the teammate reach for the same free action -
  plus the per-turn `PROTOCOL 3` handshake, and the engine now returns
  `ECHOES` counts every turn.
- **Enemy gossip over sonar**: when a dragon sees an enemy of 3+ visible
  segments, the biggest and second-biggest fresh sightings ride the east and
  south sonar slots (tag 01 in the top bits: x, y, size, round).  Every
  dragon that hears it gains a pack target, and `attack_path` will route to
  gossip positions that outsize the attacker - coordinated hunting that
  hunter-v03 cannot do.  Gossip is only trusted for 15 rounds, and only
  chased within 6 path steps: far chases starve.
- **Echo radar for the grower**: when the echo says an enemy HEAD stands on
  one of the grower's rays and no enemy head is visible nearby (the stalker
  case), growth targets are biased away from every recently seen enemy
  position.
- **Status messages carry x/y** (into `FriendlyMemory.position`), parsed and
  kept fresh for two rounds.  Deliberately NOT wired into nearest-friend
  spread or owns_pearl yielding: map-wide yielding starved the richest maps
  (big_empty flipped from 2W to 2L when it was on) - the fields remain for
  future use with a distance-aware rule.

## Lineage

- hydra-v01/v02/v03: the python family (roles, gossip map, judge-budget
  engineering). v03 beats hunter-v03 11-15; kept as benchmarks.
- hydra-v06: the C++ fork that actually takes the crown.
