# monte_christo-v05-compact-risk

Lineage: **monte_christo**. Parent: `monte_christo-v04-supported-risk`.

v04 won its screen but the reserved test exposed a Schooltime regression against
Sinbad (0–2 versus v01's 2–0). Most fitted hazard observations came from compact
maps. Apply v04's supported table only on maps <= 625 cells, the compact/open
boundary already used by the feature contract and other pool doctrines. On open
maps return the exact v01 prior before blending/clipping. All other code is
unchanged from v04; the model and thresholds are not refit.

This is an adaptation to v04's held-out results, so those results are development
evidence for v05. Fresh reflected fixtures (arena_FY, Colosseum_TFX, trophy_FY)
provide the subsequent robustness check. They remain the same topology families,
not three independent new map designs. Test both direct-parent and common-pool
performance. See `docs/monte_christo.md` for exact results and limitations.

## Completed evaluation

Fresh reflected-layout run: **9–15**, comprising 6–12 against external references (v01 also 6–12, all outcomes matched) and 3–3 directly against v01. Schooltime/Sinbad regression verification: **2–0**, identical baseline outcome/material metrics. Two judge fixtures: 14,584 turns, max 66.00M points, 22,020,096 bytes, no timeouts. Latest conservative learned candidate; **not a proven general improvement over v01**.

No game, analysis, reported runtime or caught policy errors in these runs.
Exact run paths, map/side breakdowns, counterexamples and training provenance:
[Monte Christo handoff](../../docs/monte_christo.md).
