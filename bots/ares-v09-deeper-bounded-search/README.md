# Ares V09 — deeper bounded search

Ares V09 is a separate snapshot of Ares V06. It preserves V06's C++ runtime,
policy, and size-matched supported-threat evaluation while applying the deeper
bounded-search parameters used by Robert V01:

- First target-search pass depth: 16 → 20.
- Target-search cap: 160 → 256 normally, 64 → 96 when saturated, and 60 → 80
  for the first two turns.
- Target-frontier cutoff: depth 4 → 6.
- Room-flood caps: 24/40 → 32/48.

The existing late-round and sparse-board caps remain unchanged. No other
runtime or policy source was changed from Ares V06. V09 has not been
benchmarked; its parent-relative score and CPU/TLE behavior are unmeasured.
