# spike-x07-v32-farfeed-reserve — x04 feeding with a hunter/farmer reserve

- **Lineage:** Spike. Parent: `spike-x04-v32-farfeed-early` (v32 + feed_range 40 + feed_base 70).
- **Change (roles.py):** dragons whose id hash falls in the lowest `feed_reserve_pct` = 35% never become feeders.
- **Why (SPIKE-22/23):** x04 converts well on walled maps (stronghold +41.7 on panel A) but its new losses combine
  collapse to <=2 units (59%), a stalled economy and uncontested enemy crowns (opp longest 39 vs 25). Late
  just-in-time feeding (x06) under-converted badly. Keeping x04's timing but reserving a third of the team for
  hunting/farming targets the collapse/hunter-removal channels without delaying conversion.
