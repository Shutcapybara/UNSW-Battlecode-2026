# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 3, 2026-10-04 ~12:57Z)

- **Last BOARD line read:** line 713 of `docs/hub/BOARD.md` (tanaka 12:52Z P-2 repair audit). My 2 unit-3 lines follow
  it (12:57Z), ending at line 715.
- **Live:** 14585 = `carthage-05-free-sprint` (unchanged; no human activation). **Linked in the hub** (D-051 §2):
  register.done.json 12:53:39Z, DB row submission_id 14585, upload_name `LV-carthage-05-free-sprint-ebeba55f-ai`.
  The mirror `hub-state/candidates.json` (12:52Z) predates the link; the next refresh should show `submission: 14585`.
- **Hub redeployed** 12:52Z: `redeploy.done.json` sha 8988d9489-20261004T125209Z, tests ok (link item live).
- **A/A job 952053397eed (D-051 §1) running.** Dispatch enabled 12:53:44Z (battles.done.json). Job accepted 12:54:50Z:
  arm 14585, opponents 545 + 752, 17 server maps by name, seats both, games_per_pair 4 → 8 units / 136 games,
  deadline 18:54Z, expect_active 14585. At 12:55Z: open, 0 requested.
  Analysis when done: delta = replicate 1 − replicate 2 per (opponent, map, parity) cell from the job rows (order of
  play within a cell decides the replicate), cell bootstrap (cluster = opponent × map × parity), 1,000 × seed 7,
  5th–95th. Pass = 0 inside and width ≤ 0.25. Report n, delta, interval, missing games (listed, not counted), runtime
  faults. **Then write `battles.json` {"action":"disable","by":"daichi","decision":"D-051 §1"}** (enable covered one job).
- **D-051 §4 done** on r/daichi: `rating_at` no longer borrows a later snapshot (game before first snapshot → no
  expectation; 40 ranked games in the 14-day window are now excluded). Every monitor run writes frozen inputs to
  `docs/learning/live-inputs/<UTC>-<sha8>.json.gz` (≈60 KB; sha256 of the uncompressed JSON). Commit only the ones
  behind published numbers (move older unpublished ones to build/daichi/tmp/_old/).
- **Monitor (12:56Z, ranked, inputs sha 2be3ac55):** since 2 Oct −0.022 [−0.053, +0.007] (690 / 140 series); first 40
  −0.052 [−0.204, +0.071]; rolling 40 −0.006 [−0.092, +0.065] (8 series); Elo 1720 rank 81 (24 h ago 1738).
  Worst maps: Schooltime −0.47, weakhold −0.35, Trauma −0.19. Best: Tower Defense +0.41, QoS +0.30. Regression roster
  +0.108 [+0.066, +0.151] (298 / 60). Style roster still empty (no `docs/learning/top-teams.md`).
- **Unexplained team-7 requests (D-051 §3):** none since 3 Oct 02:42Z (corpus to 12:42Z). The non-live-arm rule is now:
  D-046 §4 gate passed + no unexplained request in the previous 24 h + re-check before each unit, pause on a new one.
  Re-run the check (unranked games with team_a = 7 whose game id is not in the hub `games` table) before any
  non-live dispatch. D-051 §3 says the lead is told once without a request to act; noted in this unit's run summary.

## Next unit

1. Read BOARD after line 715: D-052 (rollback reference, interval convention, P-2 gate) after 13:00Z.
2. Follow `hub-state/battles/952053397eed.json` / index.json; on completion (or stop rule) run the split-half
   analysis, post the result, disable dispatch.
3. Refresh the monitor; confirm candidates.json mirror shows 14585 linked.
4. Fill the style roster once Data's `docs/learning/top-teams.md` exists.

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

Unit 3: none new (D-051 answered unit 2's three). Awaiting D-052.
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

- The Cowork VM's home disk is full (32 MB free on 4 Oct 10:45Z); tests run from a 1.3 MB overlay in `$HOME/daichi-test`.
- The VM cannot delete files in the mount and cannot push.
