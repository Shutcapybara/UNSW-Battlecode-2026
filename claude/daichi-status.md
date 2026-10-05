# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 27, 2026-10-05 12:51–13:00Z)

- **Last BOARD line read:** 1400 (Asahi 12:42Z D-082 §C economy table). My line 1401 (17388 confirmed; windows). Next unit reads from 1402.
- **LIVE = 17388 (`kenma-03-pocket-queen`)**, confirmed status.json active 17388 (as_of 12:41Z); restored 12:34:13Z; first ranked series after reactivation 12:36Z.
- **restore.json field order (actuator.restore_check): `previous` = the id to ACTIVATE, `candidate` = the id active NOW.**
- D-052 §B watch on 17388: rollback target 14585; trial window (60 g, 05:02–07:13Z) counts as its first 60. Roll back on mean diff < −0.08 with bootstrap 95th pct < 0, or crash/DQ.
- Numbers at 12:51Z (ranked, post-m2, series bootstrap 1000×seed 7): 17388 since 12:34Z −0.056 [−0.262, +0.136] (20/4); 17388 07:14–12:34Z −0.078 [−0.276, +0.121] (20/4); all 17388 100 g −0.007 [−0.106, +0.083]. 17530 second window (games 61–120) −0.045 [−0.166, +0.065] (60/12). Elo 1769 rank 76.
- Ad-hoc window script: build/daichi/tmp/win27.py (imports live_monitor).
- No new D-records after D-082. Asahi-27-b13-reserve h2h vs kenma-03 0.676 [0.608, 0.745] (102 g, local) — no upload without a Chair D-record.
- Battles dispatch enabled (D-055), no jobs. No API/quota errors in *.done.json.

## Next unit

1. Read BOARD from 1402. live_monitor; 17388 games since 12:34Z (win27.py) and D-052 §B look once n ≥ 40 new.
2. Trial candidates: asahi-27-b13-reserve / bokuto-18 — act only on a Chair D-record (upload activate:false, outside blackout).
3. If a unit lands in a blackout, schedule a send_later continuation for blackout end + 2 min.

## Open questions for the Chair

- None open (end rule applied).

## Units

- 2026-10-05 12:51Z unit 27 — read BOARD 1377–1400; 17388 confirmed active; windows posted (BOARD 1401). No actions.
- 2026-10-05 11:51–12:40Z unit 26 — read BOARD 1359–1374 (D-081 end rule → 17388; D-082). Unit hit the 11:52–12:12Z blackout; continuation at 12:33Z wrote restore.json (previous 17388, candidate 17530); restored 12:34:13Z. BOARD + user notified.
- 2026-10-05 ~10:55Z unit 25 — read BOARD 1348–1357 (D-080: screen not dispatched; Chair applies end rule). Trial-2 look table posted (1358): 17530 −0.041 vs 17388 +0.074.
- 2026-10-05 ~10:00Z unit 24 — read BOARD 1335–1346 (Kenma retired; 2nd BOARD overwrite, my 1334 survived; D-079). Trial-2 at 45 −0.087; D-079 screen drafted and sized; BOARD 1347.
- 2026-10-05 ~08:51Z unit 23 — Trial-2 interim 25 games −0.193 @1725; BOARD 1334.
- 2026-10-05 ~08:15Z unit 22 — Trial-1 look posted (1318). bokuto-13-cull uploaded as 17530 and live from 08:15:41Z; user notified.
- Earlier units: see git history of this file on r/daichi.

## Known environment issues

- The mount is now at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (connected folder = Projects).
- The Cowork VM home disk (/sessions) is full (0 free at 20:50Z). Build the test overlay in `/tmp/daichi-test` (tools/hub,
  tools/*.py, tests/test_hub_*.py + lane overrides, ~2 MB), run `python3 -m unittest` (no pytest), then `rm -rf` it.
  The full hub suite hits "disk full" in one executor test and an import mismatch in test_hub_analysis_a1 (env, not code).
- The mount refuses symlinks (a tar extract left an unreadable entry; moved to build/daichi/tmp/_old/). Materialise
  bots with `git show` per file. No unswbc in the VM (python < 3.11): CPU probes run in the cloud container
  (pip install unswbc==1.2.9; stage the bot, opponent and maps).
- The VM cannot delete files in the mount and cannot push. commit.sh may exit 2 after a successful commit; check
  `git rev-parse r/daichi`.
