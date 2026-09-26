# tew-v07-production-ladder

Lineage: Tew. Previous branch: `tew-v06-safe-fallback`. Strategy parent: `bots/ouroboros-v13-ladder`.

Borrowed complete multi-file Python ladder policy, compact-map doctrine, safety evaluator, route/world model, and sonar modules from Ouroboros v13. This is a controlled strategy transfer from the leading current all-functional tournament entry, not a claim of novel Tew logic.

Hypothesis: its compact-map ladder (attacks, frequent splitting, pearl ownership, exploration, and safety vetoes) will outperform the Tew Hunter v11 adaptations against the known baselines.

Comparison: native `default_small` and `arena`, both sides, versus ouroboros-v10, hunter-v20, and Tew v04/v06. Results pending. The parent README reports native sandbox CPU tests; this copied Tew build has not yet been sandbox-checked.


## Measured results

Native only; no sandbox check on this copied package. Small-map comparison `experiment_data/tew-v07-production-ladder_20260925044748879208`: 12–0–4 across 16 games, no runtime faults. It scored 4–0 versus v04, 4–0 versus v06, 3–1 versus ouroboros-v10 and 1–3 versus hunter-v20 on `default_small` and `arena`, both sides. Held-out maps comparison `experiment_data/tew-v07-production-ladder_20260925045104973067`: 11–0–5 across 16 games, no runtime faults; 4–4 versus v08 and 7–1 versus hunter-v20 on Colosseum, devil, schooltime and stronghold, both sides. Across these two configurations it went 23–9 (no draws/errors/runtime faults). Against hunter-v20, it went 8–4 across six maps; `arena` and `default_small` were weak (1–3 combined), while it went 7–1 across the four held-out maps. The 4–4 v07/v08 split gives no evidence that v08's aggression tweak is better.

Champion among measured Tew variants. The result comes from 32 native games against the selected pool, not the full eleven-map roster. A separate arena judge-sandbox comparison against hunter-v20 (`experiment_data/tew-v07-production-ladder_20260925045728976040`) completed 1–1 with no errors/runtime faults; reported candidate peak was 48.6M CPU points per turn and 21.6 MB memory, below the 100M / 48 MB limits for these two games. This is a narrow check, not broad worst-case proof.
