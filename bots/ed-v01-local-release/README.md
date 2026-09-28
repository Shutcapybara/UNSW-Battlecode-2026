# Ed v01: local birth-site release

- **Lineage:** Ed, created for the 2026 temporal-policy campaign.
- **Parent:** `ed-v00-serre-control` (frozen Serre v01 source).
- **Change:** during the first seven observed turns, a dragon receives a modest
  score bonus for increasing distance from its birth cell, but only while it
  is still near that cell and the destination has at least two known or
  optimistic exits. The bonus is disabled in one-exit corridors and dead ends.
- **Hypothesis:** new dragons spread into nearby open space instead of turning
  back into a parent's pearl pocket or crowding its route.
- **Active parameters:** `birth_release=1`, `birth_release_turns=6`,
  `birth_release_radius=5`, `birth_release_weight=1.2`.
