# Carthage 11 — portal memory (H-S1)

This immutable experiment forks `carthage-05-free-sprint`. It implements the
queued H-S1 rule: report known portal transits over tagged sonar; treat a
transit as a possible team death when its dragon sends no timestamped team
report through the three-round risk window; then avoid that pair for 30 rounds.
Known trauma reports are relayed, and any later report from the same dragon
proves it survived the event window. The rule only applies to portal pairs the
dragon has identified.

Sonar cannot prove a death from silence alone. This is a best-effort
missed-heartbeat approximation: directional rays can be intercepted or fail to
reach a teammate. This first draft also counted prey-sighting packets as source
heartbeats. Its partial run was stopped and is preserved as unscored; corrected
decoding is in `carthage-12-portal-memory`.

Parent policy and all existing behavior remain in `carthage-05-free-sprint`.
This directory is experimental and has no submission manifest.
