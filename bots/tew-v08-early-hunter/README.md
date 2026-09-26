# tew-v08-early-hunter

Lineage: Tew. Parent: `tew-v07-production-ladder`; borrowed policy family: `ouroboros-v13-ladder`.

Hypothesis: Tew v07 scored 1–3 against hunter-v20 on two compact maps. Lowering the ladder's attack population gate from 3 to 2 and raising the accepted head-risk threshold from 1.0 to 2.0 may let Tew capitalize on early trade-up opportunities.

Change: compact-map doctrine only, `ladder_attack_units=2`, `ladder_risk_max=2.0`. All other policy, safety and hotspot settings match v07.

Comparison: native, both sides on `default_small` and `arena`, versus v07 and hunter-v20. Pending. No judge CPU validation.


## Measured results

Native comparison `experiment_data/tew-v08-early-hunter_20260925044925359348`: 4–0–4 across 8 games, no runtime faults; 2–2 versus v07 and 2–2 versus hunter-v20 on `default_small` and `arena`, both sides. Held-out matchup versus v07 was 4–4 over Colosseum, devil, schooltime and stronghold in `experiment_data/tew-v07-production-ladder_20260925045104973067`. Combined with the initial v07 matchup this is 8–8 across six maps. Lower attack gate with relaxed risk changes where wins occur, but did not beat v07 overall. No sandbox checks.
