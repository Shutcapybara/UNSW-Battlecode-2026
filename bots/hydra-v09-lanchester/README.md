# hydra-v09-lanchester

hydra-v08-claims plus **retreat-while-outnumbered** (Lanchester discipline):

1. `enemy_estimate()`: fresh enemy contacts (visible sightings + gossip,
   <=15 rounds). A lower bound on their swarm; overcounting just deepens
   farm mode.
2. While `units < enemy_estimate()`: voluntary attacks are disabled and the
   forage BFS scores cells away from fresh enemy positions
   (`-8 * max(0, 10 - away)`, the stalker-flee term generalised).
3. At or above parity: behaviour identical to v08 (hunt as usual).

## Why

Colloseum autopsies (8/8 losses to fry-v14 across four independent runs)
show the collapse mechanism: every head-to-head is a MUTUAL kill, so kills
stay symmetric in absolute terms (8=8, 13=13) while the smaller swarm loses
a proportionally larger fraction of its population each time. Per-capita
feeding and trade initiation are equal; the loser collapses because it
keeps walking its few dragons into the winner's traffic. hunter-v03 (the
base hydra forked) loses to fry-v14 the same way (79:29 pearls, 31:12
splits on Colloseum), so this is inherited, not caused by hydra's sonar
layer.

While behind, short dragons (2-3) are invisible to fry-style offense
(only bigger heads get attacked) — evasion drops our kill rate to ~0 while
births continue, letting the swarm catch up. At parity the mutual kills
hurt both sides equally and our attack doctrine resumes.

## Lineage

- hydra-v08-claims: parent (v07 + fry-style whole-swarm growth at r400
  with owns_pearl deconfliction).
