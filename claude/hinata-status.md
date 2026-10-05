# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 18:42Z (unit 18:35Z → 18:42Z). **This unit: trial-3 (17791) curve block read with the frozen procedure (60/12, same window as Daichi 18:25Z) → P-hinata-07 § "Trial-3 look result", BOARD line 1472. ≥ 1725 carried r300 +6.6 [−14.2, +29.3] (17530 +0.8); queen alive r300 0.62 (0.42); all diff intervals include 0 → no curve evidence either way. D-087 §A server compute for 17791: max 12.62 M, 0 cuts. D-087 recorded: limit 100 M, working ceiling probe ≤ 60 M; Hinata reports trial bot's server max turn + cuts at each look (a cut ends the trial); no seat term. Trial 4 = 17940 (asahi-27-b13-reserve), activated 18:25:06Z, look ≈ 22:15Z.** No user notification (no gate of mine, no contradiction).

## Host and tree
- Device shell works. Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is Projects). VM: 4 cores / 3 GB RAM; no pyarrow/lightgbm on the VM; stdlib python works. VM disk 8.2 G free. Use `date -u`.
- Cloud container: `pip install --break-system-packages lightgbm pandas pyarrow numpy`; stage from the Mac.
- Mac learn queue: build/learn/queue/*.json (format: build/learn/done/hinata-05-a1-full-final.json); one job ≤ ≈ 45 min (D-069 §B).
- Ranked corpus: `public_replays/corpus/index.jsonl` (team 7 = us; bot_a/bot_b = submission id), replays `corpus/replays/<gid>.replay` (gzip), ladder snapshots `corpus/ladder/<ts>.json`. Decode ≈ 1.6 s/game; 4 shards ≈ 300 games / 145 s.
- `tail -1`/`tail -2` fail on the VM ("option used in invalid context") — use `tail -n 2`, `tail -c` or python.
- Heredoc gotcha: escape backticks in unquoted heredocs.
- Keeper: uncommitted lane files: P-hinata-03 appends; P-hinata-05; tools/hinata/p05_s0.py; P-hinata-06 + appends, p06_gap.py, p06_analyse.py, p06_column.py, p06_column_q.py; P-hinata-07 (card + all appends incl. 17:36Z trial-4 forecast and **18:40Z trial-3 look result**), tools/hinata/look.py, curves.py, curves_table.py, curves_owner.py, curves_qid.py, curves_fix.py, qband.py, pts_own.py, pts.py (superseded).

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (moved to _old at end).
- **Last BOARD line read: line 1471 (bokuto 18:32Z budget twins); own line 1472.**

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). |
| R1b V-legal (P-4) | FALLBACK. |
| R2 P1 battery (dev120) | A5-400 0.7267 … A10b 0.6785. Selection by accuracy suspended (D-068). |
| R2 full rows | A1-full 0.7379 [0.7352, 0.7409]; deploy model sha 60c57a64…, λ_match 1.76. |
| Clone in play (D-072 §D) | All arms −5.9 to −13.6 vs carthage-05 pool. **PAUSED (D-080 §C).** |
| R3 cull head (P-hinata-05) | CLOSED at S0 (D-079 §C). |
| Self-play V | Not filed. |
| R0 diagnostic P-06 | Done; standing column tools/hinata/p06_column.py. |
| R0 curve table P-07 | Trial-3 look done (18:40Z). Trial-4 forecast filed 17:36Z (score at its look, Brier). |
| R4–R8 | P-7 throughput PASS; no training approved. D-087 §E: 100 M budget fits an ~8 M MAC student. |

## Tools (lane)
- `look.py` 6a691c0f6bbc: `python3 tools/hinata/look.py decode SUB START 60 140 SHARD 4 build/hinata/lookN` (shard 0 alone first: writes sel.json; then 1–3 in parallel) → `look.py block build/hinata/lookN`. Reference: `look.py block build/hinata/curves2 17530`.
- `p06_column.py` (`python3 tools/hinata/p06_column.py <sub> <start ISO> 60` → json; save to build/hinata/col/col-<sub>-lookN.txt).
- `pts_own.py`: `scan 130 K 4 build/hinata/pts_own` (4 shards parallel, resumable, newest first), then filter by the look's sel.json gids for max / max01 / n30 / ntle (D-087 §A item 4).
- Seat × result and end reason × band: inline python over sel.json + g_s*.jsonl (fields us, winner, reason, map).

## Open requests
1. **Keeper:** commit the lane files listed under Host and tree.
2. Chair: registry carries REG-003/004 …; check whether A1-full / deploy sha rows exist before re-asking.

## Human-in-the-loop
- None blocking.

## Next 3 actions
1. Trial-4 look (17940, start 2026-10-05T18:25:06Z; boundary ≈ 22:15Z; blackouts 19:52–20:12, 21:52–22:12Z): check `select('17940','2026-10-05T18:25:06Z',60)` complete=True; then `look.py decode 17940 2026-10-05T18:25:06Z 60 140 0 4 build/hinata/look4` (+ shards 1–3), `block`; p06_column; pts_own scan + server max/cuts (a cut ends the trial, D-087 §A); seat/end-reason columns. Score the 17:36Z forecast items 1–6 (Brier) vs 17530 rows; item 3 also vs 17791's 32.4 (joint reading). Append to P-hinata-07, BOARD line, notify user (trial look + forecast score).
2. Answer any review on the P-hinata-07 trial-3 result.
3. If funded, card first: value feature queen-alive r300 (RL translation of the trial-3 reading) — VM-sized, training maps only.
