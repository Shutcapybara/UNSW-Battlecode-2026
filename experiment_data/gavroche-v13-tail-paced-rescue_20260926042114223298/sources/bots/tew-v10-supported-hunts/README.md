# tew-v10-supported-hunts

Lineage: Tew. Parent: `tew-v07-production-ladder`; strategy base `ouroboros-v13-ladder`.

Hypothesis: Tew v07 loses some compact-map games to hunter-v20 despite comparable population because it initiates trade-up attacks without checking whether local friendly support can absorb the trade. Use visible head density in the current 7×7 view to gate attacks.

Change: `ladder_decide()` counts visible allied and enemy heads within wrapped topology distance 6 (the full view's Manhattan radius). It permits a trade-up attack only when allied heads (excluding self) are at least as numerous as enemy heads. Splitting, growth, exploration, safety vetoes, and sonar are unchanged.

Comparison: see measured native run below. No sandbox check.


## Measured results

Native comparison, `experiment_data/tew-v10-supported-hunts_20260925052409317574` (config frozen in that run): 23–0–17 over 40 games, no runtime faults. It scored 4–4 versus each Tew v07, v08 and v09; 6–2 versus ouroboros-v10; and 5–3 versus hunter-v20 across `default_small`, `arena`, `devil`, and `schooltime`, both sides. Its 5–3 hunter result matches v07 on these same four maps; its broader cross-line result is encouraging but not proof the support gate caused the gains. Native only; no sandbox test for v10.
