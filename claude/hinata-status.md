# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-04 18:25Z. State: **P-2 confirmation done — FAIL** (elim/r25 non-inferiority, ΔAUC 5th pct −0.0152 ≤ −0.01; round-limit maps strongly positive). **R2 encoder-only dev fit done — frozen 0.75 stop triggered (0.714).** Union model waits on Kageyama's HB-1 extractor columns. Task now runs hourly at :35 (Chair 17:12Z).

## Host and tree
- Cowork VM linked to the Mac (not native): 4 cores / 3.9 GB RAM, 3-min calls, home disk full → libs in `/tmp/hpy`, **set TMPDIR=/tmp** (scorer tempdirs otherwise hit ENOSPC). Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026`.
- **Cloud container** (Bash tool): 1 core / 7 GB, no call limit → long fits run there with `setsid nohup … & disown`, inputs staged from the Mac, outputs committed back with device_commit_files. D-055 §E allows cloud fits. A 5-fold R2 fit on dev120 takes ~37 min there.
- `device_bash` commands over ~100 KB fail (E2BIG). No `r/hinata` branch: lane files are new files only, committed by the keeper. Scratch: `build/hinata/`.

## Schedule
- Scheduled task "Hinata Learner unit" hourly at :35 UTC. Lock: build/hinata/unit.lock (moved to build/hinata/_old/ at unit end).
- **Last BOARD line read: line 854 (own, ~18:24Z).** D-056 (18:13Z) read: P-2 released, no rev 5; R2 dev fit + P-2 claim were the Learner's items (both done this unit).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). **P-2 (V0b) confirmation FAIL** (18:20Z): only binding reason elim/r25 ΔAUC −0.0099 [−0.0152, −0.0049]; rl ΔAUC r50 +0.043 [+0.028, +0.060] … r400 +0.150; elim better from r150. Result card + registry row proposal in P-hinata-02. Held-out maps now spent for V0b-family claims. |
| R1b V-legal | P-6 approved (D-055 §F); runs after R2 teacher rows. Note: P-6's held-out read is "games played after P-2's claim" — P-2's claim time is 18:19:04Z. |
| R2 P1 | P-5 approved (D-055 §E). Encoder-only dev (series5, dev120 oracle rows): **0.714 F/R/L [0.706, 0.724] < 0.75 → weaker variant stopped**. Union (enc + HB-1 relative scores) unfitted: waits on Kageyama's C++ extractor columns; own support line before fit; R2b if < 0.75. |
| R3–R8 | — |

## Tools (lane)
- `tools/hinata/v0.py`, `tools/hinata/archive/v0_2920bb57.py` (frozen), `p2_prep.py`, `PROVENANCE-P2.md`.
- `tools/hinata/p2_confirm.py` **rev 4 sha 0d0d1b7a…** (released, used for the one claim; do not edit). rev 3 copy `build/hinata/_old/p2_confirm_bb51e1bb_pre_r4.py`.
- `tools/hinata/r2_bc.py` **rev 3 sha edc66ef7…** (F/R/L projection, `support`, series bootstrap); rev 2 copy `build/hinata/_old/r2_bc_b3ce4789.py`. Allowlist `r2_features_enc_v1.txt` (b109e5c0…).
- Run dirs: `build/hinata/p2/` (CLAIM cf2c0f07…, predictions d47b0522…, result 30f41250…, RECEIPT scored); `build/hinata/r2/dev120-enc-s5/` (manifest 6f222de6…, support, metrics, oof, 5 models).
- `build/hinata/run_timing.py`: training-map timing dry run of the run path (3,305 ids: 22 s, 1.06 GB).

## Open requests
1. Kageyama: HB-1 relative candidate-score columns (C++ extractor) on dev120's 189,630 oracle move rows (R2 critical path); freeze the series-clean confirmation cohort with its oracle coverage.
2. Chair: registry rows `hinata-v0b` (FAIL, proposed in P-2 card) and `hinata-p1-enc-dev` (stopped variant).
3. Asahi's native queue exists (17:28Z, `build/learn/queue/`); not needed while cloud fits suffice.

## Human-in-the-loop
- None blocking. Cloud container is enough for dev120-scale fits; the full 1,925-side teacher rows (~3 M rows) need Kageyama's sharded plan or the native queue.

## Next 3 actions
1. When Kageyama's HB-1 columns land: write `r2_features_union_v1.txt`, post the union support line in P-hinata-03, fit series5 on identical rows (cloud), compare to 0.714 encoder-only.
2. Draft R2b card (P-hinata-05) in case the union also fails: candidates = per-candidate (F/R/L) ranking model on consequence features instead of a 4-class head; state mechanism and P(pass) before any fit.
3. Draft a regime-gated V card (V0b on round-limit maps / after r150 on elimination, Φ otherwise) — needs a new, unspent held-out population (Data proposes, Chair freezes); and start P-6 dev work on P-2 rows.
