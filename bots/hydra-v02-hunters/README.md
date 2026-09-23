# hydra-v02-hunters

hydra-v01-core plus a combat layer and big-map tuning. Python, protocol 3.

## What changed from v01

- **Trade discipline** (the attack layer): strikes into an adjacent enemy
  head only when the trade clearly favours us — the enemy is much longer
  (they drop more pearls), we are an expendable scout with a big team
  behind us, or we outnumber them. Hunters sprint: a straight second step
  through clear, unthreatened tiles while closing on fresh prey (the
  midway cell is recorded so the body trail stays exact).
- **Big-map awareness**: team-size target scales with map area; a
  fertility-block waypoint (own sight + sonar gossip) steers gatherers
  past the BFS horizon when nothing near scores.
- **Growth transition**: at `grow_after` the team stops expanding and only
  replaces losses below `grow_floor` — pearls go into length for the
  endgame tiebreak (longest dragon wins), instead of endless shrimp.
- **Portal gossip at full width**: portal ids travel unhashed in sonar
  packets (32 bits). On portal-mesh maps (big_empty/help carry ~1500
  portals) the old 16-bit hash collided constantly, poisoning or losing
  most pairings.
- **Boot-turn edge fix**: the newborn's first step checks the edge on our
  side of the neighbour tile (`get_opposite`), not the far side — v01
  newborns could step across kelp and die on spawn.

## Known gap vs fry-v03-portal-hunters

On portal-heavy large maps fry still out-farms us (measured: ~2x split
activity on big_empty, so roughly double the pearl intake). Their beam
search plans portal round-trips explicitly; hydra treats portals only as
shortcuts inside the ordinary target search. Closing that gap is the main
hydra-v03 item.
