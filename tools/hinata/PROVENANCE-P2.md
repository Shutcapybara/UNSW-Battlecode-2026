# P-2 (hinata-v0b) provenance — D-051 §6, Tanaka P-2 review §3

2026-10-04 12:42Z, hinata. Reads only the frozen development rows; no held-out map loaded.

## Source
- The registry of `build/hinata/v0/fit-lq` names code sha `3138d10777ce5490`. **Those exact bytes are not recoverable**:
  `tools/hinata/v0.py` was edited at 10:52Z, one minute after the fit (10:51Z), and was never committed in that state.
- The current source `2920bb5746c41cac…` is archived unchanged as `tools/hinata/archive/v0_2920bb57.py`.
  **It reproduces the frozen artifact exactly** (`python3 tools/hinata/p2_prep.py repro` → `build/hinata/v0/fit-lq-phi/repro.json`):
  from `train_rows.parquet` (sha256 c958e8c7f830c4c5d1b5e322adc44f16152d2a4c4c96714d5d1c30eb091cae76) it refits the
  14 cells × 8 V0b coefficients with max |diff| 0.0 against `v0b_*.json`, and the LOMO out-of-fold predictions on all
  35,948 / 35,948 game-checkpoint rows (0 unmatched) with max |diff| 0.0 for both p_v0 and p_phi. This reproduction
  was a provenance check into a scratch frame; nothing was written to `fit-lq` and no new candidate exists.
- Dependencies (VM, `/tmp/hpy`): Python 3.10.12, numpy 2.2.6, pandas 2.3.3, scikit-learn 1.7.2, duckdb 1.5.6,
  lightgbm 4.7.0 (unused by lr_q), pyarrow 25.0.1.
- Confirmation code loads the archived copy by path and checks its sha, so later edits to `tools/hinata/v0.py` cannot
  change what is confirmed.

## Comparator Φ (frozen)
`python3 tools/hinata/p2_prep.py phi` → `build/hinata/v0/fit-lq-phi/phi_post-m2_<regime>_r<k>.json`, 14 cells, full
float64. Fit: `LogisticRegression(C=1.0, fit_intercept=False, max_iter=1000)` on Φ's six shares − 0.5, both sides,
running rows, on exactly the c958e8c7 rows — the same function `cmd_confirm` would have refitted on newer data.
File hashes: `fit-lq-phi/MANIFEST.sha256.json` (sha256 d8104492d0c020a4…); registry `fit-lq-phi/registry.json`.
Coefficients (rounded here; files hold full precision):

| cell | total | units | longest | pearls | territory | deaths |
|---|---|---|---|---|---|---|
| elim r10 | 2.810 | −0.706 | −0.957 | 0.718 | 2.551 | −2.032 |
| elim r25 | 6.418 | 5.061 | −0.235 | 0.724 | 2.193 | −0.258 |
| elim r50 | 5.487 | 3.728 | 0.631 | 0.458 | 3.508 | 0.108 |
| elim r100 | 4.977 | 4.452 | 0.360 | 0.476 | 1.537 | −0.329 |
| elim r150 | 3.926 | 3.801 | 0.416 | 0.186 | 2.969 | −1.069 |
| elim r250 | 2.636 | 3.319 | 0.480 | −0.423 | 3.326 | −1.570 |
| elim r400 | 2.303 | 1.171 | 2.022 | 0.309 | 2.023 | −1.148 |
| rl r10 | 1.273 | 0.792 | 0.395 | 0.754 | 1.886 | 0.359 |
| rl r25 | 1.046 | 1.073 | 1.063 | 1.181 | 3.057 | −1.125 |
| rl r50 | 2.338 | 0.319 | 0.843 | 1.347 | 2.899 | −1.260 |
| rl r100 | 3.659 | −0.062 | 0.952 | 0.532 | 1.755 | −1.009 |
| rl r150 | 3.978 | −0.145 | 0.574 | 0.796 | 0.676 | −1.084 |
| rl r250 | 4.194 | −0.270 | 1.085 | 0.748 | 0.170 | −1.095 |
| rl r400 | 2.597 | 0.611 | 2.763 | 0.066 | 0.226 | −0.960 |

## Confirmation code (`tools/hinata/p2_confirm.py`, sha256 d298a6e7f60b140d…)
Implements Tanaka §4: `manifest` (population from manifest v2, no outcome column read; ranked, clean = series has no
P-2 game, decoded flag), `run` (gate spec must name a D-record; atomic O_EXCL claim with all hashes before any label is
read; predictions sealed read-only with their sha in the receipt; an error is written to the receipt and the claim
still blocks a second run), `score` (deterministic from the sealed predictions: per population ranked∩clean / ranked /
unranked / all-clean / all, every declared cell with n, positives, negatives, series, AUC, ΔAUC, slope and intercept
with intervals, Brier, per-map AUCs; any declared cell absent, one-class or without a model file → INCOMPLETE).
Interval: paired whole-series percentile bootstrap, 1,000, seed 7, numpy linear percentiles, one series draw per
replicate shared across all cells, both models and all populations. The old `v0.py confirm` is superseded and must
not be used for P-2.
