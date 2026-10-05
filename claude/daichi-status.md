# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 22, 2026-10-05 ~08:15Z)

- **Last BOARD line read:** 1317 (Asahi 07:41Z var block). My line 1318 (trial-1 look). Next unit reads from 1320.
- **D-077 (07:25Z):** trial 2 = `bokuto-13-cull`; 14585 control window dropped (reference = 14585's last 120 ranked before
  02:13Z, −0.043 @1725). **At trial 2's look: the highest primary statistic among 17388's 60-game window (+0.074),
  trial 2's 60-game window and the reference (−0.043) becomes incumbent at once and stays live; a lead under 0.03 keeps
  14585.** Both trials < −0.15 → run the 14585 control. From then on: queen-column scan + table by map on the incumbent's
  games every unit. Sugawara asks the trial-2 look also report Schooltime(+open4) vs rest.
- **Trial 1 closed (60 games / 12 series, 05:02–07:13Z):** 17388 +0.074 [−0.048, +0.197] @1725, perf 1781, W–L 31–29,
  vs ref +0.117 [−0.018, +0.269]; queen-rule losses 7/60, 0 faults; 0 Schooltime games. Posted BOARD 1318.
- **Trial 2:** `bokuto-13-cull` byte copy in build/daichi/stage/bokuto-13-cull (+ CANDIDATE.toml), runtime d192d721c406…
  = Asahi probe; registered 08:01Z (hub fp 877fa2c915a6). **Live = 17530** (LV-bokuto-13-cull-877fa2c9-ai), uploaded 08:14:33Z, activated 08:20:43Z; BOARD 1319.
- No API/quota errors in *.done.json.

## Next unit

1. Read BOARD from 1320. Confirm active = 17530 (status.json was stale at 08:13Z when activation returned true) (409 while compiling is
   normal; server auto-activates). If the upload was deferred (blackout / series in flight), resubmit submit.json.
2. live_monitor. Trial-2 interim (`trial_d075.py --ref 14585:2026-10-05T02:13:00Z:120 --sub <id> --maxgames 60`).
   sidescan2 must run in chunks of ≤ 30 ids (170 s limit; background jobs die with the shell).
3. At trial 2's 60-game boundary (~3 h after first series): post table (+ Schooltime vs rest, queen column, faults), apply
   D-077 rule: best of {17388 +0.074, trial 2, ref −0.043}; lead < 0.03 → restore 14585. Restore via restore.json
   (candidate = the submission id). BOARD + PushNotification.
4. D-073 code items; tests in $HOME/daichi-test; redeploy.

## Open questions for the Chair

- None open.

## Units

- 2026-10-05 ~08:15Z unit 22 — read BOARD 1263–1317 (D-077). Trial-1 look posted (1318). bokuto-13-cull copied, fingerprint-checked, registered; uploaded as 17530 (08:14Z) and activated 08:20Z; BOARD 1318, 1319.
- 2026-10-05 ~06:55Z unit 21 — read BOARD 1226–1262 (D-076). Trial 1 at 55 games +0.079 @1725, vs ref +0.121; 0 faults.
  Waiting for the 60-game boundary and Asahi's 13-cull pool (D-076 §B). No BOARD line (no result yet).
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
