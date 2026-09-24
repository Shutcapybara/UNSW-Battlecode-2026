# hydra-v08-claims

hydra-v07-farm-first plus the late-game length-race fix, copied from
fry-v14's behaviour:

1. **Whole-swarm farm switch at round 400** (`round >= 400 -> growth_action()`
   for every dragon) instead of v06's largest-known-dragon-only conditional
   growth. Round-limit games are won by the longest single dragon; a team of
   64 dragons where one farms while 63 brawl loses that race (help: lost on
   length both sides).
2. **`owns_pearl` gate inside `growth_action`**: the farm-mode BFS only
   targets pearls the dragon is the closest visible teammate to, so 64
   farmers deconflict instead of stampeding the same tile.

## Why

v06's round-limit losses (help 0-2, schooltime as A on length) are a
length-race problem, independent of the early numbers war v07 addresses.
fry-v14 wins both game types; its growth switch is the only structural
piece hydra lacks.

## Lineage

- hydra-v07-farm-first: parent (v06 + strength-gated gossip chases).
