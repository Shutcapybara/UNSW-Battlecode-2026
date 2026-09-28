# Ed v23: visible-recipient pressure feeding

- **Lineage:** Ed; descended from v22 and mechanism parent v02.
- **Change:** keep v22's r300 fresh-pressure gate, but enter the feeder role
  only when the crown's head is directly visible within feed_dist.
- **Reason:** prior traces showed many feeder-role turns but few selected feed
  actions, and native screens increased total length without growing the
  longest dragon. Distant donors should continue foraging until the recipient
  is directly actionable.
- **Reversibility:** recompute each turn; no fixed donor lock.
- **Feature switch:** feed_require_visible=0 restores the prior feed_range
  eligibility. Disable feed_pressure_gate and set feed_pressure_start_round=0
  to restore v02's inherited feed condition.
