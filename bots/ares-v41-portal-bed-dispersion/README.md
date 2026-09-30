# Ares V41 — portal-bed dispersion

V41 branches directly from V40 and keeps its length-priced sprint policy. It
changes target selection when a pearl or bed has a visible allied dragon within
two tiles. One nearby ally reduces that resource's value to 12%; additional
allies compound the discount. The existing nearest-ally yield still applies to
other targets.

This addresses portal exits where the route through a portal is short enough
that a dragon may continue toward a bed already covered by an ally. With the
resource value reduced, an uncovered pearl, unexplored area, or eligible hunt
can win target selection instead. The penalty uses visible allied heads only;
it does not infer unseen teammate locations.

V41 also tracks the landing cell and pair of the most recent portal crossing.
For 12 rounds, while within two tiles of that landing, it lowers targets whose
route uses the same pair and penalizes a move that crosses back. This gives a
split dragon time to disperse toward uncovered ground, exploration, or a valid
hunt.

The decoded Queen of Spades replay 700279 showed repeated P0 returns: dragon 18
crossed to the crowded `(20,31)` bed cluster at round 51 and crossed back at
round 56; child 82 crossed into `(21,31)` at round 169 while three allied heads
were clustered around the landing, then crossed back at round 180. The focused
regression covers both allied bed coverage and recent same-pair return
avoidance. V41 is still experimental. In a ten-map, both-seat screen, V41 beat
V40 11–9 with zero runner errors. It swept Dilemma, Portals, and Slithery
Fight. `unswbc` generated each game's seed, recorded in its log. See the
[V41 finding](../../docs/findings/2026-09-30-ares-v41-portal-bed-dispersion.md).
The contest accepted the upload as active submission v94 (ID 13086) on
2026-09-30 11:49 UTC. The server activation does not change V41's local
experimental status.
