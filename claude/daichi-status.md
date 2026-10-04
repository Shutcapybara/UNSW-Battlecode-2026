# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 7, 2026-10-04 ~16:58Z)

- **Last BOARD line read:** line 818 of `docs/hub/BOARD.md` (my own bed-variant live read). No Chair D-record after D-054;
  D-055 (teacher-row fitting) pending. No answer yet to the unit-6 A/A question.
- **Live:** 14585 = `carthage-05-free-sprint` (unchanged; no human activation).
- **Pushed:** r/daichi 1e6bd31b9 confirmed on origin. Unit 7 commit + push requested via git.json.
- **Monitor 16:51Z (ranked):** since activation −0.018 [−0.042, +0.009] (950 / 192 series); first 40 −0.017
  [−0.106, +0.065]; rolling 40 +0.025 [−0.128, +0.190] (8 series); Elo 1721 rank 82 (24 h ago 1732). Worst maps
  Schooltime −0.480 (61), weakhold −0.329 (62), Trauma −0.194 (55). Flat vs unit 6.
- **Bed variants (Kageyama 16:10Z, Nishinoya 16:45Z):** posted BOARD 818 — live per-map on the five affected maps:
  Schooltime −0.480, Slithery −0.091, PD −0.090, Devil +0.188, QoS +0.318. No sign hidden beds per se cost us.
- **battles.py (lane tree, not merged):** `request_counts()` adds `requests` (by status) and `rejected_opponents` to
  every job in the index / job file; job 952053397eed reads accepted 16, rejected 4, [752]. Test added; 15/15 battles
  tests pass in the overlay. Needs a merge request to main + redeploy (Chair) before it is live.
- **Dispatch disabled** since 15:52Z (D-051 §1).

## Next unit

1. Read BOARD after line 818; look for the Chair's answer on the A/A question and D-055.
2. Confirm git.done.json pushed the unit-7 commit.
3. Refresh the monitor. When the Chair next merges hub code, ask that r/daichi battles.py (rejected counts) ride along.

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

Unit 6 (BOARD 794): re-run the A/A against a near-50 % opponent (which?), or close D-051 §1 on the degenerate pass?
The screen panel [545, 752, 45] has lost 752 (no active submission).
Unit 5: none. D-052 answered the rollback rule; its simulation report is posted.
Unit 2 (BOARD 12:0xZ): (a) an enable D-record for the A/A split-half job as sized above; (b) a ruling on the 7
unexplained team-7 requests (2–3 Oct; is the Windows quota runner disabled?); (c) merge r/daichi (link control).

Unit 1 (asked 10:50Z, answered by D-048 / D-050 §4):

1. **Executor mode.** Proposal: keep the executor in `shadow`; requested battles dispatch on their own authority
   (like `submit.json`) once you enable them with a D-record. Flipping the executor to live would also turn on its
   automatic experiments, uploads and promotions — not wanted under Phase 3.
2. **Exposure.** Testing a non-live candidate means activating it for seconds per unit (the server plays the active
   submission). The blackout and in-flight guards cover autoscrims, not a challenge that lands in those seconds.
   Accept, or require candidate arms on dev opponents only?
3. **Other quota executors.** Is the Windows quota runner off? A second executor posting during a temporary
   activation would have its games played by the candidate.
4. **Record number.** D-045 is taken (Antioch's learned-arm gate); the founding Phase 3 record needs D-046+.
5. **Link 14585 to carthage-05** in the hub so rollback/promotion can be done by candidate name.

## Units

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
- The VM cannot delete files in the mount and cannot push. commit.sh may exit 2 after a successful commit; check
  `git rev-parse r/daichi`.
