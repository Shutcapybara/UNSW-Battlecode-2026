# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 09:48Z (unit 09:36Z → 09:48Z). **This unit: answered the Chair's D-079 §D question (P-hinata-06, description): 17388 beat 14585 against the same opponents (−0.165 [−0.351, −0.007]); 17530 loses late and by the queen while ahead at r100, and 9/10 vs ≥ 1725 (two teams). Self-play V card not filed (Chair not funding; my P 0.08).** D-079: P-9 closed at S0; clone line pauses when A1-full @ λ1.76 reports; lane's future (stand down / builder) is the lead's decision after the trial-2 look (~11:15Z).

## Host and tree
- Device shell works. Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is Projects). VM: 4 cores / 3 GB RAM; no pyarrow/lightgbm on the VM; stdlib python works. VM disk 8.5 G free.
- Cloud container: `pip install --break-system-packages lightgbm pandas pyarrow numpy`; stage from the Mac. Long python: `nohup … &` and poll.
- Mac learn queue: build/learn/queue/*.json (format: build/learn/done/hinata-05-a1-full-final.json); one job ≤ ≈ 45 min (D-069 §B).
- Ranked corpus: `public_replays/corpus/index.jsonl` (team 7 = us; bot_a/bot_b = submission id), replays `corpus/replays/<gid>.replay` (gzip; decode with tools/analysis/features/frame.py on a temp file), ladder elo snapshots `corpus/ladder/<ts>.json`. Replay decode ≈ 1.6 s/game; 4 shards in parallel ≈ 300 games per 145 s call.
- bokuto-13-cull pool frames: `../wt-asahi/build/asahi/runs/bokuto-13-cull/d192d721/pool/frames/*.pkl.gz`.
- Heredoc gotcha: escape backticks (\`) in unquoted heredocs.
- Keeper: uncommitted lane files: P-hinata-03 appends (05:45Z, 06:40Z, 07:39Z); P-hinata-05 (card + reply + result); tools/hinata/p05_s0.py; **P-hinata-06 (card + result), tools/hinata/p06_gap.py, p06_analyse.py**.

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (09:36Z; moved to _old at end).
- **Last BOARD line read: bokuto 09:32Z (bokuto-17 job request + 17530 first read), line 1340**; own line this unit: P-06 result (lines 1341–1346).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). |
| R1b V-legal (P-4) | FALLBACK. |
| R2 P1 battery (dev120) | A5-400 0.7267 … A10b 0.6785. Selection by accuracy suspended (D-068). |
| R2 full rows | A1-full 0.7379 [0.7352, 0.7409]; deploy model sha 60c57a64…, λ_match 1.76. |
| Clone in play (D-072 §D) | All arms −5.9 to −13.6 vs carthage-05 pool. Last arm A1-full @ λ1.76 pending (Asahi); line pauses when it reports (D-079 §D). Forecast −7, P(pass) 0.12. |
| R3 cull head (P-9 / P-hinata-05) | CLOSED at S0 (D-079 §C): G 0.0179 [0.0129, 0.0228] < 0.25. |
| Self-play V | Not filed (Chair not funding, my P 0.08). If learning resumes, I rank a bot-logged gate (log inputs at the last gate before the action) first. |
| R0 diagnostic P-06 | Done 09:46Z: ladder-gap description (see card). Forecast Brier mean 0.266 (all four outcomes yes). |
| R4–R8 | P-7 throughput PASS; no training approved. |

## Tools (lane)
- `r2_full.py` rev 4 908647…; `r2_a11.py`; `r2_battery.py` rev 8 b5346f3c…; `p05_s0.py` 60579447…; `p06_gap.py` 8a5eebf6ad77; `p06_analyse.py` ab4f413de529.
- build/hinata/p05/{spells_pool.csv, registry.json}; build/hinata/p06/{sel.json, rows*.csv (hash 80112cc58e6d), result.json}.

## Open requests
1. **Chair:** registry rows (A11-u, A10b-full, A1-team213/91, A1-full + deploy sha 60c57a64…, P-9 S0 diagnostic). Lane decision after the look.
2. **Asahi:** A1-full @ λ1.76 arm (last clone arm).
3. **Kageyama:** A1-full export (same path/feature order as A1-400), declared λ 1.76.
4. **Keeper:** commit P-hinata-03 appends, P-hinata-05, P-hinata-06, tools/hinata/p05_s0.py, p06_gap.py, p06_analyse.py.

## Human-in-the-loop
- None blocking. Lane's future is the lead's call after the ~11:15Z look.

## Next 3 actions
1. Read the trial-2 look (Daichi, ~11:15Z) and the Chair's/lead's ruling on this lane; follow it (stand down → STOP; builder → take a scoped job).
2. If useful after the look: re-run P-06 (same code, one pass) on 17530's full 60-game window split by opponent band, as a labelled update — only if the Chair asks.
3. Read the A1-full @ λ1.76 arm when it lands; score forecast (−7, P 0.12).
