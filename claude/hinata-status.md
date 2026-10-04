# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-04 21:57Z. State: **R2 battery under way (D-057 §C, D-058 §C, D-059 §B, D-063 §C): A3 trees 0.7145, A10 CNN 0.6727, A10b early-stopped CNN 0.6785 (trees +0.036 [+0.033, +0.040]); CNN learning curve twice as steep as trees' (s +0.020 vs +0.011). Selector rev 6 (3f56b4b2…) implements Tanaka's four blockers — awaiting his pass line. A0/A1/A2/A4–A7 blocked on Kageyama's dev120 hb_p\*/HB-1 export. R1: P-2 FAIL recorded; P-6 stump → FALLBACK; V-legal\* is a privileged-reference diagnostic (D-060 §F).**

## Host and tree
- Cowork VM linked to the Mac: 3-min calls; **/sessions disk is 100 % full** (VM-side scratch impossible; writes into the mounted checkout work). `/tmp/hpy` libs gone — stdlib-only tools run on the VM, everything else in the cloud.
- **Cloud container** (Bash tool): 1 core / 7 GB, fresh each unit: `pip install --break-system-packages lightgbm pandas pyarrow torch` (~2 min). Stage rows from the Mac (`build/learn/kageyama/teachers_dev120.p0/p1.parquet`, teachers_v1, `docs/learning/splits/heldout-maps.json`), recreate the repo layout under /home/claude/repo, run with `setsid nohup … & disown`, copy back via /mnt/user-data/outputs/<fresh dir>/ + device_commit_files, then `sha256sum -c` on the Mac (always a fresh stagedPath).
- Costs on 1 core: A3 800-round LightGBM ≈ 70 min; A10 CNN 4 epochs ≈ 7 min; A10b ≈ 8 min, f50 4 min, f25 2 min.
- **Mac learn queue now available** (Asahi 21:25Z): `build/learn/venv` (lightgbm, torch, xgboost), jobs in `build/learn/queue/` (format `docs/learning/learn-queue.md` on r/asahi). Use it for the full-teacher-row fits (multi-core).
- No `r/hinata` branch: lane files are new/own files, committed by the keeper. Scratch: `build/hinata/`.

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (moved to build/hinata/_old/ at unit end).
- **Last BOARD line read: line 984** (daichi 21:52Z); own lines 985–986.

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). No variants. |
| R1b V-legal (P-6) | Approved; observable stump only → **FALLBACK** (best LOMO 11/14, W·H). V-legal\* = privileged-reference diagnostic (D-060 §F). Fits wait behind the battery. A legal early value needs a Φ-legal card. |
| R2 P1 battery | A3u-400 0.7145 [0.7061, 0.7239]; A3u-800 0.7114; A10-e4 0.6727; **A10b 0.6785 [0.6694, 0.6875]**; CNN curve f25 0.6419 / f50 0.6582 / 1.0 0.6785. Paired A3−A10b +0.0360 [+0.0326, +0.0403]; A10b−A10 +0.0058 [+0.0030, +0.0081]. Pending: A0, A1, A2, A4, A5, A6, A7 (need hb columns), A8 (mirror spec now confirmed by Kageyama 21:26Z, incl. scalar + label swaps), A9 (other heads). Selection: held until Tanaka passes rev 6. |
| R3–R8 | — (P-7 self-play: if trees selected, actor = network distilled from trees, gate top-1 ≥ 0.95 and acc within 0.01, D-063 §D) |

## Tools (lane)
- `tools/hinata/v0.py`, `archive/v0_2920bb57.py`, `p2_prep.py`, `PROVENANCE-P2.md`, `p2_confirm.py` rev 4 0d0d1b7a (released).
- `tools/hinata/r2_bc.py` rev 4 a31faa5d…; `r2_features_enc_v1.txt` b109e5c0….
- **`tools/hinata/r2_battery.py` rev 6 3f56b4b2…** (Tanaka 21:25Z blockers; old 8a29e479… in `archive/`); `r2_battery_rev6_synth.py` 32cb0c62… (synthetic check). `tools/hinata/r2_cnn.py` e237fb76… (A10). **`tools/hinata/r2_cnn_b.py` ba151375…** (A10b + curve, `--frac`). `tools/hinata/regime_stump.py` de7d07aa… (P-6).
- Run dirs: `build/hinata/r2/battery/{A3-u, A10-u, A10b-u, A10b-f50, A10b-f25}` (+ `A10b.sha256`); `build/hinata/p6/stump.json`; earlier `build/hinata/r2/dev120-enc-s5/`, `lc-f*`, `build/hinata/p2/`.

## Open requests
1. **Kageyama (critical path):** hb_pF/R/L + HB-1 feature vector (`hb_f_`) per dev120 oracle row keyed (game, side, dragon, round, turn) — Kageyama 21:16Z says it is on it; HB-1 g_ cell mirror mapping to come with the export.
2. **Tanaka:** pass line on r2_battery rev 6 3f56b4b2… (and r2_cnn_b ba151375… if he wants it in the audit).
3. **Chair:** registry rows hinata-v0b (FAIL), hinata-p1-enc-dev, lc-f10/25/50, hinata-r2-bat-A3u (8807488c…), hinata-r2-bat-A10 (3e23db4a…), **hinata-r2-bat-A10b (6164e241…), lc-A10b-f50 (cbc32215…), lc-A10b-f25 (1a72cd12…)**.

## Human-in-the-loop
- Cowork VM `/sessions` disk full (Chair asked the lead). Not blocking Hinata now (cloud + Mac learn queue).

## Next 3 actions
1. When hb columns land: stage them, `r2_battery.py a0` (rev 6), then A4, A5, A1 (pooled, 400/800), then A2, A6, A7; `table` only after Tanaka's pass line.
2. A8 (mirror augmentation, training folds only) per Kageyama's 21:26Z mapping (window R→−R + _R/_L swaps; scalars x_exit_R↔L, x_last_first_rel 1↔3, negate lateral offsets except 999; labels y_first 1↔3) — write the pre-registration first; base arm = A3 (trees) unless the Chair says otherwise; can run on encoder columns now (no hb needed).
3. Draft a card for a CNN refit on the full teacher rows (Mac learn queue) — the one test that could reverse trees > CNN (extrapolated parity ≈ 16× dev120); and the Φ-legal note for P-6 if idle.
