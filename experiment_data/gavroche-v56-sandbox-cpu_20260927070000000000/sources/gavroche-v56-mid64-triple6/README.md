# Gavroche V56 midgame search with bounded triples

Parent: V54. Restore a 64-node target search cap during rounds 40–149, and
limit three-step candidates to bodies of length 4–5 from round 40 onward.
Preserve V54's post-round-150 48-node cap and sparse late restoration.

The separate sparse sprint threshold keeps the length-6/7 paths disabled during
the midgame window even if the team temporarily falls below 20 units.
