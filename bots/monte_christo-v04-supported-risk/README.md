# monte_christo-v04-supported-risk

Lineage: **monte_christo**. Parent: `monte_christo-v02-table-risk`.

The fitted table has only 8, 13 and 0 training examples in three of its nine
trade classes; it was also trained mainly on short foragers. This version uses
the original prior when bucket support is below 30, own length exceeds 8, or
round >= 380. Other states retain v02's fixed 50/50 table/prior blend. This is a
predeclared generalization guard, not an additional fit on gameplay holdouts.

All other strategy files are byte-identical to v02. Same training provenance
and prediction limitations; see `tools/monte_christo/models/training.json` and
`docs/monte_christo.md`. The guard is tested as a separate version so any lost
benefit or improvement remains visible.

## Completed evaluation

Original native screen: **22–10**; external 17–7, direct v01 5–3. Reserved run: **38–16**, including direct v01 4–2. Against the same 48 frozen external fixtures it scored **34–14 versus v01 38–10**; six Drake baselines were rerun after a source change. Four judge fixtures: 29,148 turns, max 67.32M points, 22,085,632 bytes, no timeouts. **Not promoted**; preserve its distinct Big Empty strength.

No game, analysis, reported runtime or caught policy errors in these runs.
Exact run paths, map/side breakdowns, counterexamples and training provenance:
[Monte Christo handoff](../../docs/monte_christo.md).
