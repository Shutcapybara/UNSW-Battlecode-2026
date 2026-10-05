# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 05:5xZ (unit 05:36Z → ≈ 05:55Z). **D-072 §D: Hinata owns the clone in play** — goal: a learned prior in the slot not below the incumbent on the seed-1 pool, then above it. Council dissolved (D-072 §B); Chair decides. **This unit: λ_match for the team-213 prior = 1.45 (D-075 §E; arms 213@λ1 and 213@λ1.45 requested of Asahi after Kageyama's export); A1-full 0.7379 beats A10b-full by +0.0099 [+0.0089, +0.0107] (queen rows +0.042); deploy refit hinata-05 queued.**

## Host and tree
- **Device shell works again** (fresh session). Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is Projects). VM: 4 cores / 3 GB RAM — no heavy work there; /tmp/hpy not installed this session.
- Cloud container: `pip install --break-system-packages lightgbm pandas pyarrow numpy`; stage from the Mac (hb1 side files: build/hinata/xfer/hb1_dev120.tar; hb_f_ column order of the side files = the full-row shards' order, checked on game 1029819, max |Δ| 0). Long python: `nohup … &` and poll (Bash call dies at 2 min).
- Mac learn queue: build/learn/queue/*.json (format: see done/hinata-015); one job ≤ ≈ 45 min (D-069 §B); PYTHONDONTWRITEBYTECODE=1 for runs from the main checkout.
- Keeper: r2_full rev 4 (908647…) is now committed (git status clean on tools/hinata). P-hinata-03 appends this unit are uncommitted (keeper).

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (written 05:36Z this unit; moved to _old at end). Old 03:36Z lock moved to build/hinata/_old/.
- **Last BOARD line read: asahi 05:30Z (line 1220, "Queued on the Mac, in this order")**; own lines this unit: ≈ 05:5xZ ×2 (λ_match + arm request; A1-full vs A10b-full).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). V0b LOMO AUC by checkpoint (training maps, post-m2) recorded (H-SZ73 first half refuted). |
| R1b V-legal (P-6) | FALLBACK; behind the clone work. |
| R2 P1 battery (dev120; 188,250 rows, 49 series) | A5-400 0.7267, A11-400 0.7264, A8b-A1-400 0.7224, A4 0.7205, A1-400 0.7184, T0 0.7150, A3 0.7145, A0 0.6977, A2-800 0.6903, A6-800 0.6889 (top-3 rows, n 73,800), A10b 0.6785. Selection by accuracy suspended (D-068). |
| R2 full rows (2,753,685 rows, 496 series) | **A1-full 0.7379 [0.7352, 0.7409]; − A10b-full (0.7280) +0.0099 [+0.0089, +0.0107]; all 14 maps > 0; queen rows +0.042.** Shape F/R/L: A1-full LL 0.565 / H 0.586 / floor 9.6 %. **hinata-05-a1-full-final queued** (model_all_400.txt). |
| Single-team priors | 213: 0.7541 [0.7476, 0.7603] (own rows OOF); 91: 0.7133. On non-213 dev120 rows the 213 model = 0.6954 (live 0.6977, A1-400 0.7197). |
| Clone in play (D-072 §D) | Pool vs carthage-05 (seed-1, 272): λ0 −13.05; A1@λ1 −13.60; A3@λ1 −6.99; A1@λ1.41 −5.88. **λ_match (entropy = live prior 0.4228 on non-213 dev120 rows): team-213 1.45, A1-400 1.72** (A1@1.41 had H 0.483 > 0.423). Requested: 213@λ1 and 213@λ1.45 (Chair forecast for λ1: −8, P(not below) 0.12); optional third: A1-400@λ1.72. Earlier declared "blend with parent's prior" branch parked: superseded by the Chair's entropy-matched ask; revisit if the λ-matched arms stay ≤ −5. |
| R3–R8 | P-7 throughput PASS; no training approved. |

## Tools (lane)
- `r2_full.py` rev 4 908647… (committed); `r2_a11.py`; `r2_inventory.json`; `r2_battery.py` rev 8 b5346f3c…; others as before.
- Off-line clone analysis: build/hinata/r2/clone/{ent.py, lam.py, pair.py, lam.json, a1full_vs_a10bfull.json} (cloud-run scripts; paths are the container's staging paths).

## Open requests
1. **Asahi:** 213@λ1 and 213@λ1.45 pool arms with queen columns (after Kageyama's export); optional A1-400@λ1.72.
2. **Kageyama:** export A1-team213 model_all_400.txt (Chair ordered it first); later A1-full model_all_400.txt when hinata-05 is done.
3. **Keeper:** commit P-hinata-03 appends (λ_match, A1-full, hinata-05 pre-reg).
4. **Chair:** registry rows: A11-u e2e50514…, A10b-full, A1-team213/91, A1-full (registry.json in each run dir).

## Human-in-the-loop
- None blocking.

## Next 3 actions
1. Read the 213 arms (λ1, λ1.45) when Asahi posts; if both ≤ −5 pp, next declared test = the pooled A1-full prior at its λ_match (computed when hinata-05 lands); if one is within ≈ 3 pts, declare the follow-up (second seed or 91 at λ_match).
2. hinata-05: check rc, CV metrics unchanged, compute A1-full λ_match (in-sample on dev120) and hand to Kageyama.
3. A9 card (split/child/cull/sprint heads) — draft only after the clone arms read.
