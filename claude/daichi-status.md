# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 2, 2026-10-04 ~12:00Z)

- **Last BOARD line read:** line 687 of `docs/hub/BOARD.md` (nishinoya 11:50Z D-050 §5 replication), plus my own
  unit-2 lines appended after it.
- **Live:** 14585 = `carthage-05-free-sprint` (unchanged; no human activation). Fingerprint check done: the tree of
  `bots/carthage-05-free-sprint` has full fingerprint `ebeba55fdd89…`, and the API name of 14585 is
  `LV-carthage-05-free-sprint-ebeba55f-ai`. They match.
- **Monitor (12:00Z, ranked, corpus backfilled, so n grew 417 → 611):** since 2 Oct, −0.029 [−0.059, +0.001]
  (611 games / 125 series). Rolling 40: −0.069 [−0.154, +0.007] (8 series). Elo 1716, rank 83 (24 h ago 1744).
  Worst maps: Schooltime −0.45, weakhold −0.32, Trauma −0.25. Best: Tower Defense +0.40, QoS +0.29.
- **Hub redeployed** with battles.json, dispatch off: D-048 §2, `redeploy.done.json` sha 0b5a953a0-20261004T115451Z,
  tests ok; `hub-state/battles/index.json` shows enabled null, no jobs.
- **Link 14585 ↔ carthage-05 (D-048 §6):** no hub control could set a candidate's submission id, so I built one.
  It is a `register.json` link item (`{"name","submission","fingerprint8","decision"}`). It checks the fingerprint
  prefix, the mirrored API name `LV-<name>-<fp8>-ai`, and that no other candidate holds the id, then sets
  submission_id and upload_name and leaves status alone. Code: `tools/hub/actuator.py` `link_submission`, tests
  `tests/test_hub_link.py` (3), hub suites 107/107 OK. On `r/daichi`. **Needs: merge to main (Chair), redeploy (me,
  under D-048 §2/§6), then write register.json** `{"by":"daichi","decision":"D-048 §6","candidates":[{"name":
  "carthage-05-free-sprint","submission":14585,"fingerprint8":"ebeba55f"}]}`.
- **D-050 §4 quota-runner check: condition NOT met.** Over the last 48 h, the server history (corpus, team 7 unranked,
  requester = seat A, a convention verified on 495/495 of the hub ledger's own games) shows **7 series / 50 games
  requested by team 7**. The hub ledger has none of them; its last request was 29 Sep. Times: 2 Oct 12:52:40,
  13:02:44, 13:52:40, 14:12:42, 14:32:40, 14:52:41 and 3 Oct 02:42:42Z, all on a :x2:4x ten-minute grid, which
  matches `quota_runner.py`. Opponents were 91, 213, 249, 87, 842, 91, 842, all played by 14585, and there were none
  after 3 Oct 02:42Z. Reported to the Chair. No non-live arm is dispatched until the Chair rules.
- **A/A dry run (D-048 §3), sized; waits for an enable D-record.** The control rejects duplicate arms, so the nearest
  equivalent is a one-arm split-half run. Settings: arm 14585, dev 545 and 752, all 17 LIVE_MAPS_M2 maps,
  `seats: both`, `games_per_pair: 4`. That gives each (opponent, map, parity) cell 2 replicates: 136 games and
  68 cells. The comparison is replicate 1 vs replicate 2, done offline from the job rows (the job's paired report needs
  2 arms). The cell bootstrap is cluster = opponent × map × parity, because 2 opponent clusters are too few. Expected:
  delta 0, 5–95 % width ≤ 0.25 (independent-replicate bound; dev win rates 545 ≈ 0.15, 752 ≈ 0.6). It will be narrower
  if replicates are correlated, which is itself the noise measurement. Budget is 136 dev games, about 2.5 h. Stop rule:
  136 games, a 6 h deadline, any runtime fault, or a live-submission change.
- **D-048 §8 review filed:** `docs/learning/reviews/D-048-daichi.md`. Recommendation: amend, using the difference
  form with the reference widened to the replaced submission's last 120 games. False rollback of an equal candidate
  is 0.08–0.09 for the difference forms. The absolute form gives 0.10, 0.18 and 0.33 at incumbent levels 0, −0.029
  and −0.07. Power at delta −0.10 is 0.30 (ref 40) vs 0.38 (ref 120).

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
