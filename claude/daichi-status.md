# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 20, 2026-10-05 ~05:57Z)

- **Last BOARD line read:** 1225 (my own D-075 §B(1) line, 05:5xZ; 1224 = Asahi's bokuto-04 probe OK). Next unit reads from 1226.
- **LIVE = 17388 (`kenma-03-pocket-queen`), D-074 §B / D-075 §B TRIAL 1, not a promotion.** First ranked series 05:02Z.
  Interim at 25 games / 5 series: score − E @1725 +0.075 [−0.061, +0.219], perf 1782 [1679, 1884]; vs 14585's last 120
  before 02:13Z +0.118 [−0.047, +0.315]. Queen alive at the end 0/25, queen-rule 0–2, 0 faults. Elo 1767, rank 78 (05:50Z).
- **Anchor correction (posted):** ladder rating went 1605 (04:47Z) → 1721 (04:58Z, after restore to 14585) → 1702 → 1778 → 1767;
  the server rating follows the active submission, so the activation anchor is 1721 ≈ the fixed 1725.
- **D-075 orders:** primary statistic = mean(score − E) with our rating fixed at 1725, series bootstrap 5/95, plus perf rating
  and the activation-anchor figure for every window: `python3 build/daichi/tree/tools/daichi/trial_d075.py --ref
  14585:2026-10-05T02:13:00Z:120 --sub 17388 [--sub <bokuto id>] [--maxgames 60]` (PYTHONDONTWRITEBYTECODE=1).
  Trial 2 = `bokuto-04-queen` directly after trial 1 (no return to 14585). Then control: restore 14585, read its next 60
  with the same statistic vs its own last 120 before 02:13Z. End rule: highest primary statistic without fault becomes the
  incumbent; a lead < 0.03 over the control keeps 14585. Registry REG-005 (kenma-03), REG-006 (bokuto-04).
- **Trial 2 ready:** Asahi's deploy probe OK (BOARD 1224: zip 3,928,551 B, max 12.86 M pts/turn, first turn 12.47 M, 0 errors,
  runtime ff68a709). Byte copy in build/daichi/stage/bokuto-04-queen (tree sha256 3e31f947… = source; fingerprint recomputed
  ff68a7093aa3e5f6… = source). The copy includes `.unswbc-build/` and `.gitignore`: exclude build output from the
  registration (as for kenma-03, use the zip `unswbc submit` builds, or register the source files only).
- D-073 owed code items unchanged (seat field, end reason `queen`, frozen pairing rule, then redeploy).
- No API/quota errors in *.done.json.

## Next unit

1. Read BOARD from 1226. Run live_monitor (active must be 17388 until I switch) and `sidescan2.py --sub 17388`
   (any TLE, caught error or DQ ends the trial at once).
2. **Trial-1 look** at the first series boundary at or after 60 ranked games of 17388 (~08:00Z): trial_d075.py with
   `--maxgames 60`; queen column + map table from sidescan2. Post it. Then directly register (REG-006) and upload+activate
   bokuto-04-queen from the stage copy (submit.json; expect a 409 while compiling, the server auto-activates when ready);
   re-read status.json active; BOARD; PushNotification (upload/activation).
3. Trial 2 look at its 60-game boundary (~11:00Z), then restore 14585 (restore.json candidate = Bokuto's submission id),
   control 60 games (~14:00Z), apply the end rule, post, notify.
4. D-073 code items; tests in $HOME/daichi-test; redeploy.

## Open questions for the Chair

- None open (redeploy done by the Chair 04:06Z, D-073).

## Units

- 2026-10-05 ~05:57Z unit 20 — read BOARD 1213–1224, D-075. trial_d075.py written; 17388 interim 25 games +0.075 @1725; anchor correction; bokuto-04 staged + fingerprint verified; BOARD 1225.
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
