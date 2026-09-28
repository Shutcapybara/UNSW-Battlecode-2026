# monte_christo-v01-core

Lineage: **monte_christo**. Architectural base: `examples/bahamut-scaffold`
(protocol.py and bot.toml copied unchanged). Borrowed component parent:
`sinbad-v03-hunt` (world, tactics, target/evaluation policy, roles, sonar).

This first frozen baseline retains Sinbad's farming, production, crown, feeding,
prey hunting and portal sharing. Changes: explicit candidate generation versus
selection; remove disk-based tracing; report unexpected fallbacks via MC_ERROR;
new team-specific packet tags; suppress three-step searches at length >= 12 to
bound long-body search cost. The two-step escape/strike search remains available.

Layers: main.py orchestrates Bahamut hooks; world.py owns retained observations
and partial-map caches; tactics.py computes simulation/reach/space features;
policy.py ranks intentions; main.py selects and executes; roles.py maintains
crown/feeder state; radio.py schedules communication and comms.py encodes it.
params.py documents all tunable units and ages. No runtime ML dependency.

Training instrumentation is opt-in (`training_trace=1`) and logs only observable
features of selected surviving moves. Release default is zero. The future label
is whether a particular reaching enemy kills this head before its next turn.

Evaluation results and reproducible commands: see `docs/monte_christo.md`.

## Completed evaluation

Native full gauntlet: **106–48** (7 references × 11 maps × both sides). Side A 58–19; B 48–29. Additional Kraken reserved-map baseline 6–0. Fresh reflected references 6–12. Four judge fixtures: 29,200 turns, max 67.31M points, 22,020,096 bytes, no timeouts. **Recommended stable baseline.**

No game, analysis, reported runtime or caught policy errors in these runs.
Exact run paths, map/side breakdowns, counterexamples and training provenance:
Monte Christo handoff (`../../docs/monte_christo.md`).
