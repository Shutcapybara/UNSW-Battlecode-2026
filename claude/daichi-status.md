# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 10, 2026-10-04 ~20:00Z)

- **Last BOARD line read:** line 899 (Hinata 19:50Z, R2 battery tooling) + my own lines after it.
- **Mac restart 18:48Z → hub back 19:21Z, in a terminal (not launchd). D-057 §A: NO REDEPLOY until the Chair posts that
  the hub is under a restart loop / launchd.** daemon.json heartbeat fresh at 19:50Z.
- **Built in the lane tree (not deployed):** D-056 §B `submit_check` fix (`restore_after_upload`: active read before the
  POST, re-activated in `finally` unless `activate`, never overwrites a third id; refuses in blackout / ranked series in
  flight) + `tests/test_hub_submit.py` (5 tests); D-057 §E reserve field 10 → 5 (`config.py`, `battles.py` DEFAULTS);
  job rows now carry `opponent_submission`, `request_at`, `requested_at`, `seed`. Tests: submit 5 + battles 15 +
  executor 29 pass (cloud container, Python 3.13; VM disk full).
- **Seed (Sugawara/Chair):** POST /battles takes teamId, ranked, mapIds only (docs/api); a fresh seed per game (87/87
  distinct since 17:42Z). Testing an undocumented field = server mutation, not done without a D-record.
- **Opponent submission ids are not exposed** (API payload has no submission fields since 28 Sep; replay header bot_b
  blank). D-056 §C(2) cannot be checked; every LS-1 cell's two games are in one unit (posted seconds apart) — proxy
  proposed to the Chair.
- **16979 ranked games 17:33–17:41Z: 0** (public corpus, team 7). Posted.
- **LS-1 job 5ed81ad3e1f3:** 60/204 requested (units 3/12), 40 verified, 0 runtime faults, expect_active 14585. All
  19 deferrals since 17:42Z are quota/field (available 25, reserve 10, need 20); dispatches 17:42, 18:44, 19:45Z.
  8-hour stop = 02:15Z (D-057, hub uptime). Look 1 at 102 pairs or the stop (≥ 60 pairs). No running paired figures
  quoted (D-056 §C.7).
- **Live:** 14585. Monitor 19:52Z (ranked): since activation −0.018 [−0.043, +0.009] (990 / 200 series); rolling 40
  −0.026 [−0.142, +0.109] (8 series); Elo 1723 rank 82 (24 h ago 1735). Flat; no trigger.

## Next unit

1. Read BOARD after my 20:0xZ lines; look for (a) the Chair's hub-under-launchd post → merge request + redeploy of the
   tree changes (check `request_redeploy.py` usage), (b) a ruling on the opponent-version proxy, (c) TD-1 starts after
   LS-1's first look (D-056 §B) — not before.
2. Job 5ed81ad3e1f3: games, rejected requests, faults (stop rule: any candidate runtime fault → cancel and report).
3. At the stop (02:15Z) or 102 pairs: look-1 report per D-056 §C (n+/n−/n0, cluster sums, non-zero clusters, cluster
   sign test p ≤ 0.075, frozen D-055 §B verdict).
4. Refresh the monitor; confirm the push of r/daichi.

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

- Redeploy of the submit_check fix + reserve 5: waits on the Chair's launchd post (D-057 §A).
- Opponent-version proxy for D-056 §C(2) (same unit) — asked 20:0xZ.

## Units

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

- The Cowork VM's home disk is full (7.5 MB free at 16:55Z). Build the test overlay in `$HOME/daichi-test` (tools/hub,
  tools/*.py, tests/test_hub_*.py + lane overrides, ~2 MB), run `python3 -m unittest` (no pytest), then `rm -rf` it.
  The full hub suite hits "disk full" in one executor test and an import mismatch in test_hub_analysis_a1 (env, not code).
- The mount refuses symlinks (a tar extract left an unreadable entry; moved to build/daichi/tmp/_old/). Materialise
  bots with `git show` per file. No unswbc in the VM (python < 3.11): CPU probes run in the cloud container
  (pip install unswbc==1.2.9; stage the bot, opponent and maps).
- The VM cannot delete files in the mount and cannot push. commit.sh may exit 2 after a successful commit; check
  `git rev-parse r/daichi`.
