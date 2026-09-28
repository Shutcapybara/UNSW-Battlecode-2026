# Bifröst v2 — narrow-path child escape

- **Base:** the submitted `bifrost-v01-portal-memory` bot.
- **Change:** after a split in a topology-constrained area, give the newborn a
  short `SEEK_NEW_AREA` objective. The parent retains its existing target and
  movement policy.
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

Separation pressure decays by `0.86` each round and ends after the child has
reached an open region at least five route steps away, or after twelve turns.
A nearby visible pearl or ready bed can temporarily keep the child on its
ordinary resource target. The child then resumes normal exploration. If it
grows and splits in another constrained path, it can pass the same handoff to
its own child.

## Evaluation

The behavior was motivated by the user's review of match `405581`, which
reported parents and newborns following the same narrow resource route. An
initial all-map screen used 120 games (both seats on 15 bundled maps) against
v01, v20, Loki v01, and Sinbad v26. v2 went 15–15 against v01, 13–17 against
v20, 13–17 against Loki, and 9–21 against Sinbad, with no runtime errors. The
round-zero local fallback was retested against the same panel on Dilemma and
the four issue maps (Devil, Portals, Queen of Spades, and Trauma). It scored
1–7 on Dilemma; on the four issue maps combined it scored 13–19, including
4–4 against v01. These results do not establish an overall strength gain over
v01. See v3 for a separate stable-waypoint candidate and its full panel.
