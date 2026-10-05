# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 16, 2026-10-05 ~02:20Z)

- **Last BOARD line read:** line 1149 before my posts (Chair 01:48Z D-068 §E, Kenma). Posted 1141–1149 (LS-1 table,
  ~01:52Z) and line 1151 (activation, 02:18Z).
- **LIVE = 16979 (`asahi-05-kz12-k16`, k = 16) since 02:13:22Z.** Activated by Daichi under D-064 §B / D-065 §B on
  Chair order D-068 (LS-1 ended early: expired at its 8 h deadline, 160/204 verified, 0 faults). submit.done.json
  activated:true; control_set 14585 → 16979 02:13:23Z; status.json active 16979 at 02:17:37Z. User notified.
- **LS-1 final (D-064 estimator, recomputed from job rows):** 75 pairs of 80 cells (5 missing, opp 98, candidate games
  on the wrong id parity: Default p0, Tower Defense p1, Islands p0, Around UNSW p1, Trophy p0); paired mean +0.080,
  opp × map clusters (40) 1,000 × seed 7 5/95 [−0.029, +0.187]; 0 candidate errors/faults; cpu max 11.10 M.
  LS-1 frozen letter HOLD. Per opp: 716 +0.233 (30), 98 0.000 (25), 347 −0.050 (20). Weakhold +0.50 (4); bed maps
  pooled −0.045 (22). Hub's own paired block clusters on 3 opponents only (+0.073 [−0.039, +0.163]); not the rule's.
- **Rollback watch D-052 §B (adopted, Chair 01:46Z "unchanged"):** after 16979's first 40 ranked games, roll back to
  14585 when mean score − expectation < −0.08 with series-bootstrap 95th pct < 0, or on any crash/DQ:
  restore.json {"previous":14585,"candidate":"asahi-05-kz12-k16","reason":…}; then BOARD + notify user.
  D-052 §B reference = 14585's last-120 ranked window. No promotion before 14:13Z (12 h rule).
- **Pre-switch monitor (01:52Z, ranked, post-m2):** 14585 since activation −0.023 [−0.048, +0.002] (1,085 / 219
  series); rolling 40 −0.044 [−0.191, +0.102] (8 series), own pct 0.435; Elo 1720 rank 90 (24 h 1704).
- Hub: no API/quota errors. Keeper merged r/daichi 377f35639 at 01:51Z.

## Next unit

1. Read BOARD after 1151.
2. Monitor: confirm the script treats 16979 as active (since_activation should restart at 02:13Z); report ranked n/40
   for 16979, mean − expectation with interval, Elo/rank; any 16979 runtime error/DQ → rollback at once.
3. At n ≥ 40 ranked: apply D-052 §B (candidate window − 14585 last-120 reference); post the result either way.
4. Redeploy question: blind fix may deploy now that LS-1 closed (D-064 §B) — still waits on Chair (H11/restart).

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
