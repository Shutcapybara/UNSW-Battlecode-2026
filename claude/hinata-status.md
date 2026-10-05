# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 22:47Z (unit 21:35Z + self follow-up 22:41Z). **This unit: trial-4 look (17940) done, frozen procedure, one read: ≥ 1725 reached r300 per-game growth 46.4 [34.0, 59.2] (39/10) vs 17791 38.2 — diffs include 0; queen alive r300 0.33 (17791 0.72), queen losses 14/50; W 19/50; server max 12.94 M; forecast Brier 0.209/7 (coin 0.25), missed item 4 (queen). Appended to P-hinata-07; BOARD line 1511; user notified.** Read BOARD 1499–1510 (D-089, D-090: trial 5 = bokuto-61-mouth; Chair asks Hinata+Daichi to watch at trial 5's look: Australia + Slithery results and queen deaths, queen alive r300, QoS/Trophy/Default/Stripes, Schooltime; Sugawara 22:27Z: test at the look the share of 61's queen wall deaths with a paired-portal edge next to the head in the prior 1–3 turns and landing out of sight, his P(≥ 5 of 10 qk2) 0.55).

## Host and tree
- Device shell works. Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is Projects). VM: 4 cores / 3 GB RAM; no pyarrow/lightgbm on the VM; stdlib python works. VM disk 8.2 G free. Use `date -u`.
- Cloud container: `pip install --break-system-packages lightgbm pandas pyarrow numpy`; stage from the Mac.
- Mac learn queue: build/learn/queue/*.json (format: build/learn/done/hinata-05-a1-full-final.json); one job ≤ ≈ 45 min (D-069 §B).
- Ranked corpus: `public_replays/corpus/index.jsonl` (team 7 = us; bot_a/bot_b = submission id), replays `corpus/replays/<gid>.replay` (gzip), ladder snapshots `corpus/ladder/<ts>.json`. Decode ≈ 1.6 s/game; 4 shards ≈ 300 games / 145 s.
- `tail -1`/`tail -2` fail on the VM ("option used in invalid context") — use `tail -n 2`, `tail -c` or python.
- Heredoc gotcha: escape backticks in unquoted heredocs.
- Keeper: uncommitted lane files: P-hinata-03 appends; P-hinata-05; tools/hinata/p05_s0.py; P-hinata-06 + appends, p06_gap.py, p06_analyse.py, p06_column.py, p06_column_q.py; P-hinata-07 (card + all appends incl. 17:36Z trial-4 forecast and **18:40Z trial-3 look result**, **19:40Z reply to Sugawara's check**, **20:40Z growth pre-registration + result**), tools/hinata/look.py, growth_pg.py (new 20:40Z), **P-hinata-07 22:45Z trial-4 look append**, curves.py, curves_table.py, curves_owner.py, curves_qid.py, curves_fix.py, qband.py, pts_own.py, pts.py (superseded).

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (moved to _old at end).
- **Last BOARD line read: line 1510 (sugawara 22:27Z 61 diff read); own line 1511.**

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
| R0 curve table P-07 | Trial-3 look done (18:40Z), checked by Sugawara (amend labels, accepted 19:40Z). Trial-4 look done 22:45Z (Brier 0.209/7). Quote conversion/queen in the reached view from now on. Per-game growth check PASS (20:40Z): gap to top-ten winners −29.9; outcome-unconditioned ≈ −13. |
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
1. Trial-5 look (bokuto-61-mouth; sub id and activation time from Daichi's BOARD line after the trial-4 end-rule table): file a frozen look card + forecast (items incl. queen alive r300, Australia/Slithery queen deaths, the four maps, Schooltime) BEFORE the 61 window is read; then same procedure as look4 (decode → block, p06_column, pts_own, seat/end reason, growth_pg row, watch-map W/n). Add Sugawara's test (22:27Z): queen deaths (end reason queen, our queen) with a paired portal adjacent to her head in the prior 1–3 turns — needs a portal-adjacency scan in tools/hinata (new script, pre-register the rule first).
2. Answer any review on P-hinata-07 (trial-4 result).
3. If funded, card first: V features queen-alive r300 + per-game growth r100→300 fitted on all outcomes, training maps only; 17940 vs 17791 as the paired queen-term set.
