# Carthage 12 — portal memory (H-S1)

This immutable experiment forks `carthage-05-free-sprint`. It implements the
queued H-S1 rule: report known portal transits over tagged sonar; treat a
transit as a possible team death when its dragon sends no timestamped team
report through the three-round risk window; then avoid that pair for 30 rounds.
Known trauma reports are relayed, and a later crown or density report from the
same dragon proves it survived the event window. Prey sightings are excluded
because their ID refers to the enemy prey, not the reporting dragon. The rule
only applies to portal pairs the dragon has identified.

Sonar cannot prove a death from silence alone. This is a best-effort
missed-heartbeat approximation: directional rays can be intercepted or fail to
reach a teammate. The paired replay analysis therefore measures actual transit
deaths, while any promotion decision also needs to account for this signal
limitation.

Parent policy and all existing behavior remain in `carthage-05-free-sprint`.
This directory is experimental and has no submission manifest.

## Result

Rejected on the declared seeds 1–3 pool/gen panels. Per-transit death within
three rounds fell only 2.7% on pool and 1.3% on gen, while normalized economy
lower bounds fell to −0.065 and −0.038. Transit volume dropped about 25–26%.
See [the H-S1 finding](../../docs/findings/2026-10-04-carthage-12-hs1-portal-memory.md)
for the paired intervals, map-level rates, and artifacts.
