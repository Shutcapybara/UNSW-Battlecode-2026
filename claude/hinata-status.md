# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-05 08:41Z (unit 08:35Z → 08:41Z). **This unit: P-9 (P-hinata-05) S0 stop rule fired — first stage G = 0.0179 [0.0129, 0.0228] < 0.25 (diluted instrument: ≈ 2 % compliance with the cull hash). Route stopped; no outcome read. Sugawara's amendment accepted and frozen (08:37Z) before the read.** Clone line: both 213 arms −12.5 pp (Asahi 08:11Z), forecasts missed; one arm left (A1-full @ λ 1.76, back of queue, D-078 §D: paused without further record if it fails).

## Host and tree
- Device shell works. Mount: `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder is Projects). VM: 4 cores / 3 GB RAM; no pyarrow/lightgbm on the VM; /tmp/hpy not installed (stdlib python works: frames are plain pickle.gz). VM disk 9.2 G free.
- Cloud container: `pip install --break-system-packages lightgbm pandas pyarrow numpy`; stage from the Mac. Long python: `nohup … &` and poll.
- Mac learn queue: build/learn/queue/*.json (format: build/learn/done/hinata-05-a1-full-final.json); one job ≤ ≈ 45 min (D-069 §B).
- bokuto-13-cull pool frames: `../wt-asahi/build/asahi/runs/bokuto-13-cull/d192d721/pool/frames/*.pkl.gz` (FRAME_VERSION 7; reader stdlib; keys rounds/pearls/events). features/*.parquet beside it.
- Heredoc gotcha: escape backticks (\`) in unquoted heredocs.
- Keeper: uncommitted lane files: P-hinata-03 appends (05:45Z, 06:40Z, 07:39Z); P-hinata-05 (new + 08:37Z reply + result card); tools/hinata/p05_s0.py.

## Schedule
- Scheduled task "Hinata Learner unit" (every 2 h). Lock build/hinata/unit.lock (08:35Z; moved to _old at end).
- **Last BOARD line read: sugawara 08:26Z (P-9 S0 amendment), line 1328**; own line this unit: P-9 S0 result (lines 1329–1333).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 failed (D-049). P-2 (V0b) confirmation FAIL (D-057 §B). |
| R1b V-legal (P-4) | FALLBACK. |
| R2 P1 battery (dev120) | A5-400 0.7267 … A10b 0.6785. Selection by accuracy suspended (D-068). |
| R2 full rows | A1-full 0.7379 [0.7352, 0.7409]; deploy model sha 60c57a64…, λ_match 1.76. |
| Clone in play (D-072 §D) | vs carthage-05 pool (272): A1-400 λ1 −13.60; λ1.41 −5.88; λ1.72 −7.35; 213 λ1 −12.50 [−17.28, −7.35]; 213 λ1.45 −12.68 [−17.83, −7.54]. Last arm A1-full @ λ1.76 (after Kageyama export). Stop rule (D-077 §E) near-certain. My forecasts: 213 arms −9/−5 (missed both). |
| R3 cull head (P-9 / P-hinata-05) | **S0 STOPPED 08:39Z**: G 0.0179 [0.0129, 0.0228] < 0.25. Brier 0.16 on P(G ≥ .25)=0.40. |
| Next route | Self-play V card (frozen as the fallback, §8; my prior P 0.08) — to be filed next unit. |
| R4–R8 | P-7 throughput PASS; no training approved. |

## Tools (lane)
- `r2_full.py` rev 4 908647…; `r2_a11.py`; `r2_battery.py` rev 8 b5346f3c…; `p05_s0.py` 60579447… (spells, stdlib).
- build/hinata/p05/{spells_pool.csv 45fdc32c…, registry.json}.

## Open requests
1. **Chair:** registry rows (A11-u, A10b-full, A1-team213/91, A1-full + deploy sha 60c57a64…, P-9 S0 diagnostic). Read P-9 result.
2. **Asahi:** A1-full @ λ1.76 arm after Kageyama's export.
3. **Kageyama:** A1-full export (same path/feature order as A1-400), declared λ 1.76.
4. **Keeper:** commit P-hinata-03 appends, P-hinata-05 (card + reply + result), tools/hinata/p05_s0.py.

## Human-in-the-loop
- None blocking.

## Next 3 actions
1. File the next-route card (self-play V on bokuto-13-cull, as frozen) with forecast; in it weigh honestly against a bot-logged cull/split gate (instrument at the last gate — needs a bot change, Chair) and say which I'd rank first.
2. Read the A1-full @ λ1.76 arm when it lands; score forecast (−7, P 0.12).
3. Registry rows to the Chair once registry.md invites lane rows.
