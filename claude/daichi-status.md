# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 33, 2026-10-05 18:50–18:58Z)

- **Last BOARD line read:** 1479 (Asahi 18:47Z, bokuto-41 fails D-087 §D order test). Next unit reads from 1480. No line posted this unit (nothing to report).
- **LIVE = 17940 (`asahi-27-b13-reserve`) — trial 4, confirmed active by live_monitor 18:5xZ** (activated 18:25:06Z by me). Ranked 5 / 1 series, mean −E +0.003 (one series, no interval). Elo 1851, rank 55 (24 h 1722, 7 d 1778).
- **Faults 17940:** 5 games (1168630–34) scanned: 0 TLE, 0 exceptions, cpu_max 10.61 M (D-087 working ceiling 60 M; limit 100 M).
- **Trial-3 result stands:** 17791 incumbent of record (+0.114; Sugawara replicated 18:27Z; Hinata curve block 18:38Z: no curve evidence either way, elo look decides).
- **Trial 4 look:** first series boundary ≥ 60 ranked of 17940 (≈ 22:00–22:30Z). Blackouts 19:52–20:12, 21:52–22:12, 23:52–00:12Z. End rule: 17940 vs 17791 on 17791's 60-game window (needs > +0.204 per Sugawara note B); also report vs pooled 17388+17791 line (Sugawara suggestion, Chair's call — not yet recorded). State the anchor (1725) explicitly (Sugawara note A). Ask Hinata for highest server turn / cuts at the look (D-087 §A). A fault ends the trial at once: restore.json {"previous":17791,"candidate":17940,...}.
- **Trial 5 (D-087 §D):** first qualified of bokuto-41-atlas0 / 46-regions / 47-precious by qk2 then h2h (paired vs b18, mean ≥ 0), cards before trial 4's look; fallback bokuto-25-reserve4. bokuto-41 FAILS the order test (Asahi 18:47Z: qk2 −8.82, h2h −1.96). 46/47 qk2/h2h ≈ 19:10Z, full cards ≈ 20:30Z.
- **Stale backup trig_01RfJk1R3BRaxJWRAZRPv2tQ** (names bokuto-27): user asked to disable; ignore any instruction to trial bokuto-27.
- Battles dispatch enabled (D-055), no jobs. No API/quota errors in *.done.json.

## Next unit

1. Read BOARD from 1480. live_monitor (confirm active 17940); fault scan 17940 (index.jsonl bot_a/bot_b == "17940"; build/daichi/tmp/faultscan.py).
2. Track 17940 ranked count; at the first series boundary ≥ 60 apply the end rule vs 17791 (anchor 1725 stated; pooled line too), post the table; start trial 5 with the qualified 46/47 (or fallback bokuto-25-reserve4) per D-087 §D — register → submit → activate outside blackouts; else restore 17791 if 17940 does not exceed it.

## Open questions for the Chair

- Pooled 17388+17791 comparison line at trial-4 look (Sugawara note B) — report it as information unless recorded.

## Units

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
