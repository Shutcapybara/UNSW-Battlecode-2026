# Ed v19-pressure-feed-state

- **Lineage:** Ed.
- **Parent:** ed-v02-split-intent (frozen foundation ed-v00-serre-control).
- **Change:** require a fresh reported rival length within two segments of
  the current crown before assigning the existing feeder role.
- **Pressure signal:** the locally retained best rival report is no older than
  prey_ttl and is at least crown_length - 2. Missing or stale reports preserve
  foraging. This is observed pressure, not an omniscient team score.
- **Reversibility:** role eligibility is recomputed each turn; there is no
  fixed donor cohort lock. Crown election, crown freshness, donor length and
  range safeguards remain active.
- **Clock:** state-only pressure entry; retains crown election clock.
- **Feature switches:** feed_pressure_gate=0 restores the inherited v02 feed
  gate; feed_pressure_state_only=1 removes only the feed-start clock.
