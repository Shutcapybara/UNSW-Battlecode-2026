# Daichi — Live ops (Phase 3), Claude Opus 5.5

Lane `daichi`, branch `r/daichi`. Host: the Mac through the Cowork VM (no API key here; every server action goes through
`hub-state/control/*.json`, answered by the hub actuator on the Mac). Lane files are edited under
`build/daichi/tree/<repo path>` and committed with `build/daichi/tree/tools/daichi/commit.sh` (temp index; never touches
HEAD, the index or the shared working tree). Pushes go through the keeper (`git.json` `push_branches`).

STATUS: RUNNING

## Top — read this first (unit 8, 2026-10-04 ~17:45Z)

- **Last BOARD line read:** line 834 of `docs/hub/BOARD.md` (Nishinoya 17:52Z agreeing with Sugawara's LS-1 amendment).
  Mine: 831 (LS-1 upload + job), 832 (hub defect: server activates on upload), 834 (amendment: keep dispatching, no
  interim read, print n+/n−/n0 + sign test + opponent-submission pairing; Chair decides which rule binds).
- **D-055 (17:02Z):** live-first; §A eligibility replaces the Evaluator gate for upload/screen; §B orders LS-1 and is
  the enable; §C promotion rule; §D A/A closed. Chair 17:08Z: battles.py rejected counts merged to main 17:05Z;
  redeploy approved "to be recorded in D-056" — NOT done this unit (no D-056 yet; LS-1 first).
- **LS-1 (record `build/daichi/tree/docs/learning/ls-1.md`, committed as docs/learning/ls-1.md):**
  - candidate `asahi-05-kz12-k16`, fp 0cf975af, built from main 593810d14 into `build/daichi/stage/asahi-05-kz12-k16`
    (symlinked header resolved to main's carthage-05 blob, sha256 1c3f8974). Manifest committed on r/daichi as
    `bots/asahi-05-kz12-k16/CANDIDATE.toml`. Probe pass: max 10.6 M, round 0 ≤ 7.13 M, 0 faults, zip 3.74 MiB.
  - **uploaded 17:32:57Z = submission 16979.** The server ACTIVATED it on upload (submit_check has no restore).
    Restored 14585 via restore.json 17:40:00Z. 0 ranked games of 16979 in the hub mirror at 17:43Z — re-check the
    public corpus (`bot_a`/`bot_b` = 16979, ~17:33–17:40Z) next unit and report if any.
  - job **5ed81ad3e1f3** (204 games, arms [14585, 16979], opponents 716, 98, 347; extension 919, 351), accepted
    17:41:15Z, deadline 8 h (~01:41Z). Dispatch enabled 17:42:26Z; unit 0 (20 games vs 716) requested 17:42:34Z.
    Quota: field available 25, reserve 10 → ~1 unit per quota window; the 8 h deadline may bind before 204.
  - Cancelled job eccd265afc81 (wrong expect_active 16979).
- **Live:** 14585 (DB 17:42Z active). `hub-state/status.json` was stale at 17:38Z (showed 16979) — trust the DB /
  next status refresh.
- **Monitor 17:09Z (ranked):** since activation −0.018 [−0.044, +0.008] (955 / 193 series); rolling 40 +0.036
  [−0.108, +0.196] (8 series); Elo 1725 rank 80 (24 h ago 1732). Flat.
- **No more uploads** until submit_check restores the prior active (requested BOARD 832) or the Chair rules.

## Next unit

1. Read BOARD after line 834; look for the Chair on (a) the LS-1 amendment (Sugawara/Nishinoya), (b) the upload
   defect, (c) D-056 redeploy.
2. Check job 5ed81ad3e1f3 (`hub-state/battles/5ed81ad3e1f3.json`): games done, rejected requests, candidate faults
   (stop rule: any candidate runtime fault → cancel and report), live still 14585. No interim paired read.
3. Re-check 16979 ranked exposure 17:33–17:40Z in public_replays/corpus/index.jsonl.
4. Refresh monitor; confirm git.done.json pushed r/daichi.
5. If D-056 exists and no LS-1 unit is mid-dispatch, redeploy (`tools/hub/request_redeploy.py`, check usage).

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

- BOARD 832: submit_check must restore the prior active after upload (server auto-activates). Uploads paused.
- BOARD 834: LS-1 objective — frozen §B or Sugawara's amendment (Nishinoya agrees)? Dispatch continues unless told.
- D-056 redeploy record.

## Units

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
