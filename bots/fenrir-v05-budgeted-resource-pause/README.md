# Fenrir v5 — budgeted nearby-resource pauses

- **Base:** `fenrir-v04-escape-anti-loop`, ultimately based on submitted
  `bifrost-v01-portal-memory`.
- **Change:** retain v4's stronger child separation and allow up to three total
  turns of nearby fresh-pearl detours during one escape. This lets a child
  collect a close pearl without letting a dense local pocket repeatedly reset
  its route back through the parent.
- **Scope:** map-independent. Corridor detection and escape targets use sensed
  edge topology, reachable room, and the learned portal graph; there are no
  map names, coordinates, or per-map rules.

## Split handoff and child behavior

The parent probes the child's old-tail spawn out to depth three. It sends a
checked sonar packet only when that area has at most two exits and a small
reachable region or very few branch points. The packet carries the parent's
ID, the child's spawn cell, the split round, and the escape / crown-inheritance
flags. It is repeated for up to two turns because newborns may have no sonar on
their first input. A receiving process accepts it only when it is newly born
and still near the encoded spawn cell.

When no packet arrives, the newborn checks its own first-turn topology and
starts the same short escape objective if it is constrained. This includes
round-zero children, using the same initial-ID boundary already used by the
opening policy to distinguish starters from newly split units. Crown-inheriting
children skip the local escape fallback.

The child runs a bounded breadth-first search over known open edges, paired
portals, and optimistic unknown edges. It prefers a nearby target at least five
route steps from the split origin with more local reachable cells and branches.
Known portal links participate in the same search; an unpaired portal remains
an uncertain exit and receives a small escape bonus under the inherited blind
risk calculation.

Separation pressure decays by `0.91` each round and ends after the child has
reached an open region at least five route steps away, or after eighteen turns.
The child may pause for a fresh visible pearl within two steps, up to three
turns total during that escape. Remembered pearls and beds cannot keep it
circling locally. After the budget is used, the child continues toward its
stable waypoint. If it grows and splits in another constrained path, it can
pass the same handoff to its own child.

## Evaluation

The behavior was motivated by the user's review of match `405581`, which
reported parents and newborns following the same narrow resource route. An
initial all-map screen used 120 games (both seats on 15 bundled maps) against
v01, v20, Loki v01, and Sinbad v26. That v2 screen went 15–15 against v01,
13–17 against v20, 13–17 against Loki, and 9–21 against Sinbad, with no runtime
errors. A later Dilemma retest after the round-zero fallback remained 1–7 across
the same panel. v3 then completed the same 120-game all-map panel with zero
runtime errors: 15–15 against v01, 13–17 against v20, 16–14 against Loki, and
10–20 against Sinbad. That is four more wins than v2 overall and four more wins
on the four issue maps combined (15–17 vs 13–19), while Dilemma remains 1–7.
This is a measured improvement over v2, but v3 still does not beat the stronger
reference bots overall. v4 went 16–16 on the four issue maps; v5 went 18–14
against the four reference bots on the same maps, with zero runtime errors.
The 40-game panel, which also includes v4, is recorded in
`build/bifrost-v5-budgeted-resource-pause-key-maps`.
