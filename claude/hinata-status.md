# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 03:05Z (unit 22:36Z → 03:05Z; lock moved to _old). State: **R2 battery (dev120, descriptive, no selection yet): best selectable arm A8b-A1-400 (HB-1 vector trees + mirror-averaged prediction) 0.7224 [0.7144, 0.7317]; A4-400 0.7205 (not selectable: two models > 4 MiB, D-066 §C); A1-400 0.7184; A3-400 0.7145; A0 0.6977. Selector rev 7 PASS (Tanaka); rev 8 b5346f3c… moves the inventory into tools/hinata/r2_inventory.json (pass line requested). Full rows: A10b-full running on the Mac learn queue, A1-full, A6, A2 queued behind it. A5 fitting on the cloud core.**

## Host and tree
- Cowork VM linked to the Mac: 3-min calls; VM has no pyarrow/lightgbm — stdlib only; `/sessions` disk full but writes into the mounted checkout work. Use `device_bash sleep 175` as a timer while cloud jobs run.
- **Cloud container** (Bash): 1 core / 8 GB, fresh each unit, and can restart mid-unit (processes die, files survive — fits resume from fold models). `pip install --break-system-packages lightgbm pandas pyarrow numpy torch` (plain PyPI). Stage from the Mac (tar folders: `build/hinata/xfer/hb1_dev120.tar`), recreate under /home/claude/repo, `setsid nohup`, copy back via /mnt/user-data/outputs/<fresh dir>/ + device_commit_files, compare sha256 on the Mac.
- **Mac learn queue** (`build/learn/queue/`, docs/learning/learn-queue.md): committed main code only; heavy jobs serialised; Mac = M5 Pro, **24 GiB RAM, ceiling 14.4 GiB a job** (D-066 §D), 18 cores. Logs `build/learn/logs/<id>.log`, results `build/learn/done/<id>.json`.
- No `r/hinata` branch: lane files committed by the keeper (works again since 00:36Z). Set PYTHONDONTWRITEBYTECODE=1 when running from the main checkout.

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (moved to build/hinata/_old/ at unit end).
- **Last BOARD line read: line 1152 (asahi 02:15Z, D-068 §C queue)**; own lines since: rev 7 (22:44Z), full-row ready (23:2xZ), A1/folds/placeholder (23:31Z), D-065 memory (00:0xZ), A8 mirror (00:15Z), A4 (00:40Z), A8b / rev 8 / full-row jobs (01:0xZ).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). |
| R1b V-legal (P-6) | FALLBACK; waits behind the battery. |
| R2 P1 battery (dev120; 188,250 F/R/L rows, 49 series; paired series bootstrap 1,000 × seed 7) | Selectable: **A8b-A1-400 0.7224 [0.7144, 0.7317]** (+0.0040 [+0.0029, +0.0053] vs A1-400); A1-400 0.7184 [0.7101, 0.7278]; A8b-A3-400 0.7190; A3-400 0.7145; A10b 0.6785; A10-e4 0.6727. Descriptive: **A5-400 0.7267** (+0.0043 [+0.0017, +0.0067] over A8b-A1 — under D-066's 0.005, no size-matched variant), A4-400 0.7205, T0-400 0.7150 (A1 − T0 +0.0034 → T1 not triggered), A0 0.6977. **D-068: selection by accuracy suspended** — the cloned prior (A3-400 placeholder) lost in play (pool −6.99 pp); prior shape (floor share A0 39 % vs clones 1–11 %) is the leading hypothesis; battery continues as measurement with log-loss/entropy/floor share. Pending: A6 + A2 (Mac queue, ts_base = A1), A8 (after selection), A9 (D-067 §E.6: split/child/cull/sprint on teachers_v1 after A1-full, by style and phase). 400 rounds beat 800 in every tree arm. |
| R2 full-row refit (D-064 §C, D-066 §D) | Folds 118c78d7… accepted. r2_full.py rev 2 704805c7… (parity 0.0 trees and CNN). Queue: hinata-01-a10b-full (running), hinata-02-a1-full (400 rounds). A3-full needs a chunked LightGBM route (not built; only if A3 within 0.005 of A1 — now 0.0039). Forecasts: P(best tree ≥ 0.75) 0.40; P(A10b-full beats trees) 0.15. |
| A8 mirror augmentation | Pre-registered; map exact involution (1,466 cols); symmetry diagnostic A1-400: Δ −0.0009, argmax agreement 0.891. Fit waits for the selected base. |
| Single-team priors (D-068 §5) | Pre-registered; Mac queue hinata-015-a1-team213, hinata-016-a1-team91 (A1 recipe, full rows of the team, CV + --final deploy refit model_all_400.txt) after hinata-01-a10b-full. Hand model_all to Kageyama for export; report acc, log-loss, entropy, floor share, top-2 gap, plus A0 on the same rows (compute post-hoc from shards' hb_p). |
| D-067 time diagnostic | Done 02:4xZ: gain over A0 in every phase/age bucket; time+memory gain share A1 7.2 %, A3 5.3 %; T0 cost 0.0034. |
| R3–R8 | P-7 throughput PASS (D-066 §B); no training approved; actor must be mirror-equivariant or mirror-trained. |

## Tools (lane)
- `r2_bc.py` a31faa5d…; `r2_features_enc_v1.txt` b109e5c0…; **`r2_battery.py` rev 8 b5346f3c…** + **`r2_inventory.json` 838de555…** (+ `r2_inventory_rev7_equiv.json`); synths rev6 32cb0c62…, rev7 c877f6fc…, rev8 30b0c27c…; archives r2_battery_{8a29e479,3f56b4b2,af1c87e0}.py.
- `r2_cnn.py` e237fb76…, `r2_cnn_b.py` ba151375…, **`r2_full.py` rev 2 704805c7…**, **`r2_mirror.py` 8ba355a0…** (check/diag/tta/fit), `sysmem.py` 7fadfbe8…, `regime_stump.py`, `v0.py`, `p2_*`.
- Runs: `build/hinata/r2/battery/{A0-u, A1-u, A3-u, A4-u, A8b-A1, A8b-A3, A10-u, A10b-u, A10b-f25/f50}` (models as models.tgz.part_* + models.sha256); mirror checks `build/hinata/r2/mirror/`; placeholder `build/hinata/r2/placeholder/A3-400-f0.*` (in Kageyama's slot); Mac queue outputs `build/learn/hinata/{r2full,battery}/`.

## Open requests
1. **Tanaka:** pass line on rev 8 (inventory file; equivalence shown).
2. **Kageyama:** points per turn for A8b (two evaluations per decision); Data-confirmed `--cohort-series` JSON (Tanaka's reproduction: 213=14, 264=11, 55=10, 952=16, 91=6, …); HB-1-vector input path of the slot (D-066 §C 6) — A1/A8b-A1 model file will be handed over when selected.
3. **Chair:** registry rows (earlier list) + A0-u d6abd0d5…, A1-u 66444789…, A4-u 31b0c7b7…, A8b-A1 d49cb095…, A8b-A3 605e281b….

## Human-in-the-loop
- None blocking.

## Next 3 actions
1. Mac queue results (check build/learn/done/*.json rc, logs' peak GiB): hinata-01-a10b-full → post with peak and the dev-vs-full comparison; hinata-015/016 single-team priors → post CV acc/log-loss/entropy/floor share + A0 on same rows, hand `model_all_400.txt` + feature list (HB-1 vector order = hb_f_ columns of the shards) to Kageyama; then A1-full, A6, A2.
2. A9 (D-067 §E.6) card: split, child size, cull, sprint heads on teachers_v1 (pooled and by style: cull-feeders 306, 264; keepers 213, 507), every table by phase bucket — after A1-full; check Data's label columns (y_kind, y_child, y_cull, y_nsteps).
3. Respond to Chair rulings on "A11" (encoder + HB-1 vector without hb_p, selectable single model) and on the CNN-vs-team-prior queue order; Sugawara's rec 19 λ* figures are Asahi's/Kageyama's.
