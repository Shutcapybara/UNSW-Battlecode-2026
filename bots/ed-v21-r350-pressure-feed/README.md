# Ed v21: r350 pressure-conditioned feeding

- **Lineage:** Ed, descended from v20/v19 and mechanism parent v02.
- **Change:** require a fresh observed rival length within two segments of the
  crown, and global round at least 350, before entering the existing feeder
  role.
- **Reason:** v19's state-only arm opened too early and lost; v20's inherited
  map-scaled clock saw pressure but produced no selected feed action in trace.
  Round 350 is the intermediate entry indicated by the v19 activation window.
- **Reversibility:** reassess every turn; no fixed donor lock.
- **Other safeguards:** fresh crown, minimum crown length, donor shorter than
  crown, and existing feed range.
- **Feature switches:** feed_pressure_gate=0 plus feed_pressure_start_round=0
  restores v02's inherited feed condition.
