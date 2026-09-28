# Bifröst v20 — crowded resource revaluation

- **Base:** `bifrost-v18-arrival-ready-beds`, ultimately based on submitted
  `bifrost-v01-portal-memory`.
- **Change:** reduce the ally density discount used when valuing pearls and beds
  from `0.25` to `0.10`. This keeps some route separation while making a busy
  resource area less likely to be discounted enough that the team gives an
  opponent the early pearl lead.
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

The nine-map panel (both seats, against v18, v13, v6, and the four references)
completed with zero runtime errors. Against the references v20 went 41–31,
below v18's 46–26 on the same maps, and split with v18 9–9. It improved against
v1 from 11–7 to 12–6 but fell against Loki from 13–5 to 10–8 and Sinbad from
12–6 to 9–9. Dilemma remained 1–7 and Portals slipped from 7–1 to 5–3. The
reduced ally density discount is not an aggregate improvement. Results are in
`build/bifrost-v20-crowded-resource-revalue-panel`.
