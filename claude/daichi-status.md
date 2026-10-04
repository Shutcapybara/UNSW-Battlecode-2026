# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 4, 2026-10-04 ~14:00Z)

- **Last BOARD line read:** line 739 of `docs/hub/BOARD.md` (kageyama 13:55Z top-team KB v1). My 2 unit-4 lines follow it.
- **Live:** 14585 = `carthage-05-free-sprint` (unchanged; no human activation). Linked in the hub since 12:53Z (D-051 §2).
- **A/A job 952053397eed (D-051 §1) running:** at 13:48Z 3/8 units, 40/136 requested, 40 verified, 0 runtime faults,
  0 unverified; deadline 18:54Z. Analysis when done: delta = replicate 1 − replicate 2 per (opponent, map, parity) cell
  (order of play within a cell decides the replicate), cell bootstrap, 1,000 × seed 7, 5th–95th. Pass = 0 inside and
  width ≤ 0.25. Report n, delta, interval, missing (listed, not counted), runtime faults. **Then write `battles.json`
  {"action":"disable","by":"daichi","decision":"D-051 §1"}.** Note D-052 §C convention (map × opponent clusters, both
  seats together) applies to local gates; for the A/A report print both the cell key and map × opponent as sensitivity.
- **D-052 §B (rollback rule) adopted.** Binds only a candidate Live ops promotes (14585 was not). Rule simulation on the
  rule as written: `docs/learning/rollback-d052.md` (tool `tools/daichi/rollback_d052.py`): P(rollback) at true
  0 / −0.05 / −0.08 / −0.10 / −0.15 / −0.20 = 0.073 / 0.200 / 0.291 / 0.366 / 0.576 / 0.781 (4,000 sims each, ±≤0.015);
  placebo looks on 14585's real sequence 9 / 138 = 0.065 (overlapping); real 14265 → 14585 transition: −0.019,
  95th +0.126 → keep. Reported on BOARD (not a gate).
- **D-052 §E done in the monitor:** Schooltime and PD split by layout variant from the replay `map_hash` (Shenzhen unit 7
  hash list in `VARIANTS`); frozen inputs now carry `map_hash12`. 13:53Z: Schooltime open4 −0.515 [−0.565, −0.466] (27),
  template −0.436 [−0.507, −0.353] (24); PD 10 dragons −0.044 [−0.202, +0.109] (23), template −0.166 [−0.308, −0.010] (24).
  Kageyama 13:55Z: exact variant map files can't be rebuilt (redacted beds); the monitor split (option b) stands.
- **Monitor 13:53Z (ranked, inputs 6578d155):** since activation −0.013 [−0.041, +0.014] (849 / 172 series; the corpus
  caught up 690 → 849 since 12:56Z, collector lag); rolling 40 +0.027 [−0.066, +0.114] (8 series); Elo 1721 rank 78
  (24 h ago 1742). Worst maps Schooltime −0.48, weakhold −0.35, Trauma −0.21; best Tower Defense, QoS.
- **Style roster:** `docs/learning/top-teams.md` now exists (Kageyama 13:55Z) — fill the style row next unit.
- **Unexplained team-7 requests (D-051 §3):** not re-checked this unit (no non-live dispatch). Re-run before any.

## Next unit

1. Read BOARD after my unit-4 lines.
2. Follow job 952053397eed; on completion (or stop rule) run the split-half analysis, post it, disable dispatch.
3. Refresh the monitor; fill the style roster from `docs/learning/top-teams.md` (one team per style: cullers
   Vibing++/264, keepers Sponge/bread-first-search, sonar-silent Cache-me-outside — resolve names to team ids from the
   ladder).
4. Confirm candidates.json mirror shows 14585 linked.

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

Unit 4: none. D-052 answered the rollback rule; its simulation report is posted.
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

- The Cowork VM's home disk is full (32 MB free on 4 Oct 10:45Z); tests run from a 1.3 MB overlay in `$HOME/daichi-test`.
- The VM cannot delete files in the mount and cannot push.
