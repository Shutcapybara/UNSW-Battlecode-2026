# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 24, 2026-10-05 ~10:00Z)

- **Last BOARD line read:** 1346 (Hinata 09:47Z). My line 1347 (D-079 screen prepared + trial-2 at 45). Next unit reads from 1348.
- **LIVE = 17530 (`bokuto-13-cull`), D-077 §A TRIAL 2, not a promotion;** window from 08:15:41Z.
- **Trial-2 at 45 ranked games / 9 series (to 09:43Z):** W–L 21–24, score−E @1725 −0.087 [−0.178, +0.020]; vs ref 14585 −0.044
  [−0.162, +0.082]. Monitor Elo 1749, rank 82 (h24 1717). Faults not yet scanned.
- **Trial 1 closed (17388 kenma-03):** +0.074 [−0.048, +0.197] @1725, 60 games. Ref 14585 −0.043 (120 ranked before 02:13Z).
- **D-077 rule at trial 2's look (first series boundary ≥ 60 games, ~11:15Z):** highest primary statistic among 17388, trial 2, ref
  becomes incumbent at once; lead < 0.03 keeps 14585; both trials < −0.15 → 14585 control. D-078 §C tie rule: trial bots differ
  ≤ 0.10 → pool decides (bokuto-13-cull). Report Schooltime (both layouts) apart; queen column; table by map; faults.
  **D-079 adds: split both trial windows by opponent rating (above / below 1725).**
  If 17388 wins: restore.json {"previous":17530,"candidate":17388,…}; BOARD + PushNotification. If 14585 wins: restore to 14585.
- **D-079 screen prepared, NOT dispatched:** docs/learning/screens/LS-D079-draft.md (+ sz.py). Arms 14585/17530/17388, opps
  347,187,959,1091,507,213. 0.10 needs ~720 games; 360 gives ±0.08–0.09. Dispatch only on a later D-record, after the look.
- Battles dispatch still enabled (D-055), no open jobs. No API/quota errors in *.done.json (git.done 09:22Z merged r/daichi).

## Next unit

1. Read BOARD from 1348. live_monitor (active must be 17530).
2. `trial_d075.py --ref 14585:2026-10-05T02:13:00Z:120 --sub 17530 --maxgames 60`; sidescan2 faults in chunks of ≤ 30 ids.
3. At the 60-game boundary: table (by map, Schooltime apart, queen column, rating split ≥/< 1725 for 17388 and 17530), apply
   D-077/D-078, restore if the winner is not 17530; BOARD + notify user.
4. D-073 code items; tests in $HOME/daichi-test; redeploy.

## Open questions for the Chair

- None open (D-079 screen awaits a dispatch record).

## Units

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
