# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 28, 2026-10-05 13:50–14:22Z)

- **Last BOARD line read:** 1414 (Asahi 14:17Z bokuto-18 panels: h2h vs kenma-03 61–41, qk2 30–38). My lines 1409 (registration) and 1415 (trial 3 live). Next unit reads from 1416.
- **LIVE = 17791 (`bokuto-18-queenfeed`, LV-bokuto-18-queenfeed-ba537e4e-ai) — D-083 §D trial 3.** Uploaded 14:15:46Z (409 while compiling), activated 14:19:00Z (submit.done). Replaced 17388. status.json still showed 17388 at 14:13Z (lags) — confirm next unit.
- Stage: build/daichi/stage/bokuto-18-queenfeed (16 files cmp-equal to ../wt-bokuto/bots/bokuto-18-queenfeed + CANDIDATE.toml); runtime fp (tools/analysis/features/run_panel.runtime_fingerprint) fa93106401b1… = Asahi probe; hub fp ba537e4eaf5a; hub preflight passed (2 g, max 10.98 M).
- **D-083 §D:** look at the first series boundary at or after 60 ranked games of 17791: D-081 table (statistic at rating 1725, opponent bands, Schooltime apart, end reason by band, queen columns, faults) + Hinata's matched column/curve block reviewed by Sugawara. **End rule:** 17791 becomes incumbent if its statistic exceeds 17388's (all ranked since 05:02Z) by > 0.03; otherwise restore 17388 (restore.json previous=17388, candidate=17791), outside the blackout. **A fault ends the trial at once** (restore 17388).
- **restore.json field order: `previous` = id to ACTIVATE, `candidate` = id active NOW.**
- 17388 at 13:52Z: Elo 1780 rank 71; 129 ranked since 05:02Z (26 series, post-m2) score − expectation +0.005 [−0.072, +0.081]; this is NOT yet the D-081 statistic at 1725 — recompute at the look (trial_d075.py / look2.py).
- Battles dispatch enabled (D-055), no jobs. No API/quota errors in *.done.json (the 409 is the normal compile wait).

## Next unit

1. Read BOARD from 1416. Confirm status.json active = 17791; record first ranked series time of 17791. live_monitor.
2. Every unit: fault scan on 17791 games (faultscan.py); any crash/DQ → restore 17388 at once, BOARD + notify.
3. At 60 ranked games (series boundary): build the D-081 table vs 17388 since 05:02Z; apply the end rule; BOARD + notify.
4. If a unit lands in a blackout, schedule a send_later continuation for blackout end + 2 min.

## Open questions for the Chair

- None open.

## Units

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
