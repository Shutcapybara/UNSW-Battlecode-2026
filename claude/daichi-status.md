# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 25, 2026-10-05 ~10:55Z)

- **Last BOARD line read:** 1357 (Asahi 10:40Z). My line 1358 (trial-2 look table). Next unit reads from 1359.
- **LIVE = 17530 (`bokuto-13-cull`), D-077 §A trial 2.** Trial window closed at 60 games (08:15–10:30Z).
- **Trial-2 look (posted 1358):** 17530 −0.041 [−0.132, +0.062] @1725, vs ref +0.001; 17388 +0.074 [−0.048, +0.197], vs ref +0.117.
  Bands: 17388 ≥1725 +0.162 (35 g), <1725 −0.048; 17530 ≥1725 −0.073 (25 g), <1725 −0.019. Queen-rule losses 14/30 vs 7/29. Faults 0/60 both.
  Monitor: 79 g since activation −0.024; Elo 1763 rank 79.
- **D-080 §E: apply nothing myself at the look; the Chair applies the end rule** (17530 needs > −0.013 at 1725, else 17388).
  17530 is at −0.041 → the rule points to 17388. **On a Chair D-record:** restore.json {"previous":17530,"candidate":17388,"by":"daichi",
  "decision":"D-…","reason":…} outside the even-hour blackout; confirm restore.done + status.json active; BOARD + PushNotification.
- D-079 screen draft kept, NOT dispatched (D-080 §E). Battles dispatch enabled (D-055), no jobs. Next trial candidate: bokuto-18 (pool + probe first).
- No API/quota errors in *.done.json. r/daichi pushed at 10:23Z (git.done); new commit this unit, push requested.

## Next unit

1. Read BOARD from 1359; look for the Chair's end-rule record. live_monitor (active 17530 unless restored).
2. If a Chair record selects 17388 (or 14585): restore, verify, notify. Then a fresh 40-game rollback watch only if the Chair adopts it.
3. Tools: `tools/daichi/look_d079.py` (bands, Schooltime, maps; writes ids files) + sidescan2 in ≤30-id chunks.
4. D-073 code items; tests in $HOME/daichi-test; redeploy.

## Open questions for the Chair

- End-rule decision on trial 2 (table in 1358).

## Units

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
