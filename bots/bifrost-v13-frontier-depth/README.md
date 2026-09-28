# Bifröst v13 — deeper frontier search

- **Base:** `bifrost-v06-longer-resource-window`, ultimately based on submitted
  `bifrost-v01-portal-memory`.
- **Change:** search one extra route layer before the target search can stop, and
  reduce the estimated risk for an unexplored portal exit from `0.5` to `0.15`.
  The extra layer lets deeper value beyond a portal compete with nearby targets;
  the risk change affects only unpaired portals with no recent exit information.
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

The all-map panel ran 150 games (both seats on all 15 bundled maps) against v6
and the four reference bots, with zero runtime errors. Against the references
v13 scored 58–61–1 (win–loss–draw): 16–14 against v1, 13–17 against v20,
17–12–1 against Loki, and 12–18 against Sinbad. The previous v6 reference panel
scored 54–66, so v13 is a modest aggregate improvement, although v13 lost its
direct 30-game head-to-head with v6, 13–17.

On the issue maps v13 scored 18–13–1 against the references: Devil 4–4, Portals
6–2, Queen of Spades 3–4–1, and Trauma 5–3. Compared with v6, it gained two
wins on Portals and three on Schooltime, with a two-win gain on Autarky and
Stronghold. It lost two wins each on Colosseum and Default, and the known
Dilemma weakness remained 1–7. This is the strongest tested Bifröst version so
far on the combined reference-bot all-map panel, but still trails the reference
bots in aggregate. Full results are in
`build/bifrost-v13-frontier-depth-full`; the focused panel is in
`build/bifrost-v13-frontier-depth-key-maps`.
