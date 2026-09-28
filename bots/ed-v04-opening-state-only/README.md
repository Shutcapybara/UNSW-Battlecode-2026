# Ed v04: opening investment state only

- **Lineage:** Ed, created for the 2026 temporal-policy campaign.
- **Parent:** `ed-v00-serre-control` (frozen Serre v01 source).
- **Temporal interface:** `temporal.phase_state()` uses the 500-round global
  horizon and reports opening (`r < 80`), middle (`80 <= r < 360`) or endgame
  (`r >= 360`), plus progress, remaining time and a reason string. It does not
  use per-dragon age.
- **Intervention:** add 2.0 to the existing split value when a safe split is
  available and the configured gate is satisfied. Existing split, child-room,
  parent-room, unit-cap and emergency rules remain in force.
- **Arm:** `state only`.
- **Off switch:** `opening_mode=0` returns the inherited split score exactly.
