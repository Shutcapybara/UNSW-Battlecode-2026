# Kenma 11 — current-view queen orbit

Parent: kenma-10-short-queen-orbit. Corrects its freshness comparison to World.seen == round + 1, the actual World::sense convention, and emits a short kenma_orbit activation log. All geometric, body-rollout, population and threat conditions are unchanged. Kenma 10's game trial was cancelled after this integration error was identified; its source and attempts are retained and it is not a strength result.

Original queens of length two or three can persist in a freshly observed, empty four-cell loop once three team units exist. Parent splits and sealed-pocket rescue retain priority. Eight projected separate turns validate entry and the cycle; every actual turn rechecks terrain, food, bodies and threats. No map identity inputs.

The original synthetic fixture repeated the timestamp mistake. The corrected fixture uses round + 1 and explicitly rejects round as stale. A real-engine activation check is required before the full comparison; passing the synthetic test alone is insufficient. Reserved seeds 11–13 and new maps remain untouched.

Status: corrected candidate, unmeasured. tools/kenma/test_orbit.cpp tests the corrected snapshot; the original fixture is preserved in test_orbit_v10.cpp for the draft audit.

Audit update: Four-game Weakhold/Australia seed-1 smoke finished 2–2, zero runtime errors, zero orbit activations. The observed-no-bed convention was still wrong (0 versus -1); this snapshot is frozen and rejected as an integration draft. Output main build/kenma/k11-orbit-smoke/activations.json. Test preserved as tools/kenma/test_orbit_v11.cpp.
