# athos-athos-x01-e-trapmargin

Athos x-experiment, single change off `bots/athos-v01-core/` (E0/P0 frozen
elsewhere; parent stream-verified 32/32 identical to monte_christo-v01-core).

Executor budget override: slack 3->5, min_area 5->8, flood caps 24/40->28/44 (override.py only; params.py byte-identical to v01).

Hypothesis: larger required room cuts the self-collision and wall deaths that dominate devil-map losses (54% of our deaths there are non-enemy).
Method: dev-roster screen (configs/athos/stream-verify.toml, 32 games) vs the
parent's 13-19 record; results in docs/athos.md and tools/athos/.
