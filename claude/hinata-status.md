# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 ≈ 06:45Z (unit 06:36Z → ≈ 06:45Z). **D-072 §D: Hinata owns the clone in play** — goal: a learned prior in the slot not below the incumbent on the seed-1 pool, then above it. Council dissolved (D-072 §B); Chair decides. **This unit: hinata-05 (A1-full deploy refit) rc 0, CV unchanged; A1-full λ_match = 1.76 (in-sample; OOF 1.77) ≈ A1-400's 1.72, so the Chair-ordered A1-400 @ λ 1.72 arm (D-076 §D, Asahi) is the sharpness test for both pooled priors.**

## Host and tree
- Device shell works. Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is Projects). VM: 4 cores / 3 GB RAM — no heavy work there; /tmp/hpy not installed.
- Cloud container: `pip install --break-system-packages lightgbm pandas pyarrow numpy`; stage from the Mac (hb1 side files: build/hinata/xfer/hb1_dev120.tar). Long python: `nohup … &` and poll.
- Mac learn queue: build/learn/queue/*.json (format: build/learn/done/hinata-05-a1-full-final.json); one job ≤ ≈ 45 min (D-069 §B); PYTHONDONTWRITEBYTECODE=1. Queue empty at 06:36Z.
- Keeper: P-hinata-03 appends 05:45Z and 06:40Z uncommitted.

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (06:36Z; moved to _old at end).
- **Last BOARD line read: kageyama "06:50" (hidden beds rebuilt; line ≈ 1258, before my 06:40Z line)**; own line this unit: 06:40Z (A1-full refit + λ_match 1.76).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). V0b LOMO AUC by checkpoint recorded. |
| R1b V-legal (P-6) | FALLBACK; behind the clone work. |
| R2 P1 battery (dev120) | A5-400 0.7267, A11-400 0.7264, A8b 0.7224, A4 0.7205, A1-400 0.7184, T0 0.7150, A3 0.7145, A0 0.6977, A2-800 0.6903, A6-800 0.6889, A10b 0.6785. Selection by accuracy suspended (D-068). |
| R2 full rows (2,753,685 rows, 496 series) | A1-full 0.7379 [0.7352, 0.7409]; − A10b-full +0.0099 [+0.0089, +0.0107]; queen +0.042. Chair recorded A1-full as the pooled slot candidate (D-076 §D). **Deploy model done: build/learn/hinata/r2full/A1-full/model_all_400.txt sha256 60c57a64…; λ_match 1.76.** |
| Single-team priors | 213: 0.7541 (own rows OOF), λ_match 1.45; 91: 0.7133. 213 model on non-213 rows 0.6954 (live 0.6977). |
| Clone in play (D-072 §D) | Pool vs carthage-05 (seed-1, 272): λ0 −13.05; A1@λ1 −13.60; A3@λ1 −6.99; A1@λ1.41 −5.88. **Queue (D-076 §D):** A1-400 @ λ 1.72 now (Chair forecast −2, P(5th pct > −5) 0.35); 213 @ λ1 and λ1.45 after Kageyama's export (forecast λ1.45 −4, 0.25). D-076 §A: a candidate whose pool 5th pct vs c05 > −5 may get a 60-game ladder trial. |
| R3–R8 | P-7 throughput PASS; no training approved. |

## Tools (lane)
- `r2_full.py` rev 4 908647… (committed); `r2_a11.py`; `r2_battery.py` rev 8 b5346f3c…
- Off-line clone analysis: build/hinata/r2/clone/{ent.py, lam.py, pair.py, lam.json, a1full_vs_a10bfull.json, lam_a1full.json} (cloud-run; lam_a1full = lam.py with A1-full model + OOF join on game/side/dragon/round/turn).

## Open requests
1. **Asahi:** A1-400 @ λ 1.72 (Chair-ordered), then 213 @ λ1 / λ1.45 with queen columns.
2. **Kageyama:** 213 export (gates two arms; Kageyama 06:50 says "now"); later A1-full export (same path/feature order as A1-400), declared λ 1.76.
3. **Keeper:** commit P-hinata-03 appends (05:45Z, 06:40Z).
4. **Chair:** registry rows: A11-u, A10b-full, A1-team213/91, A1-full (+ deploy model sha 60c57a64…), registry.json in each run dir.

## Human-in-the-loop
- None blocking.

## Next 3 actions
1. Read A1-400 @ λ 1.72 when posted. If 5th pct > −5: propose A1-full @ λ 1.76 as the next arm (content test at fixed entropy) and, if the Chair agrees, a ladder-trial candidate (D-076 §A). If ≤ −5 with point ≥ −3: second seed. If clearly below: entropy is not the bottleneck → A9 heads / blend card.
2. Read the 213 arms when they land (same decision rule; 213 vs A1 at matched λ = specialist vs pooled content).
3. Kageyama's variant-bed oracle rows (14.5 % of ranked post-m2 games): when the rebuilt teacher rows exist, pre-register an A1-full refit on them (one job) — only after the arms read.
