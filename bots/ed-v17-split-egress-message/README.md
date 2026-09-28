# Ed v17: split egress message

- **Lineage:** Ed, created for the temporal-policy campaign.
- **Parent:** `ed-v02-split-intent`, an otherwise unchanged descendant of the
  frozen `ed-v00-serre-control` source.
- **Change:** for a normal forager split, the parent may send the child a short
  sequence of directions through the split body. It does so only when the
  child starts in a small known-open pocket and the route reaches a larger
  known-open region. The child follows a step only when exact move simulation
  says it survives and the normal evaluator scores it within 2.8 points of its
  best action. Unknown edges are excluded from the transmitted route; a
  rejected or blocked instruction is dropped. If no egress route qualifies,
  Ed v02's parent-target hint is sent instead.
- **Feature switch:** `fork_egress=0` disables the new route message.
- **Active parameters:** `fork_intent=1`, `fork_egress=1`, route depth 6,
  local depth 3, local/goal room threshold 14, minimum room gain 4, and
  decision margin 2.8.
