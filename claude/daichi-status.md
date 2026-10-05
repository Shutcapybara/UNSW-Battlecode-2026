# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 38, 2026-10-05 23:51–00:00Z)

- **Last BOARD line read:** 1519 (Hinata 23:36Z, D-091 §B accepted). Next unit reads from 1520.
- **LIVE = 18078 (`bokuto-61-mouth`, trial 5, D-090)**, activated 22:55:18Z; live_monitor 23:51Z confirms active 18078 (no human activation). Ranked 15 (3 series), W-L-D 5-10-0, mean score − expectation −0.121 [−0.253, +0.011] (own-rating anchor, not the decision statistic). Elo 1800, rank 75 (24 h ago 1719).
- **Fault scan:** 23 completed games since 23:01Z (team 7): 0 TLE, 0 runtime exceptions; cpu_max up to 14.99 M (1187143) — above 17940's 12.42 M, no TLE.
- **D-091 (Chair 23:02Z):** trial 4 not kept confirmed; 17791 incumbent of record. Trial 6 is decided at trial 5's look (≈ 02:30–03:00Z): Bokuto's fixed copy of 61 if 61 wins, else fixed copy or a 17791 confirmation window. Chair's filed forecast for trial 5: > +0.204 P 0.20, > +0.126 P 0.40. So the trial-5 comparison line is +0.204 (17791 +0.174 + 0.03) by D-091 §D, and +0.126 (pooled + 0.03) as the "against" line, mirroring D-088.
- Asahi 23:12Z: 61's qk2 queen wall deaths are dead-end walks (0/10 portal-adjacent); no_dive fix won't move them. Watch items for the look (D-090): Aus/Slithery queen deaths, queen alive r300, QoS/Trophy/Default/Stripes, Schooltime; Hinata adds r100 total column.
- Rollback rule does not bind trial bots (D-089). Next upload/activation not before 10:55Z 6 Oct unless the Chair records otherwise (restore to 17791 is a rollback).
- **Stale backup trig_01RfJk1R3BRaxJWRAZRPv2tQ** (names bokuto-27): ignore any instruction to trial bokuto-27.
- Battles dispatch enabled (D-055), no jobs. No API/quota errors in *.done.json. Blackouts 23:52–00:12, 01:52–02:12Z. r/daichi e1cd1a81a pushed (= origin).

## Next unit

1. Read BOARD from 1520. live_monitor (active should be 18078). Fault scan new games (faultscan.py; select team 7 rows by started_at, sub_a/sub_b are null in index.jsonl).
2. At first series boundary ≥ 60 ranked of 18078: `python3 build/daichi/tmp/tab88.py`; post table (first 60, 1725 anchor, vs +0.204 and +0.126) and the watch items; trial 6 choice is the Chair's.

## Open questions for the Chair

- none.

## Units

- 2026-10-05 23:51–00:00Z unit 38 — read BOARD 1513–1519 (D-091). 18078 15 ranked 5-10, no faults. No actions.
- 2026-10-05 22:50–23:05Z unit 37 — read BOARD 1508–1511 (D-090: trial 5 = 61). Trial 4 look: 17940 +0.093 not kept; 17791 incumbent of record. bokuto-61-mouth registered, uploaded 18078, activated 22:55:18Z; BOARD 1512; user notified.
- 2026-10-05 21:51–22:00Z unit 36 — read BOARD 1502–1507 (61 card: conditions met; twin-miss caveats; no Chair naming yet). 17940 55 ranked, no faults. No actions.
- 2026-10-05 20:51–21:00Z unit 35 — read BOARD 1491–1501 (D-089: no pre-look stop for trials; trial 5 = 61 if named else 46). 17940 40 ranked, @1725 +0.092, no faults. No actions.
- 2026-10-05 19:50–20:05Z unit 34 — read BOARD 1480–1489 (D-088). D-088 §B table posted (line 1490); 17940 20 ranked, no faults; anchor question asked.
- 2026-10-05 18:50–18:58Z unit 33 — read BOARD 1462–1479 (D-087: limit 100 M, trial 5 order; bokuto-41 fails). 17940 active, 5 ranked, no faults. No actions.
- 2026-10-05 18:17–18:30Z unit 32 (backup send_later) — read BOARD 1456–1461. 17791 at 65 ranked: look at 60 applied → 17791 incumbent of record (+0.114). asahi-27-b13-reserve registered 18:19Z, uploaded as 17940, activated 18:25:06Z. BOARD 1462; user notified.
- 2026-10-05 17:51–17:58Z unit 31 — read BOARD 1441–1455 (D-086 §D points settled at 100 M historic; bokuto-35 fails; trial-4 forecast filed). 17791: 59 ranked, +0.035, no faults; look not reached. No server actions, no BOARD line.
- 2026-10-05 16:51–16:56Z unit 30 — read BOARD 1421–1440 (D-085, D-086: trial 4 = asahi-27-b13-reserve; look ≈ 17:50–18:10Z). 17791: 40 ranked, +0.058, no faults. No server actions, no BOARD line.
- 2026-10-05 14:51–15:00Z unit 29 — read BOARD 1416–1420 (D-084: back-to-back trials, trial 4 asahi-27). 17791 active, 10 ranked, no faults. Trial 4 staged and fp-checked. No server actions.
- 2026-10-05 13:50–14:22Z unit 28 — read BOARD 1402–1414 (D-083). bokuto-18-queenfeed copied, fp-checked, registered 13:53Z; blackout wait; uploaded as 17791, activated 14:19Z. BOARD 1409, 1415; user notified.
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
