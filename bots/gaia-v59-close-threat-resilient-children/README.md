# Gaia V59 — close-threat resilient children

Gaia V59 is a snapshot in the new lineage, based on
`gaia-v44-small-map-density-dispersion`, which itself descends from
`fenrir-v20-crowded-resource-revalue`. The Fenrir planner, density model,
portal memory, crown policy, and newborn handoff remain intact.

## V59 change

V59 narrows V58's conditional child safeguard: a medium-map opening uses a
three-segment child only when a visible enemy head is within four toroidal
cells. Distant enemy sightings no longer suppress ordinary two-segment
reproduction, preserving round-100 growth while retaining the safer placement
when a head-to-head collision is plausible.

## V58 change

V58 keeps V47's ordinary opening reproduction, but switches to V57's checked
three-segment child only when a visible enemy head makes a medium compact map
contested. Quiet openings retain two-segment production and therefore do not
pay V57's round-100 population cost. The child still needs visible room and a
legal parent escape; Arena and Big Empty retain V47 behavior.

## Behaviour changes

- The first 100 rounds use deterministic ID-based exploration lanes. The lane
  bonus is advisory and yields to visible resources, threat avoidance, and the
  existing route planner.
- Blind portal dives are reserved for a deterministic portal-scout subset until
  round 100. Other dragons may use a portal after round 180, and repeated dives
  receive a cooldown penalty.
- A move that would eat a visible pearl is checked with the post-move body and
  a known flood/exit probe. A pearl with no viable escape is remembered as a
  death pearl and its value is removed from later searches.
- Splits evaluate child lengths 2 through 4 (within the legal parent bounds),
  using visible child room and parent room. The fixed two-segment rule remains
  available as the deterministic tie-break and for incomplete-body opening
  rescue.
- A safe cluster of renewable beds observed over time becomes a breeding area.
  Only a deterministic minority of dragons are breeders; nearby non-breeders
  receive a leave-area bias. Gaia status packets carry the area, role, and
  sender-alive bit through checked sonar.
- `main.py` validates the selected action again and chooses a legal one-step
  fallback if a stale route or unsafe pearl slips through. This prevents an
  empty/invalid command from turning pathfinding failure into a silent stall.

The layer is map-independent: it does not contain Queen of Spades coordinates
or opponent-specific rules.

## V02 change

The deterministic first-100 lane is mirrored for team B by the map's
180-degree symmetry. V02 also rejects marginal head-to-head actions during the
opening unless the dragon is at least two segments longer than the visible
enemy. This targets V01's replay pattern of strong early growth followed by
avoidable head trades.

## V04 change

V04 restores Fenrir V18's ally-density discount (`0.25`) instead of V20's
`0.10`. This is the only policy-valuation change; the V03 contact guard,
pearl safety check, adaptive split logic, breeding-area coordination, and
legal fallback are unchanged.

## V05 change

V05 retains the V04 opening and adds a smaller all-game contact penalty for
enemy heads and nearby allied heads, raises the flood-fill head block to one
turn, and slightly increases the local crowding charge. The goal is to retain
the round-100 population lead without paying for it with late head trades.

## V06 change

V06 bounds breeding-area detection to the 64 highest-evidence bed candidates
and rescans every eight rounds. V05 timed out on Big Empty because all 4,096
tiles were renewable beds and the detector clustered the full map every turn;
V06 removes that map-size-dependent quadratic work without changing movement
or split decisions on ordinary boards.

## V07 change

After round 100, routine splits on maps of at least 2,000 tiles stop once the
team reaches 48 dragons; emergency escape splits and designated breeders are
still allowed. A weak mirrored lane preference remains after the opening to
spread full teams across different corridors. This is intended to preserve
survival and exploration after the growth burst rather than continually
replacing small dragons.

## V08 change

The checked Gaia status packet already carried a sender-alive bit, but V07 did
not consume a stale-parent condition. V08 now makes a newborn leave its split
origin and explore outward when the recorded parent has not been heard for the
configured status TTL. The first two turns are protected from false death
inference, and breeders still keep their local production role.

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

The Fenrir V20 Queen-of-Spades baseline is recorded in
`build/gaia-baseline-qos` with replay review in
`build/gaia-baseline-qos-review`. Gaia versions are promoted only when a new
snapshot has zero runtime errors and improves the measured early-growth or
survival metrics without an unacceptable regression in the comparison panel.

## V47 change

V47 keeps V44's geometry-only pearl behavior on tiny arenas and Big Empty,
where V46's threat gate was respectively too restrictive during opening
contests and too costly to saturated resource throughput. On ordinary compact
maps between 400 and 1,999 cells, a visible pearl is rejected when every
post-collection exit is in the current bounded enemy threat map, and the pearl
is remembered as a likely death pearl. The same rule runs during ranking,
final action validation, and the legal fallback path.
