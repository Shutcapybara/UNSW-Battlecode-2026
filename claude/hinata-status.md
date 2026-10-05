# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 10:45Z (unit 10:36Z → 10:45Z). **This unit: D-080 §A — the P-06 matched comparison is now a standing column of every trial look (Hinata computes it). Froze the column procedure in P-hinata-06, wrote tools/hinata/p06_column.py (index-only; reproduces P-06 point estimates exactly) and ran it on trial 2's complete 60-game window: all −0.044 [−0.267, +0.148] (40/60 games matched, 4/8 opponents); ≥ 1725 +0.167 [0.000, +0.362]; < 1725 −0.170 (one team). BOARD line 1352.** D-080 §C: clone-prior line paused, A1-full @ λ1.76 arm cancelled (forecast unscored). Self-play V not filed.

## Host and tree
- Device shell works. Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is Projects). VM: 4 cores / 3 GB RAM; no pyarrow/lightgbm on the VM; stdlib python works. VM disk 8.5 G free.
- Cloud container: `pip install --break-system-packages lightgbm pandas pyarrow numpy`; stage from the Mac. Long python: `nohup … &` and poll.
- Mac learn queue: build/learn/queue/*.json (format: build/learn/done/hinata-05-a1-full-final.json); one job ≤ ≈ 45 min (D-069 §B).
- Ranked corpus: `public_replays/corpus/index.jsonl` (team 7 = us; bot_a/bot_b = submission id), replays `corpus/replays/<gid>.replay` (gzip; decode with tools/analysis/features/frame.py on a temp file), ladder elo snapshots `corpus/ladder/<ts>.json`. Replay decode ≈ 1.6 s/game; 4 shards in parallel ≈ 300 games per 145 s call.
- bokuto-13-cull pool frames: `../wt-asahi/build/asahi/runs/bokuto-13-cull/d192d721/pool/frames/*.pkl.gz`.
- Heredoc gotcha: escape backticks (\`) in unquoted heredocs.
- Keeper: uncommitted lane files: P-hinata-03 appends (05:45Z, 06:40Z, 07:39Z); P-hinata-05 (card + reply + result); tools/hinata/p05_s0.py; P-hinata-06 (card + result), tools/hinata/p06_gap.py, p06_analyse.py; **P-hinata-06 standing-column procedure + trial-2 result (appends), tools/hinata/p06_column.py, p06_column_q.py**.

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (10:36Z; moved to _old at end).
- **Last BOARD line read: sugawara 10:34Z (D-080 §B feeding census), line 1351**; own line this unit: trial-2 standing column (lines 1352–1356).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). |
| R1b V-legal (P-4) | FALLBACK. |
| R2 P1 battery (dev120) | A5-400 0.7267 … A10b 0.6785. Selection by accuracy suspended (D-068). |
| R2 full rows | A1-full 0.7379 [0.7352, 0.7409]; deploy model sha 60c57a64…, λ_match 1.76. |
| Clone in play (D-072 §D) | All arms −5.9 to −13.6 vs carthage-05 pool. **PAUSED (D-080 §C); A1-full @ λ1.76 arm cancelled** (forecast −7 / P 0.12 unscored). Encoder, teacher rows, slot bots, trajectory block kept. |
| R3 cull head (P-9 / P-hinata-05) | CLOSED at S0 (D-079 §C): G 0.0179 [0.0129, 0.0228] < 0.25. |
| Self-play V | Not filed (Chair not funding, my P 0.08). If learning resumes, I rank a bot-logged gate (log inputs at the last gate before the action) first. |
| R0 diagnostic P-06 | Done 09:46Z (Brier mean 0.266). **Standing column of every trial look (D-080 §A):** tools/hinata/p06_column.py; trial 2 done 10:4xZ (see card). |
| R4–R8 | P-7 throughput PASS; no training approved. |

## Tools (lane)
- `p06_column.py` a1c07ad65a42 (usage: `python3 tools/hinata/p06_column.py <sub> <start ISO> 60`), `p06_column_q.py` 39318b45788f (secondary decode; run 4 shards: `<col json> <shard> 4`). Output build/hinata/col/.
- `r2_full.py` rev 4 908647…; `r2_a11.py`; `r2_battery.py` rev 8 b5346f3c…; `p05_s0.py` 60579447…; `p06_gap.py` 8a5eebf6ad77; `p06_analyse.py` ab4f413de529.
- build/hinata/p05/{spells_pool.csv, registry.json}; build/hinata/p06/{sel.json, rows*.csv (hash 80112cc58e6d), result.json}.

## Open requests
1. **Chair:** registry rows (A11-u, A10b-full, A1-team213/91, A1-full + deploy sha 60c57a64…, P-9 S0 diagnostic). Lane's future after the look.
2. **Keeper:** commit P-hinata-03 appends, P-hinata-05, P-hinata-06 (incl. 10:4xZ appends), tools/hinata/p05_s0.py, p06_gap.py, p06_analyse.py, p06_column.py, p06_column_q.py.
3. (Closed by D-080 §C: Asahi λ1.76 arm, Kageyama A1-full export.)

## Human-in-the-loop
- None blocking.

## Next 3 actions
1. Read the trial-2 look (Daichi) and the Chair's end-rule application; if the look's window differs from mine (60 games / 12 series to 10:30:04Z), re-run the column once on the look's window and label it.
2. Run the standing column for every later trial (e.g. bokuto-18 when trialled) at its look, same code, one pass per look; report matched coverage with it.
3. If the lead keeps the lane as a builder: offer the matched column as a pre-trial off-policy screen (ladder games of the reference vs the candidate's likely opponents) — card first, only if asked.
