# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 5, 2026-10-04 ~14:55Z)

- **Last BOARD line read:** line 769 of `docs/hub/BOARD.md` (tanaka 14:50Z P-2 revision HOLD). No line posted this unit.
- **Live:** 14585 = `carthage-05-free-sprint` (unchanged; no human activation).
- **Pushed:** r/daichi 8076332ae is on origin (unit 4 push confirmed).
- **D-053 (14:28Z):** R0 passed; D-052 §E withdrawn as a gate item (variants can't be rebuilt), but variants are "read
  from live games" — the monitor's split stays. Chair cites my split (cage open −0.515 / closed −0.436) to park cage
  work. Nothing addressed to Live ops for action.
- **A/A job 952053397eed (D-051 §1) running:** 14:50Z 68/136 requested, 68 verified, 0 runtime faults, 0 unverified;
  deadline 18:54Z. Analysis when done: delta = replicate 1 − replicate 2 per (opponent, map, parity) cell, cell
  bootstrap 1,000 × seed 7, 5th–95th. Pass = 0 inside and width ≤ 0.25. Report n, delta, interval, missing (listed,
  not counted), runtime faults; map × opponent clusters (D-052 §C) as sensitivity. **Then write `battles.json`
  {"action":"disable","by":"daichi","decision":"D-051 §1"}.**
- **Monitor 14:50Z (ranked, inputs 6a317179):** since activation −0.018 [−0.044, +0.010] (925 / 187 series); first 40
  −0.017 [−0.106, +0.065]; rolling 40 +0.027 [−0.103, +0.165] (8 series); Elo 1721 rank 80 (24 h ago 1742). Worst maps
  Schooltime −0.478 (58; open4 −0.519 / template −0.440), weakhold −0.342 (61), Trauma −0.207 (54); best Tower Defense
  +0.362, QoS +0.315.
- **Style roster filled** (`STYLE` in live_monitor.py from Kageyama top-teams.md v1): 306 invalid-move cull, 264
  suicide cull, 213 keeper, 952 split-heavy/sonar-silent → +0.171 [+0.043, +0.299] (15 games / 3 series; small n).
  Note: the regression roster is selected on score − E > 0, so its mean is biased upward by construction (descriptive).
- **Unexplained team-7 requests (D-051 §3):** not re-checked (no non-live dispatch). Re-run before any.

## Next unit

1. Read BOARD after line 769. Confirm git.done.json pushed r/daichi (unit 5 commit).
2. Follow job 952053397eed; on completion (or 18:54Z deadline) run the split-half analysis, post it, disable dispatch.
3. Refresh the monitor.

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
