# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 19, 2026-10-05 ~05:12Z)

- **Last BOARD line read:** 1212 (kenma 05:08Z). Posted 1213 (D-052 §B rollback) and 1214 (Kenma trial start + D-073
  checks), 05:11Z. Next unit reads from 1215.
- **LIVE = 17388 (`kenma-03-pocket-queen`, LV-kenma-03-pocket-queen-c5d2ff46-ai) — D-074 §B TRIAL, not a promotion.**
  Uploaded 05:00:14Z (activate → 409 "only a ready version" while compiling); the server auto-activated it on ready,
  first ranked series 05:02Z; my second activate confirmed 05:04:23Z. Trial window = 17388 ranked games from 05:02Z;
  anchor = our rating at ~05:00Z (≈1605, rank 120 at 04:47Z snapshot). Restore target after the trial: **14585**.
- **16979 rolled back (D-052 §B fired):** 45 ranked / 9 series (44 with E); diff vs 14585 last 120 = −0.263, 95th
  −0.126; restore.done 04:53:55Z, active 14585 re-read 04:58:10Z. Queen column 16979: queen W–L 1–14, queen alive at
  end 4/44, 0 faults. User notified (rollback, and the trial upload/activation).
- Registration: build/daichi/stage/kenma-03-pocket-queen (extracted from build/kenma/deploy zip sha e98718a5; runtime
  fp e60733a926fc recomputed equal; manifest legacy_none contract; hub fp c5d2ff46ce14).
- **D-073:** hub redeployed 04:06Z; redeploy ban lifted. Verified: index blinding (opponent bot_a/bot_b = ""; ours kept,
  so attribution of our own sub still works). Not yet exercised: upload-fix restore path, reserve 5. **Owed (Daichi, no
  ban):** seat field in live-screen job rows, end reason `queen` in executor.analyse_replay, frozen pairing rule for
  duplicate cells (D-070 §B), then redeploy via request_redeploy.py.
- Keeper: blocked since 04:31Z on tracked tools/learn/__pycache__ (git add of ignored path). Unit 18 push confirmed
  (r/daichi 236d2d224 = origin). Run main-checkout code with PYTHONDONTWRITEBYTECODE=1.
- No API/quota errors in *.done.json. status.json refreshes only every ~10 min (stale reads possible).

## Next unit

1. Read BOARD from 1215.
2. Run live_monitor (active should be 17388; anything else = human activation → pause, tell Chair + user) and
   `sidescan2.py --sub 17388` (any TLE / caught error / DQ → end trial at once: restore.json
   {"previous":14585,"candidate":17388,...}, BOARD, PushNotification).
3. **Trial look at the first series boundary at or after 60 ranked games of 17388** (~08:00Z at 5 games / ~17 min):
   score − E with rating fixed at activation, series bootstrap 5/95, vs 14585 last 120 and vs 16979's 45-game window;
   queen alive at end, queen-rule W–L, table by map. Then restore 14585 (restore.json), confirm, BOARD, notify user.
   rollback_d052.py is written for previous→live; add a `--ref`/`--new` option or a small trial script.
4. D-073 code items (seat field, end reason queen, frozen pairing rule) in the tree; tests in $HOME/daichi-test; redeploy.
5. Bokuto-07 trial follows Kenma's once the Chair confirms Bokuto's points-per-turn + pool panel.

## battles.json — what it does

Request: `{label, by, decision, note, arms:[{submission}|{candidate}], opponents:[ids], maps:[names]|omit, seats:"both",
games_per_pair:2, max_games, deadline_hours}`; actions `enable` / `disable` (need `decision`) and `cancel`.
Answer: `battles.done.json`. Job state and per-game rows + paired report: `hub-state/battles/<job>.json`, index
`hub-state/battles/index.json` (refreshed every 5 min).
- Units = one opponent × a chunk of ≤ 5 maps × every arm, back to back (arm order shuffled per unit); `seats: both`
  posts the chunk twice in the D-022 rotation, so each map is played at both id parities (layout = f(map, parity)).
- Every POST goes through `executor.request_batch`: reserve → temporary activation of a non-live arm → POST →
  restore. A non-live arm is never dispatched in the even-hour blackout (−8/+12 min) or while one of our ranked series
  is in flight. A whole unit must fit the pool's rolling-hour allowance minus a reserve (field 10, dev 5) and ≤ 40
  games per 5-minute pass. A lost restore is repaired before any dispatch.
- A job pauses when the live submission differs from the one it was accepted under (human activation), and expires
  at its deadline. Games are harvested by the executor's own harvest (runs in shadow mode too), `block_id = job:<id>`;
  the collector watches team 7, so replays also land in `public_replays/corpus`.
- Paired report: candidate − reference by (opponent, map, parity); missing/unverified cells dropped and counted;
  cluster bootstrap over opponents, 1,000 resamples, seed 7, 5th/95th percentile.

**Budget arithmetic:** a full LIVE_MAPS_M2 screen, 2 arms × 17 maps × 2 seats = 68 games per opponent. At the field
allowance (60/h, minus teammates and reserve) that is ~1 opponent per hour; 60 matched pairs need ~2 opponents ≈ 2–3 h.
Dev opponents (545, 752) have their own 60/h.

## Open questions for the Chair

- Redeploy (main holds submit_check fix + reserve 5 + blind fix): waits on the Chair's restart-loop post (D-057 §A,
  D-060 §D); blind fix deploys only after LS-1 closes (D-064 §B).

## Units

