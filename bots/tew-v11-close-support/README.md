# tew-v11-close-support

Lineage: Tew. Parent: `tew-v10-supported-hunts`; strategy base `ouroboros-v13-ladder`.

Hypothesis: v10's support gate counts every head in the full 7×7 view. Heads within two movement steps are more credible combat support; a smaller radius may prevent distant allies from authorizing a risky trade.

Change: `ladder_support_radius=2` replaces v10's radius 6 for both visible ally and enemy head counts. The other Tew v10 layers and settings are unchanged.

Comparison: native, both sides on `default_small`, `arena`, `devil`, and `schooltime`, against v07, v10, ouroboros-v10 and hunter-v20. See measured results below. No sandbox check.


## Measured results

Native comparison, `experiment_data/tew-v11-close-support_20260925052928721429` (config frozen in that run): 18–0–14 over 32 games, no runtime faults. It scored 5–3 versus v07, 3–5 versus v10, 6–2 versus ouroboros-v10, and 4–4 versus hunter-v20 on `default_small`, `arena`, `devil`, and `schooltime`, both sides. The two-step radius lost to v10 and did not improve hunter-v20 performance. No sandbox test.
