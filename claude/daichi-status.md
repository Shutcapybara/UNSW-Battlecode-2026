# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 34, 2026-10-05 19:50–20:05Z)

- **Last BOARD line read:** 1489 (Bokuto 19:47Z, commit e92220b72 for 57). My line 1490 (D-088 §B table + D-052 anchor question). Next unit reads from 1491.
- **D-088 recorded:** 17791 incumbent of record (+0.174 [+0.079, +0.282] @1725). Trial 4 = 17940, look ≈ 22:15Z: end rule > +0.204 @1725; also vs pooled 17388+17791 line (+0.096): ≤ +0.126 counts against, +0.126..+0.204 unresolved (stays candidate for a confirmation run). Before the Qualifier activation the two best get a second 60-game window (timing waits on lead's seeding cutoff). Every statistic states its anchor.
- **Trial 5 (D-088 §E) = bokuto-46-regions** if its probe passes and its gen panel 5th pct > −5 (vs bokuto-13-cull's); fallback bokuto-25-reserve4 if its probe passes. Sugawara (19:29Z) reads 46 vs 41 as a waiver, not a pass; order unchanged. Wait for Asahi's 46 probe/gen post. Start at trial 4's look: register → submit → activate outside blackouts (use restore.json if returning to 17791: previous = submission to activate).
- **LIVE = 17940 (`asahi-27-b13-reserve`)**, 20 ranked / 4 series (7–13): @1725 −0.014 [−0.096, +0.069]; live_monitor own-rating anchor −0.136 [−0.209, −0.063]. Elo 1787, rank 72 (24 h 1723, 7 d 1778). Faults: 20/20 scanned (ids in build/daichi/tmp/ids17940.txt, last 1172136), 0 TLE, 0 exc, cpu_max 12.91 M.
- **D-088 §B table done:** build/daichi/tree/docs/learning/trials-1725.md (code build/daichi/tmp/tab88.py).
- **Stale backup trig_01RfJk1R3BRaxJWRAZRPv2tQ** (names bokuto-27): user asked to disable; ignore any instruction to trial bokuto-27.
- Battles dispatch enabled (D-055), no jobs. No API/quota errors in *.done.json. Blackouts 19:52–20:12, 21:52–22:12, 23:52–00:12Z.

## Next unit

1. Read BOARD from 1491 (Chair answer on D-052 anchor; Asahi 46 probe/gen). live_monitor; fault scan new 17940 games (> 1172136).
2. At first series boundary ≥ 60 ranked of 17940: python3 build/daichi/tmp/tab88.py gives the @1725 window; apply D-088 §D (vs 17791 +0.204; vs pooled +0.096 → +0.126 band); post table; then start trial 5 per D-088 §E, or restore 17791.

## Open questions for the Chair

- (asked 19:5xZ, line 1490) Does D-052 §B rollback apply to a trial bot before its look, and on which anchor (own rating vs 1725)?

## Units

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
