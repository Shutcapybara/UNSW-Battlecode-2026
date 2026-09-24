# hydra-v10-farmclean

hydra-v08-claims with the **stalker-flee term removed** from
`growth_action()`.

## Why

The v06 echo-radar stalker-flee biased the (single) grower away from
recently seen enemy positions. With v08's whole-swarm farm switch
(`round >= 400 -> growth_action()` for everyone), the same term became a
map-wide reflex: every farmer avoided pearls near fresh enemy sightings.
On maps where the contested food sits near the enemy — big_empty (lost
0-2 under v08/v09 after v06/v07 won/split it) and schooltime (0-2) — that
hands the rich middle to fry-v14, which farms without the reflex.

v10 keeps: v07's strength-gated gossip chase, v08's round-400 whole-swarm
farm switch with `owns_pearl` deconfliction. Drops: stalker-flee.

Note: fry-v14 beats every bot in the field on Colloseum/Colosseum
(including its own v03), so those 4 screen games are treated as the
field's tax, not a hydra-specific deficit.

## Lineage

- hydra-v08-claims: parent.
