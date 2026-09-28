# spike-x05-v32-needfeed — need-gated long-range feeding

- **Lineage:** Spike. Parent: `spike-x04-v32-farfeed-early` (v32 + feed_range 40 + feed_base 70).
- **Change:** a dragon only becomes a feeder while the crown's length is below the longest enemy the dragon
  knows of (own sight or the existing prey gossip, remembered for `need_memory`=100 rounds) plus `need_margin`=4.
  With no enemy length known it feeds as x04 does. Setting need_margin very large restores x04.
- **Why (SPIKE-19):** x04 nearly eliminated v32's conversion losses (25 -> 4 round-500 losses while holding more
  total length; length efficiency 0.57 -> 0.66) but replaced them with over-conversion losses: teams collapsed to
  one dragon (units 1, longest = total) on Orchard/commons maps, and on big_empty feeding stalled the economy while
  the opponent's total ran to 475-778. Net +0.9 pp (unresolved). Feeding should be conditional on need — a small
  evaluation of "is the tiebreak already safe?" instead of a clock.
