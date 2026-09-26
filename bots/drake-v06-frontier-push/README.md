# drake-v06-frontier-push

**Lineage**: Drake. **Parent**: `bots/drake-v04-beacon/`.
No new borrowings (v04's credits apply).

## Hypothesis (user-suggested)

Dragon count should be a decision feature: at/near the unit cap the
interior is saturated with gatherers, while unclaimed map holds fast beds
nobody harvests.  Small dragons near the exploration frontier should push
outward in groups (cohesion + supported strikes), dying expendably there;
each frontier death drops the unit count so interior gatherers split
replacements and the economy stays used.

## Implementation

- **Feature**: `work["pressure"] = UNITS / team_target()` computed in
  `update_state`; frontier detection by `nearest_unknown()` — a BFS
  through known-open cells to the nearest cell with unknown sides
  (`unk[] > 0`).
- **Push mode** fires when `pressure >= 0.90`, `LEN <= 5`, not CROWN, no
  pearl within 3 tiles, frontier within 12 BFS cells (measured: ~40% of
  turns on big_empty at pressure ~0.91).
- Pushers: target = the frontier cell; **cohesion** with nearby allied
  pushers replaces the spread term (`(6 - dist) * push_cohesion`); threat
  risk tolerance ×0.75; **no voluntary splits** while pushing
  (replacements come from interior gatherers, as the hypothesis intends).
- Safety is never bypassed: fatal-move simulation, flood/doom/tunnel
  vetoes unchanged.

## Measured results

big_empty vs ouroboros-v10 (the fixture the hypothesis targeted): the
mechanism fires as designed but the economy does not move — pearls
1559 v 2051 at r499, essentially identical to v04's ~1536 v 2050.  On
big_empty both teams saturate the map at ~60 units, so "unclaimed
territory" is not where the pearls are lost; the gap is mid-game tempo
(see v07's diagnosis).

Full frozen-roster screen: **failed at 157/242 games** with a shared
`game_stats/runs/` ledger race (another lineage's concurrent process;
results saved in
`experiment_data/drake-v06-frontier-push_20260925124615277071`).  On the
completed common subset v06 is level with v04 (69-1-88 partial vs v04's
0.463 on the same opponents) — a null aggregate result.

**Superseded by v07** (same code plus the mission fix); kept for the
mechanism and its instrumentation.

## Sandbox / judge checks

`nearest_unknown` is a ≤160-cell BFS on a subset of turns; bounded by
v04/v07 family measurements.
