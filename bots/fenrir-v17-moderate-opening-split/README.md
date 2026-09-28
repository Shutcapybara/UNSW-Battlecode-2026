# Fenrir v17 — moderate density driven opening split

- **Base:** `fenrir-v13-frontier-depth`, ultimately based on submitted
  `bifrost-v01-portal-memory`.
- **Change:** test a smaller opening split incentive than v16. The bonus from
  nearby remembered pearls and soon due beds is capped at `4.0` (down from
  `8.0`), with an extra split bonus of `2.0` through round `60` (down from
  `4.0` through round `80`).
- **Scope:** map-independent. Both settings apply uniformly to every board and
  use the existing portal and frontier model; there are no map names,
  coordinates, or per-map rules.

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

The nine-map panel (both seat orders, against v13, v6, and the four references)
completed with zero runtime errors. Against the references v17 went 33–38–1:
Devil 2–6, Portals 6–2, Queen of Spades 3–4–1, Trauma 5–3, Dilemma 3–5,
Schooltime 5–3, Autarky 3–5, Colosseum 3–5, and Default 3–5. V13 scored
37–34–1 on those same maps and beat v17 10–8 head to head. The moderate opening
split bonus did not improve the all-map result. Results are in
`build/fenrir-v17-moderate-opening-split-panel`.
