# Ed v22: r300 pressure-conditioned feeding

- **Lineage:** Ed, descended from v21/v20/v19 and mechanism parent v02.
- **Change:** require fresh observed rival pressure and global round at least
  300 before entering the existing feeder role.
- **Reason:** v19's selected feeds occurred on three map/side fixtures at or
  after r300, while v21's r350 gate retained selected feeds on only one fixture.
  This removes the r250-only conversion without waiting for the inherited
  map-scaled clock.
- **Reversibility:** reassess every turn; no fixed donor lock.
- **Other safeguards:** fresh crown, minimum crown length, donor shorter than
  crown, and existing feed range.
- **Feature switches:** disable feed_pressure_gate and set
  feed_pressure_start_round=0 to restore the inherited v02 feed condition.
