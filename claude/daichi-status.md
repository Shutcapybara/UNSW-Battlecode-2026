# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 31, 2026-10-05 17:51–17:58Z)

- **Last BOARD line read:** 1455 (Asahi 17:49Z bokuto-35 atlas-off twin). Next unit reads from 1456.
- **SUPERSEDED — read before acting on any backup prompt:** D-085 §C (trial 4 = `bokuto-27-exitsplit`) was REPLACED by D-086 §B (Chair 16:25Z): trial 4 = `asahi-27-b13-reserve`; bokuto-27 is NOT trialled. The old 18:14Z backup (trig_01RfJk1R3BRaxJWRAZRPv2tQ) still names bokuto-27; any run from it must NOT register/upload bokuto-27 — follow this doc. (Disabling that task was refused from the lane; the user was asked to disable it.)
- **LIVE = 17791 (`bokuto-18-queenfeed`) — trial 3.** At 17:51Z: 59 ranked / 12 series since activation, monitor mean +0.035 [−0.072, +0.154]; rolling 40 −0.011 [−0.149, +0.138] (monitor statistic, not D-084's). Elo 1838 rank 59 (24 h ago 1725, 7 d 1767). Fault scan: 24 more games since 16:4xZ, 0 TLE, 0 exceptions either side, cpu_max 12.58 M (cumulative 79 games, 0 faults).
- **Look:** 60-game series boundary not yet reached at 17:51Z (59). Hinata (17:36Z) puts it ≈ 18:20–18:45Z and reads the curve block next unit with the frozen procedure. 18:00 blackout 17:52–18:12Z: register/submit/activate only ≥ 18:12Z.
- **D-086 §B: trial 4 = `asahi-27-b13-reserve`** (Hinata pre-registered trial-4 forecast 17:36Z, P-hinata-07). Staged at build/daichi/stage/asahi-27-b13-reserve (fp 16ceecff52c5… = Asahi probe), NOT yet registered. At the look: register.json {"candidates":[{"dir":"build/daichi/stage/asahi-27-b13-reserve","priority":100}]}, then submit.json {"candidate":"asahi-27-b13-reserve","activate":true} (409 while compiling → resubmit ~3 min). Trial 5: bokuto-35 does NOT qualify (Asahi 17:13Z, Sugawara 17:26Z); Bokuto now testing bokuto-41-atlas0 (card ≈ 19:15Z). Chair names trial 5.
- **D-084 end rule:** statistic at 1725 for 17791 vs 17388 on all ranked games since 05:02Z; 17791 becomes incumbent of record if it exceeds by > 0.03, else 17388 stays. Table: statistic at 1725, bands, Schooltime apart, end reason × result by band, queen columns, faults, reached-r300 and carried views; Hinata posts the curve block and seat × result.
- **D-086 §D points:** Hinata/Sugawara: server cut at 100 M on 25–29 Sep; our current bots peak ~13 M. Limit stays 30 M until the Chair posts otherwise; Asahi burn test ≈ 18:15Z. No Live ops action.
- restore.json field order: `previous` = id to ACTIVATE, `candidate` = id active NOW. A fault ends a trial at once (restore 17388).
- Battles dispatch enabled (D-055), no jobs. No API/quota errors in *.done.json; git.done 16:55Z pushed r/daichi.
- Backup send_later at 18:16Z (trig_01UCULKias2ATFbANx6hz14j) covers the look/upload window before the 18:51Z hourly unit.

## Next unit

1. Read BOARD from 1456. live_monitor; fault scan 17791 (`python3 build/daichi/tmp/faultscan.py <ids>`; ids from index.jsonl where bot_a/bot_b == "17791", started_at ≥ 17:4xZ).
2. If ≥ 60 ranked at a series boundary: build table (trial_d075.py / look2.py), apply D-084 end rule, post BOARD; after 18:12Z (and outside 19:52–20:12Z) register + upload + activate trial 4, BOARD + notify user.

## Open questions for the Chair

- None open.

## Units

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
