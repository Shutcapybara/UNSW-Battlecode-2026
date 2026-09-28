# Bifröst v16 — density driven opening split

- **Base:** `bifrost-v13-frontier-depth`, ultimately based on submitted
  `bifrost-v01-portal-memory`.
- **Change:** add an early production bonus that grows with the number of
  distinct nearby remembered pearls and soon due beds, and apply a smaller
  baseline split bonus through round 80. The score is capped and only applies
  to dragons of length six or less, so it rewards expansion where sensed local
  resources can support it.
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

The nine-map panel (both seat orders, against v6, v13, and the four references)
completed with zero runtime errors. Against the references v16 went 34–37–1:
Devil 5–3, Portals 5–3, Queen of Spades 3–4–1, Trauma 5–3, Dilemma 0–8,
Schooltime 4–4, Autarky 6–2, Colosseum 3–5, and Default 3–5. V13 scored
37–34–1 against the references on the same maps and beat v16 head to head
11–7. The resource density driven split bonus helps on Autarky but does not
improve the aggregate. Results are in
`build/bifrost-v16-density-driven-opening-split-panel`.
