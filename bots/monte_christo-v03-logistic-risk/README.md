# monte_christo-v03-logistic-risk

Lineage: **monte_christo**. Parent: `monte_christo-v01-core` (parallel alternative to v02).
Borrowed components and architecture are documented in v01.

Hypothesis: the hand-set threat probabilities overprice many two/three-step
trades. Replace them with a 50/50 blend of the original prior and a fitted
13-coefficient regularized logistic model.
All collision, topology, production and crown rules are otherwise unchanged.

Training: 24 native fixtures against Tew v12, Hunter v20 and Ouroboros v13.
Fit on arena/default; select regularization on default_small; audit predictions
on stronghold. Features are generated from the bot's observations, and only
future death labels come from replay truth. The target is enemy-initiated head
collision before our next action, conditional on a selected surviving move.
Do not interpret this observational hazard as a causal attack probability for
untaken moves. The 50% prior blend is fixed before gameplay testing.

Data, selected parameters, source/replay hashes and predictive metrics:
`tools/monte_christo/models/`. Release inference is standard-library Python.
Results and counterexamples: `docs/monte_christo.md`.

## Completed evaluation

Original native screen: **20–12**; common external references 16–8, direct v01 4–4. Four judge fixtures: 29,191 turns, max 67.31M points, 22,085,632 bytes, no timeouts. Retained as the logistic alternative; not promoted.

No game, analysis, reported runtime or caught policy errors in these runs.
Exact run paths, map/side breakdowns, counterexamples and training provenance:
Monte Christo handoff (`../../docs/monte_christo.md`).