- 2026-10-05 ~05:12Z unit 19 — read BOARD 1180–1212, D-073, D-074. D-052 §B fired on 16979 (−0.263, 95th −0.126)
  → restored 14585 04:53Z; registered + uploaded kenma-03 (17388), live 05:02Z as the D-074 trial; BOARD 1213–1214; user notified.
- 2026-10-05 ~03:55Z unit 18 — read BOARD 1160–1178, D-070, D-071. 16979 29/40 ranked, interim diff −0.263
  (95th −0.085); queen column added (sidescan2.py); posted BOARD 1179. No action.
- 2026-10-05 ~03:00Z unit 17 — read BOARD 1150–1159, D-069. 16979 10/40 ranked, −0.439 (2 series), Elo 1643;
  0 faults by replay scan; posted early watch + round-500 contradiction (BOARD 1160). No action.
- 2026-10-05 ~02:20Z unit 16 — read BOARD 1100–1140, D-068. LS-1 expired at deadline; D-064 table posted (BOARD
  1141); all hold → activated 16979 at 02:13Z (BOARD 1151); user notified.
- 2026-10-05 ~00:55Z unit 15 — read BOARD 1055–1099, D-066. LS-1 140/204, 0 faults. Monitor: rolling-40 −0.115,
  own pct 0.149, Elo 1716 r88. No BOARD line, no action (D-064 stop not before 02:15Z).
- 2026-10-04 ~23:55Z unit 14 — read BOARD 1034–1053, D-065. Cleared the keeper's .pyc blocker (BOARD 1054). Drift
  row now prints own-history percentile (D-065 §B). LS-1 120/204, 0 faults. Interim paired seen in index dump (not used).
- 2026-10-04 ~22:55Z unit 13 — read BOARD 985–1031, D-064. Supplied 16979 archive for D-064 §B(5). LS-1 100/204,
  0 faults. Incumbent rolling-40 drift flag on. BOARD 1032–1033.
- 2026-10-04 ~21:55Z unit 12 — read BOARD 923–983, D-062, D-063. Found the index.json blinding gap; blind() fix
  in tree (tests 50/50). LS-1 100/204, 80 verified, 0 faults. Monitor flat. BOARD 984.
- 2026-10-04 ~20:55Z unit 11 — read BOARD 903–921, D-060, D-061. MATCHING proxy label in paired_report (tree, tests
  49/49). LS-1 80/204, 60 verified, 0 faults. Monitor flat. BOARD 922.
- 2026-10-04 ~20:00Z unit 10 — read BOARD 836–899, D-056, D-057, D-058, D-059. Built submit_check fix + reserve 5 +
  job-row fields with tests (not deployed, D-057 §A). Answered the seed question; reported opponent-id gap and 16979
  exposure 0; LS-1 deferral reasons. Monitor flat.

- 2026-10-04 ~17:55Z unit 9 — read BOARD 835. No D-056, no Chair answer. 16979 ranked exposure = 0. Job 20/204
  requested, 0 verified, 0 faults. Monitor flat. No BOARD line, no notification.
- 2026-10-04 ~17:45Z unit 8 — read BOARD 819–834, D-055. LS-1: manifest, build, probe, register, upload 16979
  (server auto-activated; restored 14585 17:40Z), job 5ed81ad3e1f3 dispatching. BOARD 831, 832, 833/834. Two notifications.
- 2026-10-04 ~16:58Z unit 7 — read BOARD 795–817. Monitor flat. BOARD 818 (live read on bed-variant maps).
  battles.py rejected-request counts + test (lane tree).
- 2026-10-04 ~15:55Z unit 6 — read BOARD 770–793, D-054. A/A job closed: 752 rejected (no active
  submission), degenerate pass vs 545 (1/68). Dispatch disabled. BOARD 794. Monitor refreshed.
- 2026-10-04 ~14:55Z unit 5 — read BOARD 742–769, D-053. Monitor refreshed (no change of note); style roster
  filled. A/A job 68/136, 0 faults. No BOARD line (nothing new to report).
- 2026-10-04 ~14:00Z unit 4 — read BOARD 714–739, D-052. Rollback-rule simulation on D-052 §B as written
  (`rollback-d052.md`); monitor split by map variant (D-052 §E). A/A job 40/136, 0 faults.
- 2026-10-04 ~12:57Z unit 3 — read BOARD 688–713, D-051. Redeployed (8988d9489), linked 14585 (register.json), enabled
  dispatch and submitted A/A job 952053397eed (136 games). Fixed rating_at + frozen monitor inputs (D-051 §4).
- 2026-10-04 ~12:00Z unit 2 — read BOARD 651–687, D-048, D-050 §4/§8. Monitor refreshed. Redeployed the hub (D-048 §2).
  Fingerprint-checked 14585 and built the register.json link item. Ran the quota-runner check, which found 7
  unexplained series. Sized the A/A run. Filed the D-048 §8 review (`tools/daichi/rollback_power.py`).

- 2026-10-04 ~10:50Z unit 1 — read macro, prompts, D-041–D-045, hub docs, actuator/executor/quota code, BOARD tail.
  Built `tools/hub/battles.py` + actuator hook + config pacing + `tests/test_hub_battles.py`; built
  `tools/daichi/live_monitor.py` → `docs/learning/live.md`. Committed to `r/daichi`; push requested.
  Next: on Chair answers → enable/merge/redeploy; hourly live.md refresh; rosters (style row waits for Data's
  top-team pages).

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
