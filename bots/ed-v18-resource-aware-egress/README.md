# Ed v18: resource-aware split egress

- **Lineage:** Ed, created for the temporal-policy campaign.
- **Parent:** `ed-v17-split-egress-message`, itself descended from
  `ed-v02-split-intent` and the frozen `ed-v00-serre-control`.
- **Change:** retain v02's parent-target hint when at least two current pearls
  are visible in the confirmed-open local region around a split-born child's
  launch point. Allow v17's short known-open route only when that local pocket
  is below this resource threshold.
- **State inputs:** confirmed-open, currently unoccupied region cells and
  pearls visible in the current round. No map-name dispatch or temporal move
  average is used.
- **Feature switch:** `fork_egress_skip_resource_rich=0` restores v17 route
  selection; `fork_egress=0` disables egress messaging.
- **Active parameters:** `fork_intent=1`, `fork_egress=1`,
  `fork_egress_skip_resource_rich=1`, `fork_egress_min_pearls=2`; inherited
  route depth 6, local depth 3, room threshold 14, room gain 4, and evaluator
  margin 2.8.
