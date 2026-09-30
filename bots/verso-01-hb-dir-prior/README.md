# verso-01-hb-dir-prior

Verso cycle 0 (X-1). Parent `verso-00-base`. One change: the `dir` head — a direction GBT fitted on Heartbreaker's
(team 62) corpus moves from the v5 actor-local features only — is embedded (`verso_heads.hpp`) and used as a prior,
`lam_dir · log p_dir(first step)` added to the OK and DIVE path scores, `lam_dir = 1.0` (fixed before screening).

- Head: 300 rounds × 3 classes, 63 leaves, 112,500 nodes = 0.9 MB (header 2.1 MB of text); held-out direction
  accuracy 0.829 on HB-1's 163 held-out games. The 27 MB model (0.856) screened no better as a prior, so the small
  one ships. C++ evaluator parity with XGBoost margins: max |Δ| 7.5e-6, 0 argmax differences on 3,000 rows.
- Parity: with `VERSO_PARAMS=lam_dir=0` golden-identical to the base (trauma B, devil A: 10,301 turns, 0 divergent);
  at the compiled defaults it reproduces the `c0-hb-small~l1` arm (file-loaded head) exactly (trauma B, 12,217
  turns, 0 divergent). The measured arm and this directory are the same behaviour.
- D-032 vs `verso-00-base`, seeds 1–3: **ACCEPT**. Pool win 0.698 → 0.848, econ~ +0.052 [+0.019, +0.081];
  generalisation win 0.568 → 0.618, econ~ +0.013 [−0.017, +0.042]; units and length at r100 +0.15 to +0.33 on
  both panels; every self-inflicted death rate down.
- Sandbox CPU (judge wasm, 4 dense maps × both seats vs ares-v06): p50 4.4–8.6 M, max 11.53 M points/turn, 0 errors.
- File-mapped head loading is compiled out under `__wasm__`; `verso.hpp` otherwise equals the base's.
