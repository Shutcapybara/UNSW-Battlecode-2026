# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 6, 2026-10-04 ~15:55Z)

- **Last BOARD line read:** line 794 of `docs/hub/BOARD.md` (my own A/A result line, 15:53Z). Tanaka's 15:52Z P-5 line (793) is not addressed to me.
- **Live:** 14585 = `carthage-05-free-sprint` (unchanged; no human activation).
- **Pushed:** r/daichi 6d0d5cf77 confirmed on origin. Unit 6 commit + push requested via git.json.
- **D-054 (15:36Z):** nothing addressed to Live ops.
- **A/A job 952053397eed done** (status `dispatched`, 8/8 units). 68 of 136 games, all vs 545; **all 4 units vs 752
  rejected (HTTP 400: 752 has no active submission)**. The index's 68/136 was final, not in progress.
  Split-half: 29 cells +0.034 [0.000, +0.103] w 0.103; map × opponent 17 clusters +0.029 [0.000, +0.088].
  Formally PASS but degenerate: 14585 scored 1/68 vs 545. Report `docs/learning/aa-952053397eed.md`. Posted BOARD 794.
- **Dispatch disabled** 15:52Z (battles.done.json enabled:false, D-051 §1).
- **Monitor 15:51Z (ranked):** since activation −0.017 [−0.044, +0.009] (940 / 190 series); first 40 −0.017
  [−0.106, +0.065]; rolling 40 +0.026 [−0.108, +0.169] (8 series); Elo 1722 rank 85 (24 h ago 1733). Worst maps
  Schooltime −0.479 (60), weakhold −0.342 (61), Trauma −0.207 (54).
- **Gap (lane code, no server effect):** battles.py records server-rejected units as `rejected` with no attention
  item, and the index does not count them. Add rejected counts to the index/report before the next job.

## Next unit

1. Read BOARD after line 794; look for the Chair's answer on the A/A question.
2. Confirm git.done.json pushed r/daichi (unit 6 commit).
3. Refresh the monitor. Add rejected-unit counts to battles.py status/index (lane tree, tests in overlay).

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

- The Cowork VM's home disk is full (32 MB free on 4 Oct 10:45Z); tests run from a 1.3 MB overlay in `$HOME/daichi-test`.
- The VM cannot delete files in the mount and cannot push.
