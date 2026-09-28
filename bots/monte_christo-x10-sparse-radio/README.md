# Monte Christo x10: sparse radio control

Parent: v06/x04. Remove density state and features, leaving exactly the slots
reserved by x04 silent. Other movement, production and legacy message content
remain. This isolates message suppression from density payload/interception
and processing costs; it is not part of finalist selection.

Configuration: `configs/monte_christo_messaging/screen.toml`.
Run: `experiment_data/monte_christo-x10-sparse-radio_20260925140653499123`.
External **12–12** (v01: 9–15), direct parent **4–4**. All 32 games have identical
movement and split streams for BOTH teams to x04's corresponding fixtures;
sonar differs intentionally. No caught errors or native timeouts. This is a
mechanism control, not a broadly validated replacement or additional independent
evidence for x04. See the messaging report (`../../docs/monte_christo-messaging.md`)
and `tools/monte_christo/messaging/sparse_equivalence.json`.

Judge cost probe: Hunter v20, Stronghold A, 15,428 metered turns, no timeouts or
caught errors. Both teams' movement/split streams match x04 exactly. Mean cost
27.674M versus x04's 28.574M points; x04 adds 0.900M, or 3.25%, over x10's mean.
Peak cost is 58.542M, so the mean saving does not imply a lower peak.
Run: `experiment_data/monte_christo-x10-sparse-radio_20260925144828226450`;
configuration `configs/monte_christo_messaging/cost-probe.toml`.
