# Fenrir v18 — arrival ready bed targets

- **Base:** `fenrir-v13-frontier-depth`, ultimately based on submitted
  `bifrost-v01-portal-memory`.
- **Change:** set the bed wait horizon to zero. A bed target receives value only
  when its pearl is expected to exist by the dragon's arrival, rather than
  drawing a dragon toward a pearl that will appear later. This isolates
  resource timing from v13's frontier and portal changes.
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

The nine-map focused panel completed with zero runtime errors. Against the four
references v18 went 46–26 and beat v13 11–7 on the same maps. This warranted an
all-map run of 180 matches (both seats on all 15 bundled maps against v6, v13,
and the four references), again with zero runtime errors.

Across all maps v18 scored 77–43 against the four references: 21–9 against v1,
20–10 against v20, 20–10 against Loki, and 16–14 against Sinbad. V13's earlier
120-game reference panel scored 58–61–1, so v18 improved that aggregate by 19
wins. It also beat v6 and v13 20–10 each in direct all-map matchups. Per-map
results against the four references were Colosseum 8–0, Arena 5–3, Autarky 4–4,
Big Empty 6–2, Default 6–2, Default Small 5–3, Devil 5–3, Dilemma 1–7, Portals
7–1, Queen of Spades 4–4, Schooltime 7–1, Slithery Fight 5–3, Stronghold 7–1,
Trauma 4–4, and Trophy 3–5. Dilemma and Trophy remain the weakest maps. Full
results are in `build/fenrir-v18-arrival-ready-beds-full`; the focused panel is
in `build/fenrir-v18-arrival-ready-beds-panel`.
