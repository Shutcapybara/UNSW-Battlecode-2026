# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 15, 2026-10-05 ~00:55Z)

- **Last BOARD line read:** line 1099 (Tanaka STOP 00:49Z, user request, credit budget — Tanaka lane only). No line
  posted this unit (no result).
- **D-066 (00:36Z):** P-7 throughput PASS, no training approved; A1/A3 selectable; clone live screen does not wait on
  frozen cohort; every upload waits for H11. Chair 00:36Z reaffirms: Daichi applies the D-064 §B rule at the first
  unit after 02:15Z. (Chair also saw the running paired figure through a failed filter; not quoted.)
- **D-064 §B rule (unchanged):** promote 16979 iff (1) ≥ 60 valid matched pairs, missing listed; (2) no candidate
  runtime error/timeout/DQ; (3) 95th pct of paired mean (opp × map clusters, 1,000, seed 7) ≥ 0; (4) paired mean ≥ −0.05.
  (5) met per D-065 §B. Monitor rows: Weakhold, five bed-variant maps, invalid-command deaths.
- **LS-1 job 5ed81ad3e1f3:** 140/204 requested, 140 verified, 0 unverified, 0 runtime faults (00:51Z, filtered read).
  Unit 7 deferred on field quota (need 20, avail 25, reserve 10) — internal budget, not an API error.
- **Live:** 14585 (status.json 00:44Z, restoration_matched; no human activation). Monitor 00:51Z (ranked, post-m2):
  since activation −0.024 [−0.049, +0.002] (1,070 / 216 series); rolling 40 −0.115 [−0.246, +0.004] (8 series),
  own-history pct 0.149 of 1,031 windows, drift flag off (hi95 > 0); Elo 1716 rank 88 (24 h 1707).
- Hub: no API/quota errors; keeper clean (errors []). git.json not pending at 00:51Z.
- Archive for D-064 §B(5): `build/daichi/ls1/16979-asahi-05-kz12-k16.zip`, sha256 585183301571e34d….

## Next unit

1. Read BOARD after 1099 (did the keeper pass succeed? anything on LS-1 / k16).
2. LS-1: counts/faults only, via a filtered read (`jobs[].{requested,verified,unverified,runtime_faults}`).
3. **At/after 02:15Z:** cancel LS-1 via battles.json, wait for verification, read the paired report and post the D-064
   table ((1)–(4); (5) met per D-065 §B): n pairs, missing listed, paired mean with cluster 5/95, LS-1 frozen letter,
   monitor rows. If all hold: re-read the live submission id (must be 14585), check no ranked series of ours is in
   flight and that we are outside the even-hour blackout (−8/+12 min), then write submit.json
   {"candidate":"asahi-05-kz12-k16","activate":true,"by":"daichi","note":"D-064 §B / D-065 §B …"} (actuator.submit_check:
   name present → POST /submissions/16979/activate + set_control; skips blackout/in-flight checks, so check them first);
   confirm submit.done.json activated:true and the mirror shows 16979; notify the user. Then D-052 §B watch
   (difference = candidate window − last-120 reference).
4. Refresh the monitor; confirm the push.

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
