# hydra-v03-grower

hydra-v02 plus the hunter-v03 matchup learnings. Python, protocol 3.

Progression vs hunter-v03-team-growth (all maps, both sides):
hydra-v02 9-17 -> hydra-v03 11-15.

## The key strategic idea

hunter-v03 only ever attacks a dragon that is VISIBLE-BIGGER than the
attacker (`visible_size > length`). So the swarm deliberately stays a
crowd of equals - dragons split the moment they reach 4 segments all game
- and at `freeze_round` (340) all voluntary splitting stops and every
pearl goes into the endgame length tiebreak instead. Nothing of ours is
worth assassinating until hunter's own grower window opens.

## Other changes from hydra-v02

- crown election via sonar self-reports (`am_biggest`): ties go to the
  lower id; with no fresh reports nobody claims the crown. The crown
  never splits, ignores the ally-spread term (allies are shields), adds
  `crown_caution` against any threatened tile, and flees fresh enemy
  gossip at 4x the gatherer weight - it is the assassination bait.
- emergency split now fires BEFORE the body-crash fallback when cornered
  with 4+ segments (the fallback was feeding accidental deaths).
- role phases scale with map area (an 11x11 needs ~12 rounds of scouting,
  not 110), so small-map children become foragers early.
- gatherer targeting subtracts `w_enemy_near` per tile of proximity to a
  fresh enemy sighting: feed behind the line, not on it.
- pearl choice follows hunter's foraging law (pearls far from friends are
  worth more) and non-crown dragons yield pearls to a nearer, bigger
  teammate (`w_yield`).
- committed multi-step charges (up to `attack_steps`) at visible-bigger
  enemies, mirroring hunter's signature attack, with every intermediate
  step recorded in the body trail.
