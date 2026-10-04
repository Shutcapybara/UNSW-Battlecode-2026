# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-04 23:35Z (unit started 22:36Z, still running: A4/A5 fits on the cloud core). State: **R2 battery: selector rev 7 af1c87e0… PASSED by Tanaka (23:23Z; software hold closed, not a numerical battery PASS). A0 0.6977, A1 (HB-1 vector, trees) 0.7184 [0.7101, 0.7278] = best so far (+0.0039 [+0.0018, +0.0060] over A3-400; +0.0207 over A0). A4, A5 fitting. Full rows landed (2,753,685 F/R/L oracle moves, 14.6× dev120): folds posted, r2_full.py exact-parity verified, waiting for keeper commit + Mac RAM to queue. Placeholder A3-400 model handed to Kageyama for the p1 slot (Chair 23:07Z / D-065).**

## Host and tree
- Cowork VM linked to the Mac: 3-min calls; VM has no pyarrow/lightgbm (`/tmp/hpy` gone) — stdlib only. `/sessions` disk full; writes into the mounted checkout work.
- **Cloud container** (Bash tool): 1 core / 8 GB, fresh each unit: `pip install --break-system-packages lightgbm pandas pyarrow numpy torch` (plain PyPI; the pytorch.org index is blocked by the proxy). Stage from the Mac (tar folders first: `build/hinata/xfer/hb1_dev120.tar`), recreate under /home/claude/repo, run with `setsid nohup … &`, copy back via /mnt/user-data/outputs/<fresh dir>/ + device_commit_files, then compare sha256 on the Mac.
- Costs, 1 core: A1 (270 feats, 800 rounds) ≈ 47 min with contention; A3/A4 ≈ 70 min; A10b ≈ 8–17 min.
- **Mac learn queue** (`build/learn/queue/`, format docs/learning/learn-queue.md): runs only code committed on main; heavy jobs take HEAVY.lock; 14 workers. Use for all full-row fits.
- No `r/hinata` branch: lane files are new/own files, committed by the keeper. Scratch: `build/hinata/`.

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (moved to build/hinata/_old/ at unit end).
- **Last BOARD line read: line 1044** (sugawara 23:28Z); own lines 1015–1016 (… rev 7), 1044 (full-row ready), 1045–1047 (A1, folds, placeholder).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). No variants. |
| R1b V-legal (P-6) | FALLBACK (observable stump, best LOMO 11/14). V-legal\* privileged diagnostic (D-060 §F). Waits behind the battery. |
| R2 P1 battery (dev120) | A0 0.6977 [0.6891, 0.7069]; **A1-400 0.7184 [0.7101, 0.7278]**; A1-800 0.7158; A3-400 0.7145 [0.7061, 0.7239]; A3-800 0.7114; A10-e4 0.6727; A10b 0.6785 [0.6694, 0.6875]; curve f25 0.6419 / f50 0.6582. Paired: A1−A3 +0.0039 [+0.0018, +0.0060]; A1−A0 +0.0207 [+0.0170, +0.0244]; A3−A10b +0.0360. **Pending: A4, A5 (cloud, running), A2, A6 (teacher-specific), A8 (mirror), A9 (other heads).** Selector rev 7 af1c87e0… PASS (Tanaka 23:23Z). |
| R2 full-row refit (D-064 §C) | Pre-registered P-hinata-03 §"Full-row refit" (22:50Z) + amendment (Sequence loader dropped). Folds `docs/learning/splits/PROPOSED-hinata-full-rows-folds.json` 118c78d7…. Tool r2_full.py 6be9dd8d… exact parity (trees and CNN, max Δp 0.0). Forecasts: P(best tree ≥ 0.75) 0.40; P(A10b-full beats trees) 0.15. |
| R3–R8 | — (P-7 self-play: if trees selected, actor = network distilled from trees, gate top-1 ≥ 0.95 and acc within 0.01, D-063 §D) |

## Tools (lane)
- `tools/hinata/v0.py`, `archive/v0_2920bb57.py`, `p2_prep.py`, `PROVENANCE-P2.md`, `p2_confirm.py` rev 4 0d0d1b7a.
- `r2_bc.py` rev 4 a31faa5d…; `r2_features_enc_v1.txt` b109e5c0….
- **`r2_battery.py` rev 7 af1c87e0…** (PASS); rev 6 archived `archive/r2_battery_3f56b4b2.py`; `r2_battery_rev6_synth.py` 32cb0c62…, **`r2_battery_rev7_synth.py` c877f6fc…**.
- `r2_cnn.py` e237fb76… (A10); `r2_cnn_b.py` ba151375… (A10b + curve); **`r2_full.py` 6be9dd8d…** (full-row refit: `trees --arm`, `cnn`, `rows`); `regime_stump.py` de7d07aa… (P-6).
- Run dirs: `build/hinata/r2/battery/{A0-u, A1-u, A3-u, A10-u, A10b-u, A10b-f50, A10b-f25}`; placeholder `build/hinata/r2/placeholder/A3-400-f0.{txt,json}` (2dfb0705…); queue draft `build/hinata/queue-drafts/hinata-01-a10b-full.json`.

## Open requests
1. **Keeper/Chair:** commit tools/hinata/{r2_full.py, r2_battery.py rev 7, r2_cnn.py, r2_cnn_b.py, r2_battery_rev7_synth.py} to main (learn queue needs committed code).
2. **Asahi:** Mac RAM (trees ≈ 18 GB peak, A5 ≈ 23 GB, CNN ≈ 8 GB).
3. **Kageyama:** Data-confirmed `--cohort-series` JSON {team: frozen-cohort series} (Tanaka reproduced counts at docs/learning/reviews/tanaka-round12/cohort-series.json: 213=14, 264=11, 55=10, 952=16, 91=6, …); size target for the p1-slot model (4 MiB zip).
4. **Chair:** registry rows hinata-v0b (FAIL), hinata-p1-enc-dev, lc-f10/25/50, A3u (8807488c…), A10 (3e23db4a…), A10b (6164e241…), lc-A10b-f50/f25, **A0-u (d6abd0d5…), A1-u (66444789…)**.

## Human-in-the-loop
- None blocking. (Cowork VM disk full — Chair aware.)

## Next 3 actions
1. Finish A4, A5 (cloud; resume from model files if the container died — they are not on the Mac until copied); copy runs to the Mac; then A2, A6 (rev 7 inventory); `table` once complete with Data's cohort-series file.
2. When main has r2_full.py: queue `hinata-01-a10b-full` (draft ready) and the best tree arm's full-row job (`r2_full.py trees --arm <best> --run build/learn/hinata/r2full/<arm>-full`), heavy, after Asahi's RAM answer.
3. A8 (mirror, training folds only) pre-registration on the best arm per Kageyama's mapping (encoder + HB-1 swaps); size-matched placeholder for Kageyama if asked.
