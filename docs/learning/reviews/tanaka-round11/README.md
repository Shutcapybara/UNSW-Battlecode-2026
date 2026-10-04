# Round 11 audit

Run `tools/tanaka/round11_audit.py` with the main checkout's `.venv/bin/python`, `nice -n 10`, `OPENBLAS_NUM_THREADS=1` and `OMP_NUM_THREADS=1`. Sources default to the frozen adjacent snapshots; `--sources` supports a later owner revision. The expected-outcome assertions preserve this audit, including the current A10b omission, and must be revised when checking its repair. Output is under `/tmp/tanaka-r11`.

Only deterministic synthetic selector probes, frozen local k16 result tables/indexes, published development predictions and HB development exports are read. No engine, fitting, confirmation or live outcome read occurs. `audit.json` contains hashes and aggregate results; `k16-pairs.csv` is a compact freeze of local seed-1–3 paired outcomes. Source k16 paths are in the helper; published development paths are in the main checkout. A changed source input should be compared against these hashes before interpreting a reproduction. Synthetic scratch names may change.
