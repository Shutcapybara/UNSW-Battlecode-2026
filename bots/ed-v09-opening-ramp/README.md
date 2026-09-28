# Ed v09: continuous opening investment

- **Lineage:** Ed, created for the 2026 temporal-policy campaign.
- **Parent:** `ed-v00-serre-control` (frozen Serre v01 source).
- **Temporal interface:** shared 500-round `temporal.phase_state()`; only
  global round is used for the schedule.
- **Intervention:** when fewer than nine units remain, add a clipped linear
  split-value bonus `2.0 * opening_weight`, where
  `opening_weight = clip((80-r)/80, 0, 1)` is returned by the phase interface. The bonus is full at round 0,
  halves at round 40 and reaches zero at round 80. Existing safe-split checks
  remain unchanged.
- **Comparison:** continuous time-plus-state ramp against the hard-boundary
  time-plus-state arm (`ed-v05`) and the state-only arm (`ed-v04`).
- **Off switch:** `opening_mode=0` returns the inherited split score.
