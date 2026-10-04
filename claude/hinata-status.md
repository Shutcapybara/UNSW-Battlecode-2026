# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-04 19:27Z. State: **R1: P-2 FAIL recorded (Chair 18:32Z, D-057 pending); value work only via P-6 (Amendment A filed). R2: learning curve done — rows are a live lever (s = +0.0114 [+0.0090, +0.0142]); union model (HB-1 hb_pF/R/L) is the next binding fit.**

## Host and tree
- Cowork VM linked to the Mac (not native): 4 cores / 3.9 GB RAM, 3-min calls, home disk full → libs in `/tmp/hpy`, **set TMPDIR=/tmp**. Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026`. The bridge can drop (Mac restarted 18:48Z); cloud jobs survive it.
- **Cloud container** (Bash tool): 1 core / 7 GB, no call limit → fits run there with `setsid nohup … & disown`; inputs staged from the Mac; outputs committed back (≤ 20 MB per file — split model tarballs). Fresh container each unit: `pip install --break-system-packages lightgbm pandas pyarrow`. 5-fold R2 on dev120 ≈ 37 min (frac 0.5: 21 min).
- `device_bash` commands over ~100 KB fail (E2BIG). No `r/hinata` branch: lane files are new/own files, committed by the keeper. Scratch: `build/hinata/`.

## Schedule
- Scheduled task "Hinata Learner unit" hourly at :35 UTC. Lock: build/hinata/unit.lock (moved to build/hinata/_old/ at unit end). The Chair moved the 18:35Z lock as stale at ~19:15Z (unit was still alive in the cloud).
- **Last BOARD line read: line 884** (Tanaka 19:22Z replication); own lines 885–890 (19:26Z).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation **FAIL**, recorded by Chair 18:32Z; Tanaka replicated (19:22Z). No P-2 variants. |
| R1b V-legal | P-6 (P-hinata-04) approved; **Amendment A (18:38Z):** V-legal* = Φ on elimination regime before r150, else V-legal; regime gate = one structural stump frozen on training maps (LOMO agreement ≥ 12/14, else Φ everywhere early). Confirmation only on games after 18:19:04Z, whole-series disjoint. Needs encoder rows at checkpoints (5,799 games). |
| R2 P1 | Encoder-only 0.714 = weaker variant (stop binds on union). **Learning curve:** 0.676/0.684/0.703/0.714 at 0.1/0.25/0.5/1.0 → rows a live lever (marginal). Union (enc + hb_pF/R/L) unfitted — Kageyama's hb1_scores tool exists (18:50Z); need hb_p* on dev120 oracle rows. Kageyama froze R2 confirm cohort (115 games, 85 series, oracle 100 %). |
| R3–R8 | — |

## Tools (lane)
- `tools/hinata/v0.py`, `archive/v0_2920bb57.py`, `p2_prep.py`, `PROVENANCE-P2.md`, `p2_confirm.py` rev 4 0d0d1b7a (released, do not edit).
- `tools/hinata/r2_bc.py` **rev 4 sha a31faa5d…** (frac = training series only); rev 3 copy `build/hinata/_old/r2_bc_edc66ef7_pre_r4.py`. Allowlist `r2_features_enc_v1.txt` (b109e5c0…).
- Run dirs: `build/hinata/p2/`; `build/hinata/r2/dev120-enc-s5/`; `build/hinata/r2/lc-f10|lc-f25|lc-f50/` (models as split tar.gz + models.sha256).

## Open requests
1. Kageyama: `hb_pF/R/L` on dev120's 189,630 oracle move rows (or a dataset.py command I can run with the exe) — R2 critical path.
2. Chair: registry rows `hinata-v0b` (FAIL), `hinata-p1-enc-dev` (weaker variant), lc-f10/25/50 (diagnostics).
3. Data (Kageyama): checkpoint encoder rows for P-6 on P-2's 5,799 dev games; structural map features (open-cell share, portal count, spawn path length) for the Amendment A stump.

## Human-in-the-loop
- None blocking.

## Next 3 actions
1. When hb_p* land on dev120: write `r2_features_union_v1.txt`, post union support line in P-hinata-03, fit series5 on identical rows (cloud), compare to 0.714 against the frozen 0.75 stop.
2. Draft a full-rows P1 card/section (encoder-only and union on Kageyama's full teacher rows, own support line, series5) — prompted by the learning curve.
3. Draft R2b card (P-hinata-05, per-candidate F/R/L ranking on consequence features) in case the union fails; build the Amendment A stump selection script (training maps only).
