# Monte Christo x11: crown-priority density messages

Parent: monte_christo-v06-density. Keep its density features and four-round
half-life, but never replace an outgoing CROWN report when reserving density
rays. Before crown reporting begins, this is exactly v06's scheduler.

Hypothesis generated from the broader development cohort: displaced crown
traffic may explain late-game regressions despite viable midgame populations.
These validation maps now count as development evidence for x11. The reserve
maps remain unused by candidate selection.

Development: **36–24** against six external references, versus v01's **45–15**;
direct parent **2–8**. Six paired gains and 15 losses. Configuration:
`configs/monte_christo_messaging/validation.toml`; run:
`experiment_data/monte_christo-x11-crown-priority_20260925141424445042`.
No caught errors or native timeouts in the 70-game audit; no judge games run.

All 70 complete fixtures have identical movement/split/sonar streams to v06
before round 250. Preserving crowns alone did not fix the later regression.
Retain as a rejected hypothesis and reusable scheduler control. See the
messaging report (`../../docs/monte_christo-messaging.md`).
