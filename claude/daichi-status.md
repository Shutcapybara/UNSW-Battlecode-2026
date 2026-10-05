# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 23, 2026-10-05 ~08:52Z)

- **Last BOARD line read:** 1333 (Hinata P-9 S0 stop, 08:40Z). My line 1334 (trial-2 interim). Next unit reads from 1335.
- **LIVE = 17530 (`bokuto-13-cull`), D-077 §A TRIAL 2, not a promotion;** status.json active 17530 (08:44Z). Window from 08:15:41Z.
- **Trial-2 interim 08:41Z:** 25 ranked games / 5 series, W–L 10–15, score−E @1725 −0.193 [−0.247, −0.137], perf 1567;
  vs ref 14585 −0.150 [−0.236, −0.057]. Monitor: Elo 1701, rank 98 (h24 1720). Faults not yet scanned.
- **Trial 1 closed (17388 kenma-03):** +0.074 [−0.048, +0.197] @1725, 60 games / 12 series. Ref 14585 −0.043 (120 ranked before 02:13Z).
- **D-077 rule at trial 2's look (first series boundary ≥ 60 games, ~11:15Z):** highest primary statistic among 17388, trial 2, ref
  becomes incumbent at once; lead < 0.03 keeps 14585; both trials < −0.15 → 14585 control. D-078 §C tie rule: trial bots differ
  ≤ 0.10 → pool decides (bokuto-13-cull). Report Schooltime (both layouts) apart from the rest; queen column; table by map; faults.
  If 17388 wins: restore.json {"previous":17530,"candidate":17388,…} (candidate = submission id); BOARD + PushNotification.
- No API/quota errors in *.done.json. git.done 08:25Z merged r/daichi (Chair request).

## Next unit

1. Read BOARD from 1335. live_monitor (active must be 17530).
2. `trial_d075.py --ref 14585:2026-10-05T02:13:00Z:120 --sub 17530 --maxgames 60`; sidescan2 faults in chunks of ≤ 30 ids.
3. At the 60-game boundary: post table, apply D-077/D-078, restore if the winner is not 17530; notify user.
4. D-073 code items; tests in $HOME/daichi-test; redeploy.

## Open questions for the Chair

- None open.

## Units

- 2026-10-05 ~08:51Z unit 23 — read BOARD 1328–1333 (Sugawara/Hinata P-9; nothing for Live ops). Trial-2 interim 25 games −0.193 @1725; BOARD 1334.
- 2026-10-05 ~08:15Z unit 22 — read BOARD 1263–1325 (D-077, D-078). Trial-1 look posted (1318). bokuto-13-cull copied, fingerprint-checked, registered; uploaded as 17530 (08:14Z) and activated (first series 08:15:41Z); BOARD 1318, 1326, 1327 (Schooltime in draw: 145/2,249 ranked since 05Z). User notified. Push requested after the Chair merge git.json cleared.
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
