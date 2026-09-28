# Fenrir v15 — lower unseen portal risk

- **Base:** `fenrir-v06-longer-resource-window`, ultimately based on submitted
  `bifrost-v01-portal-memory`.
- **Change:** only reduce the estimated risk of an unexplored, unpaired portal
  exit from `0.5` to `0.15`. Target-search depth remains at the v6 value of
  three steps, isolating the portal-risk change from v13's deeper search.
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
The child may pause for a fresh visible pearl within two steps, up to six
  turns total during that escape. Remembered pearls and beds cannot keep it
circling locally. After the budget is used, the child continues toward its
stable waypoint. If it grows and splits in another constrained path, it can
pass the same handoff to its own child.

## Evaluation

The nine-map panel (both seat orders, against v6, v13, v14, and the four
references) completed with zero runtime errors. Against the references v15 went
32–40: Devil 4–4, Portals 4–4, Queen of Spades 5–3, Trauma 3–5, Dilemma 0–8,
Schooltime 4–4, Autarky 5–3, Colosseum 4–4, and Default 3–5. V13 and v15 split
9–9 head to head on this panel, but v15's reference score is weaker than both v13
and v14. Lowering the unexplored-exit risk alone causes a severe Dilemma loss.
Results are in `build/fenrir-v15-lower-portal-risk-panel`.
