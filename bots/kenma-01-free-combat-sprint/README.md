# Kenma 01 — free combat sprint

Parent: carthage-05-free-sprint at ea8ada4e2.

When an enemy head is within four cells, consider three-step movement paths whenever the current length makes all three steps free. The parent suppresses these paths above its size cap, including for long dragons. The existing simulator, threat scoring and route scores select the action. Everything else is preserved.

Status: rejected as an improvement. Head-to-head against carthage-05-free-sprint: 48 wins, 54 losses, 0 errors on all 17 LIVE_MAPS_M2 maps x both seats x seeds 1–3. Full results: main checkout build/kenma/k01-v-carthage-s123/score.json; exact schedule and fingerprints: manifest.json alongside it. Australia went 0–6. No deployment recommendation; no sandbox budget spent on this failed screen.
