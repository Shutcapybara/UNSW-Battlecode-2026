# Gavroche V53 round-40 search cap 48

Parent: V52. Preserve unrestricted target search through the first 39 rounds,
then apply a 48-node cap. After round 150, restore 64 nodes and length-4/5
three-step paths only when the team has at most 20 units.

Hypothesis: recover some strategic search depth while retaining CPU headroom
against the round-49 spike observed in V50.
