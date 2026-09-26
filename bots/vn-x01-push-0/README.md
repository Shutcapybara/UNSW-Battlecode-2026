# Von Neumann x01: frozen baseline (Porthos x04 / policy P1)

Every `.py` file and `bot.toml` is a byte-identical copy of
`bots/porthos-x04-policy` (verified by SHA-256 in `tools/von_neumann/frozen.json`,
2026-09-26). Von Neumann is the combat/aggression lineage: non-combat
machinery (state, radio, candidates, executors, economy/production/crown
parameters) is frozen at this baseline; iteration happens on the combat
procedures of the decision policy (strike admission, threat calibration,
aggression gating, hunting) with the policy refit as evidence accumulates.

Provenance of the baseline (see `docs/porthos-lineage.md`):

- Ancestry `monte_christo-v01-core` → stream-verified parity decomposition
  (porthos-x02, 182/182 identical move/split/sonar streams) → swarm state/radio
  (x03) → policy P1 (x04).
- Measured at birth: 182-game gauntlet **126–56** (+13 over the MC-parity
  control x03), 24-game screen 19–5, reserve 22–14, judge-clean
  (max 71.1M CPU / 22.1 MB per turn).
- Posterior skill in the 60k-game replay model: the strongest measured bot of
  the French line available at freeze time.

Role in this lineage: the control every combat variant is compared against on
identical fixtures (deterministic engine, exact pairing). Do not edit; edit a
copy with a new version number.
