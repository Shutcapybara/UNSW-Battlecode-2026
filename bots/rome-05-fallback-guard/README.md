# Rome 05 — H-H5 fresh-queen-evidence fallback guard

Parent: `rome-03-queen-state-convert`; one switch: apply its late low-own-unit queen-conversion override only when the current crown record is for one of the two original queens (IDs 0/1) and its sonar timestamp is within the existing `crown_ttl`. All three uses (crown election, split inheritance, and feeder reach) share the same predicate. With absent, non-queen, or expired queen evidence, preserve Rome01/03 normal crown election and inheritance fallback. A fresh beacon is evidence, not proof that the queen remains alive; possible stale-beacon windows remain.

Preregistered expectations: (1) on the preselected Rome03-triggered Portals fixture subset, recover some terminal-longest/crown-consolidation performance versus Rome03; (2) overall paired win share is nonnegative versus Rome03, while reporting per-map and 90% cluster intervals; (3) opening economy and material at r50/r100 remain unchanged; (4) compare the complete arm with clean `rome-01-nodevil` as a guard. Full panels: seeds 1–3, both seats. No replay-omniscient state is used.

One-change caveat: this is evidence-gated fallback, not exact liveness detection; the protocol has no reliable queen-death signal. See Himeji H-H5 in `docs/findings/2026-10-04-himeji-dead-queen-conversion-reading.md` and Rome's final finding when available.


## D-043 closeout

This old-map arm was interrupted under D-043. It is an incomplete pre-swap diagnostic: pool simulations 480/480, no two-parent score; official gen 227/1,392 and stopped, no score or gate. It is not eligible for stacking or comparison to the post-M2 baseline. See `docs/findings/2026-10-04-rome-H-H5-pre-swap-partial.md`.
