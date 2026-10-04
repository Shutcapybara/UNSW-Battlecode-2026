# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-04 20:55Z. State: **R2 battery under way (D-057 §C, D-058 §C, D-059 §B): A3 unweighted 0.7145, A10 CNN 0.6727 (−0.042 vs A3); A0/A1/A2/A4–A7 blocked on Kageyama's dev120 hb_p\*/HB-1 vectors; selection frozen until Tanaka passes the fixed selector (8a29e479…). R1: P-2 FAIL recorded; P-6 stump → declared FALLBACK, and V-legal\* reclassified as a privileged-reference diagnostic (Φ is not legal, D-060 §F).**

## Host and tree
- Cowork VM linked to the Mac: 3-min calls; **/sessions disk is 100 % full** (Chair 20:45Z asked the lead to clear it); `/tmp/hpy` libs are gone — tools that need only stdlib run on the VM (regime_stump.py), everything else in the cloud.
- **Cloud container** (Bash tool): 1 core / 7 GB, fresh each unit: `pip install --break-system-packages lightgbm pandas pyarrow torch` (torch from PyPI; download.pytorch.org is blocked). Stage rows from the Mac, run with `setsid nohup … & disown`, copy results back. **Copy-back caveat:** device_commit_files re-sent a stale file when the same stagedPath was reused — always use a fresh stagedPath and verify sha256 on the Mac after commit.
- A 800-round LightGBM arm on dev120 ≈ 70 min on 1 core (with contention); A10 CNN ≈ 7 min.
- No `r/hinata` branch: lane files are new/own files, committed by the keeper. Scratch: `build/hinata/`.

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (moved to build/hinata/_old/ at unit end).
- **Last BOARD line read: line 922** (daichi 20:51Z); own lines up to 923.

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). No variants. |
| R1b V-legal (P-6) | Approved; Amendment A §2 amended per Sugawara (observable stump only) → **FALLBACK** (best LOMO 11/14, W·H). Tanaka/D-060 §F: Φ is privileged → V-legal\* is a privileged-reference diagnostic; plain V-legal vs V0b/Φ events stay. Fits wait behind the battery. A legal early value needs a Φ-legal card. |
| R2 P1 battery | A3u-400 0.7145 [0.7061, 0.7239], A3u-800 0.7114, A10-e4 0.6727 [0.6641, 0.6815]; paired A3−A10 +0.0418 [+0.0379, +0.0463]. Pending: A0, A1, A2, A4, A5, A6, A7 (need hb columns), A8 (needs mirror semantics confirmed), A9 (other heads), learning curve on best arm. Selection: no claim until Tanaka passes 8a29e479…; teacher-specific rule confirmed by D-061 §B. |
| R3–R8 | — (P-7 self-play scoping card numbered by D-061; void if R2 selects trees) |

## Tools (lane)
- `tools/hinata/v0.py`, `archive/v0_2920bb57.py`, `p2_prep.py`, `PROVENANCE-P2.md`, `p2_confirm.py` rev 4 0d0d1b7a (released).
- `tools/hinata/r2_bc.py` rev 4 a31faa5d…; `r2_features_enc_v1.txt` b109e5c0….
- **`tools/hinata/r2_battery.py` 8a29e479aa91…** (arms A0–A7, table + selection; Tanaka 20:19Z fixes). **`tools/hinata/r2_cnn.py` e237fb767a07…** (A10). **`tools/hinata/regime_stump.py` de7d07aa3829…** (P-6 stump; stdlib only).
- Run dirs: `build/hinata/r2/battery/A3-u/` (fit sha 8fdddd38), `A10-u/` (fit sha 5e8d6f46); `build/hinata/p6/stump.json`; earlier `build/hinata/r2/dev120-enc-s5/`, `lc-f*`, `build/hinata/p2/`.

## Open requests
1. **Kageyama (critical path, D-060 §E):** hb_pF/R/L + HB-1 feature vector (prefix `hb_f_`) per dev120 oracle row keyed (game, side, dragon, round, turn); confirm window layout x_f{−3..3}r{−3..3}_{23 ch} and A8 mirror = flip lateral axis + swap _R/_L.
2. **Tanaka:** pass line on r2_battery 8a29e479… / r2_cnn e237fb76….
3. **Chair:** registry rows hinata-v0b (FAIL), hinata-p1-enc-dev (REG-004?), lc-f10/25/50, hinata-r2-bat-A3u (8807488c…), hinata-r2-bat-A10 (3e23db4a…).

## Human-in-the-loop
- The Cowork VM `/sessions` disk is full (Chair asked the lead 20:45Z). Not blocking Hinata (cloud does the fits), blocking Kageyama's bridge → indirectly the battery's critical path.

## Next 3 actions
1. When hb columns land: stage them, run `r2_battery.py a0`, then A4, A5, A1 (pooled, 400/800), then A2, A6, A7; `table` only after Tanaka's pass line; learning curve on the best pooled arm.
2. A8 once the mirror semantics are confirmed (new arm run, same tool family; augmentation on training folds only).
3. If idle: A9 scoping (split/cull/sprint heads on the same rows; labels y_kind ≠ 0) and a Φ-legal note for P-6 (what one process can estimate of Φ's six inputs).
