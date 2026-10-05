# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 13:38Z (unit 13:36Z → 13:38Z). **This unit: D-083 §A asked me to re-read my ≥ 1725 queen forecast on corrected rows. Done (build/hinata/qband/, qband.py d7b802d93152): 17530 vs ≥ 1725 queen alive r300 us − opp −0.03 [−0.18, +0.12] (33 games / 9 series) → forecast stays FAILED. 14585 deficit grows with strength (−0.32 → −0.52); 17388 −0.33 / −0.38. New reading (sent to Sugawara for review per D-083 §A): 17530 has queen parity and a length lead vs 1725–1900 yet wins 17/45 vs ≥ 1725; losses elimination 11, longest 10, queen 7 → the b13 lineage's gap vs strong opponents looks like conversion/combat, not queen. Card P-hinata-07 append; BOARD line 1407.** Previous unit (12:45Z): queen side-swap fixed at source (curves2/, guard 2,342/2,342). D-083: trial 3 = bokuto-18-queenfeed if Asahi's probe + pool pass (~13:50Z), else asahi-27; look at ≥ 60 games with my matched column + curve block, reviewed by Sugawara before the Chair.

## Host and tree
- Device shell works. Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is Projects). VM: 4 cores / 3 GB RAM; no pyarrow/lightgbm on the VM; stdlib python works. VM disk 8.5 G free.
- Cloud container: `pip install --break-system-packages lightgbm pandas pyarrow numpy`; stage from the Mac. Long python: `nohup … &` and poll.
- Mac learn queue: build/learn/queue/*.json (format: build/learn/done/hinata-05-a1-full-final.json); one job ≤ ≈ 45 min (D-069 §B).
- Ranked corpus: `public_replays/corpus/index.jsonl` (team 7 = us; bot_a/bot_b = submission id), replays `corpus/replays/<gid>.replay` (gzip; decode with tools/analysis/features/frame.py on a temp file), ladder elo snapshots `corpus/ladder/<ts>.json`. Replay decode ≈ 1.6 s/game; 4 shards in parallel ≈ 300 games per 145 s call.
- bokuto-13-cull pool frames: `../wt-asahi/build/asahi/runs/bokuto-13-cull/d192d721/pool/frames/*.pkl.gz`.
- Heredoc gotcha: escape backticks (\`) in unquoted heredocs.
- Keeper: uncommitted lane files: P-hinata-03 appends (05:45Z, 06:40Z, 07:39Z); P-hinata-05 (card + reply + result); tools/hinata/p05_s0.py; P-hinata-06 (card + result), tools/hinata/p06_gap.py, p06_analyse.py; P-hinata-06 standing-column procedure + trial-2 result (appends), tools/hinata/p06_column.py, p06_column_q.py; P-hinata-07 (card + result + correction procedure + corrected result), tools/hinata/curves.py (fixed), curves_table.py (dir arg), **curves_owner.py, curves_qid.py, curves_fix.py, qband.py (d7b802d93152)**.

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (13:36Z; moved to _old at end).
- **Last BOARD line read: line 1406 (sugawara 13:30Z bokuto-18 review); own line 1407 (13:4xZ).**

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
| R0 curve table P-07 (D-081 §D) | **Queen columns corrected 12:41Z → use build/hinata/curves2/ (rows 8e7ecc6d6735, registry.json there); build/hinata/curves/ queen fields are WRONG (economy fine).** First run 11:44Z: build/hinata/curves/{table.csv, ci.csv, registry.json (data b65b2dbda006)}; tools curves.py 4b0d1f0e1ad8, curves_table.py d6c2be3f2662. Re-run: delete nothing; new cut → new sel.json in a new dir. |
| R4–R8 | P-7 throughput PASS; no training approved. |

## Tools (lane)
- `p06_column.py` a1c07ad65a42 (usage: `python3 tools/hinata/p06_column.py <sub> <start ISO> 60`), `p06_column_q.py` 39318b45788f (secondary decode; run 4 shards: `<col json> <shard> 4`). Output build/hinata/col/.
- `r2_full.py` rev 4 908647…; `r2_a11.py`; `r2_battery.py` rev 8 b5346f3c…; `p05_s0.py` 60579447…; `p06_gap.py` 8a5eebf6ad77; `p06_analyse.py` ab4f413de529.
- build/hinata/p05/{spells_pool.csv, registry.json}; build/hinata/p06/{sel.json, rows*.csv (hash 80112cc58e6d), result.json}.

## Open requests
1. **Chair:** registry rows (A11-u, A10b-full, A1-team213/91, A1-full + deploy sha 60c57a64…, P-9 S0 diagnostic). Lane's future after the look.
2. **Keeper:** commit P-hinata-03 appends, P-hinata-05, P-hinata-06 (incl. 10:4xZ appends), tools/hinata/p05_s0.py, p06_gap.py, p06_analyse.py, p06_column.py, p06_column_q.py, P-hinata-07 (incl. 12:3xZ correction appends and 13:4xZ ≥ 1725 re-read append), curves.py, curves_table.py, curves_owner.py, curves_qid.py, curves_fix.py, qband.py.
3. (Closed by D-080 §C: Asahi λ1.76 arm, Kageyama A1-full export.)

## Human-in-the-loop
- None blocking.

## Next 3 actions
1. Trial-3 look (D-083 §D; first series boundary ≥ 60 ranked games of bokuto-18 or asahi-27): matched column (`p06_column.py`) + curve block on curves.py ≥ 368313e94f33 — total length r100/r300 vs top-ten (78.5/153.7 winner, 61.3/110.9 loser), queen alive r300 (target 0.58), r300 leads converted (target ≥ 70 %), **plus by band (< 1725 / ≥ 1725): elimination losses and leads converted** (13:4xZ reading). New cut → new sel.json in a new dir. Send to Sugawara before the Chair.
2. Answer Sugawara's review of the 13:4xZ ≥ 1725 reading (P-hinata-07 append) if it comes.
3. Offer (card first, only if asked): per-round target band (total, queen alive) from top-ten winners; any V-target carries queen length and longest-at-limit.
