# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 29, 2026-10-05 14:51–15:00Z)

- **Last BOARD line read:** 1420 (Bokuto 14:46Z JOB bokuto-27-exitsplit). Next unit reads from 1421.
- **LIVE = 17791 (`bokuto-18-queenfeed`) — trial 3, confirmed active in status.json 14:44Z.** First ranked series 14:30:13Z; at 14:51Z 10 ranked / 2 series: +0.054 [−0.076, +0.183] (monitor; not the D-081 statistic). Elo 1806 rank 67. 44 games scanned (10 ranked + 34 unranked): 0 TLE, 0 exceptions on our side, cpu_max 13.05 M.
- **D-084 (Chair 14:24Z): apply the end rule at the look myself, then start trial 4 at once.** Look = first series boundary ≥ 60 ranked games of 17791 (~16:50–17:20Z at 12 min/series). Statistic at 1725 for 17791 vs 17388 on all its ranked games since 05:02Z; trial bot is incumbent of record if it exceeds by > 0.03, else 17388 stays incumbent. Post the full table (statistic at 1725, bands, Schooltime apart, end reason × result by band, queen columns, faults; **reached-r300 and carried views side by side** per Sugawara 14:40Z / Hinata 14:36Z; enemy-queen death round/cause if cheap per Bokuto 14:36Z).
- **Trial 4 = `asahi-27-b13-reserve`** — staged at build/daichi/stage/asahi-27-b13-reserve (16 files cmp-equal to ../wt-asahi/bots + CANDIDATE.toml); runtime fp 16ceecff52c5… = Asahi probe. **NOT yet registered** (actuator says registration auto-queues preflight/upload; not risked mid-trial). At the look: register.json {"candidates":[{"dir":"build/daichi/stage/asahi-27-b13-reserve","priority":100}]}, then submit.json {"candidate":"asahi-27-b13-reserve","activate":true} outside the blackout (409 while compiling → resubmit ~3 min). Trial 4 replaces 17791 directly (no restore to 17388 needed in between); record which is incumbent of record.
- **restore.json field order: `previous` = id to ACTIVATE, `candidate` = id active NOW.** A fault ends a trial at once (restore 17388).
- Battles dispatch enabled (D-055), no jobs. No API/quota errors in *.done.json.
- Backup send_later set for ~17:22Z in case hourly units miss the look.

## Next unit

1. Read BOARD from 1421. live_monitor; fault scan 17791 (ids from index.jsonl where bot_a/bot_b == "17791"; our side B so far).
2. If ≥ 60 ranked at a series boundary and outside the blackout (even-hour −8/+12 min): build table (trial_d075.py / look2.py), apply end rule, register + upload + activate trial 4, BOARD + notify user.

## Open questions for the Chair

- None open.

## Units

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
