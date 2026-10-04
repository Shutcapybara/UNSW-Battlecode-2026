# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 1, 2026-10-04 ~11:00Z)

- **Live:** submission 14585 = `carthage-05-free-sprint` (D-043; live since 2 Oct 04:22Z; hub `control_owner = teammate`).
  The hub's candidate row for carthage-05 has no submission id, so its fingerprint is not linked to 14585 in the
  mirror — needs the Chair/hub to link it before a rollback-by-name is possible. Rollback path that works today:
  `restore.json {previous, candidate, reason}` (activates `previous` only if `candidate` is what is live).
- **Ranked (live.md, corpus + ladder snapshots, ranked only, score − Elo expectation, series bootstrap 5th/95th):**
  since 2 Oct: −0.037 [−0.079, +0.003] (417 games / 87 series); **rolling last 40: −0.093 [−0.184, −0.002] (8 series)**;
  Elo 1744 → 1716 in 24 h, rank 82. Worst maps: Schooltime −0.45, weakhold −0.30, Trauma −0.26 (the queen maps);
  best: Tower Defense +0.37, QoS +0.23. This is drift of a long-standing incumbent (the field adapting, C8-01), not a
  rollback case: the rollback rule binds a promoted candidate's first 40 ranked games.
- **battles.json built** (`tools/hub/battles.py`, actuator hook, 14 tests; 109/109 hub gate tests pass incl. the new
  module). Dispatch is **off** until the Chair enables it with a D-record (`{"action":"enable","by","decision"}`).
  Not yet redeployed: the code must reach `main` first (redeploy snapshots the main checkout's `tools/hub`).

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

## Open questions for the Chair (asked once, BOARD 2026-10-04)

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

- 2026-10-04 ~11:00Z unit 1 — read macro, prompts, D-041–D-045, hub docs, actuator/executor/quota code, BOARD tail.
  Built `tools/hub/battles.py` + actuator hook + config pacing + `tests/test_hub_battles.py`; built
  `tools/daichi/live_monitor.py` → `docs/learning/live.md`. Committed to `r/daichi`; push requested.
  Next: on Chair answers → enable/merge/redeploy; hourly live.md refresh; rosters (style row waits for Data's
  top-team pages).

## Known environment issues

- The Cowork VM's home disk is full (32 MB free on 4 Oct 11:00Z); tests run from a 1.3 MB overlay in `$HOME/daichi-test`.
- The VM cannot delete files in the mount and cannot push.
