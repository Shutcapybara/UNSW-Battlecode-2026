# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 17:40Z (unit 17:35Z → 17:40Z). **This unit: 17791 look not due (50 ranked games since 14:19Z at 17:36Z; boundary ≥ 60 ≈ 18:20–18:45Z). Trial-4 forecast (asahi-27-b13-reserve) pre-registered in P-hinata-07 § "Forecast for trial 4" (6 items vs 17530 reference rows), BOARD line 1451. No new D-08x since D-086; Sugawara replicated D-086 §D points (ntle sum 2,836 not 2,749 — accept; reading unchanged). Bokuto 17:33Z: ally-collision excess attributed to the atlas (bokuto-41-atlas0).** Previous unit (16:55Z): D-086 §D points limit 100 M from own replays; seat column; look timing correction.

## Host and tree
- Device shell works. Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is Projects). VM: 4 cores / 3 GB RAM; no pyarrow/lightgbm on the VM; stdlib python works. VM disk 8.5 G free. VM clock may lag others' BOARD stamps by a few minutes; use `date -u` anyway.
- Cloud container: `pip install --break-system-packages lightgbm pandas pyarrow numpy`; stage from the Mac. Long python: `nohup … &` and poll.
- Mac learn queue: build/learn/queue/*.json (format: build/learn/done/hinata-05-a1-full-final.json); one job ≤ ≈ 45 min (D-069 §B).
- Ranked corpus: `public_replays/corpus/index.jsonl` (team 7 = us; bot_a/bot_b = submission id), replays `corpus/replays/<gid>.replay` (gzip; decode with tools/analysis/features/frame.py on a temp file), ladder elo snapshots `corpus/ladder/<ts>.json`. Replay decode ≈ 1.6 s/game; 4 shards in parallel ≈ 300 games per 145 s call.
- curves2 row format: g_s*.jsonl, per game `cA`/`cB`[round] = [units, total, longest, queen_alive, queen_body], plus 'end'; `us`, `winner`, `reason`, `last_round`, `elo_a/b`, `pop`, `series`.
- bokuto-13-cull pool frames: `../wt-asahi/build/asahi/runs/bokuto-13-cull/d192d721/pool/frames/*.pkl.gz`.
- Heredoc gotcha: escape backticks (\`) in unquoted heredocs.
- Keeper: uncommitted lane files: P-hinata-03 appends (05:45Z, 06:40Z, 07:39Z); P-hinata-05 (card + reply + result); tools/hinata/p05_s0.py; P-hinata-06 (card + result), tools/hinata/p06_gap.py, p06_analyse.py; P-hinata-06 standing-column procedure + trial-2 result (appends), tools/hinata/p06_column.py, p06_column_q.py; P-hinata-07 (card + result + correction procedure + corrected result + ≥ 1725 re-read + 14:36Z reply to Sugawara + 15:40Z look procedure + **17:36Z trial-4 forecast**), **tools/hinata/look.py**, tools/hinata/curves.py (fixed), curves_table.py (dir arg), curves_owner.py, curves_qid.py, curves_fix.py, qband.py (d7b802d93152). **tools/hinata/pts_own.py** (e47a35b08f39), tools/hinata/pts.py (superseded probe, other-team CPU absent). (carried.py lives in build/hinata/qband2/; promote to tools/hinata/ if reused at the look.)

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (moved to _old at end).
- **Last BOARD line read: line 1450 (bokuto 17:33Z atlas ally-collision); own line 1451.** Lock 17:35Z (moved to _old).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). |
| R1b V-legal (P-4) | FALLBACK. |
| R2 P1 battery (dev120) | A5-400 0.7267 … A10b 0.6785. Selection by accuracy suspended (D-068). |
| R2 full rows | A1-full 0.7379 [0.7352, 0.7409]; deploy model sha 60c57a64…, λ_match 1.76. |
| Clone in play (D-072 §D) | All arms −5.9 to −13.6 vs carthage-05 pool. **PAUSED (D-080 §C).** Encoder, teacher rows, slot bots, trajectory block kept. |
| R3 cull head (P-9 / P-hinata-05) | CLOSED at S0 (D-079 §C). |
| Self-play V | Not filed (Chair not funding, my P 0.08). |
| R0 diagnostic P-06 | Done. **Standing column of every trial look (D-080 §A):** tools/hinata/p06_column.py. |
| R0 curve table P-07 (D-081 §D) | Use build/hinata/curves2/ (rows 8e7ecc6d6735). ≥ 1725 reading amended, recorded D-085 §A. Look block: tools/hinata/look.py. |
| R4–R8 | P-7 throughput PASS; no training approved. |
| Deploy constraint (D-086 §D) | Server cut at 100,000,000 points a dragon-turn on 25–29 Sep (our replays); brief still says 30 M until the Chair posts otherwise. |

## Tools (lane)
- `look.py` 6a691c0f6bbc: `python3 tools/hinata/look.py decode SUB START 60 140 SHARD 4 build/hinata/lookN` (run shard 0 alone first: it writes sel.json; then 1–3 in parallel) → `python3 tools/hinata/look.py block build/hinata/lookN`. Reference: `look.py block build/hinata/curves2 17530`.
- `p06_column.py` a1c07ad65a42 (usage: `python3 tools/hinata/p06_column.py <sub> <start ISO> 60`), `p06_column_q.py` 39318b45788f (4 shards). Output build/hinata/col/.
- `pts_own.py` e47a35b08f39: `scan BUDGET SHARD NSHARD build/hinata/pts_own` / `report build/hinata/pts_own`.
- `qband.py` d7b802d93152 (reached-r300 view); `build/hinata/qband2/carried.py` 31f0c2c6a397 (carried view, 17530 hard-coded — parametrise pop for the look).
- `r2_full.py` rev 4 908647…; `r2_a11.py`; `r2_battery.py` rev 8 b5346f3c…; `p05_s0.py` 60579447…; `p06_gap.py` 8a5eebf6ad77; `p06_analyse.py` ab4f413de529.

## Open requests
1. **Chair:** registry rows (A11-u, A10b-full, A1-team213/91, A1-full + deploy sha 60c57a64…, P-9 S0 diagnostic). docs/learning/registry.md exists — check whether it invites lane rows.
2. **Keeper:** commit the lane files listed under Host and tree.
3. **Chair (D-086 §D):** rule the points limit using BOARD 1441 + Asahi's burn test.

## Human-in-the-loop
- None blocking.

## Next 3 actions
1. Trial-3 look for 17791 (boundary ≈ 18:20–18:45Z): check `python3 -c "import sys;sys.path.insert(0,'tools/hinata');from look import select;s,c=select('17791','2026-10-05T14:19:00Z',60);print(len(s),c)"`; only when complete=True: `look.py decode 17791 2026-10-05T14:19:00Z 60 140 0 4 build/hinata/look3` (shard 0 alone; existing g_s*.jsonl reused), shards 1–3 in parallel, then `block`; `p06_column.py 17791 2026-10-05T14:19:00Z 60`; seat × result column. Post block (reached + carried, by band, vs 17530 row and top-ten 78.5/153.7 winner, 61.3/110.9 loser) to Sugawara/Chair/Daichi; append result to P-hinata-07. Notify user (trial look result).
2. Trial 4: get asahi-27's submission id and activation time from Daichi's BOARD line; its look follows the same procedure; score the 17:36Z forecast (Brier) at that look.
3. If the Chair rules D-086 §D (points limit), offer (card first) the inference-budget implication for R2/R4 deploy; otherwise answer any review on P-hinata-07.
