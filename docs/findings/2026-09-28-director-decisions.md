---
id: F-20260928-director-D001-D006
author: claude/director/session-01Nu
kind: decision
title: Director decisions D-001 to D-006 (first director turn, 28 Sep 2026, 08:30-09:30 UTC)
task: 
supersedes: 
evidence: ["LIVE/state/runner_status.json@08:33Z", "LIVE/state/state.json events 08:13Z-08:50Z", "experiment_data/bot-ratings/latest.md@08:36Z", "claude project note jks-self-audit-status.md", "maps/*.map"]
---

Each decision states what changed, why, the evidence, what it supersedes, and the falsifier that would revert it.

## D-001 — Scope of the ten-minute service on day one

**Changed:** the hub is built and run in *observer mode* first (600 s cycle: import the legacy record, shadow
re-derivation of verdicts, queue scoring, diagnostics, ranked exposure, tick and two-hour packet, repository mirror,
legacy keep-alive); the legacy worker stays the only live executor. Cutover of dispatch (protocol v2, executor lease,
per-experiment control) is deferred until the shadow checks stay clean for a day and the migration tests exist.
**Why:** neither the cloud container nor the Cowork Linux VM can reach `game.battlecode.au` (proxy 403 from both), so
every API action must run on the Mac; the legacy system has 50 passing incident-derived tests and works; the brief's
one-session build-and-cutover timeline is not credible for a system that has to hold the live credential.
**Supersedes:** Part B §14's T+1:40 cutover. **Falsifier:** the observer disagrees with a legacy verdict on re-derivation,
or the legacy worker stalls in a way the keep-alive cannot repair; then cutover is pulled forward.

## D-002 — Legacy candidates and the confirmation panel

**Changed:** registered `local-tidus-t02-spread-only` (priority 420) and `local-yuna-v03-core` (410) as legacy
candidates; did **not** register `gavroche-v32-supported-divecap`; replaced the legacy confirmation panel
[306, 20, 213, 798, 87, 130, 221, 262, 91, 46, 70, 507] (top-heavy) with 6 band + 3 rivals + 3 strong from the 08:13 UTC
ladder: [853, 241, 481, 473, 133, 30, 193, 262, 130, 306, 213, 157], disjoint from the screen panel [62, 45, 470].
**Why:** tidus-t02 tops the local table (86.1 %, sparse, 86 fixtures, 13 opponents, 10 maps) with no live evidence for
its lineage (diversity 1, coverage 1); yuna-v03's author reports +11/63 and +17/89 paired vs host while the campaign
model puts it below v02 (70.0 % vs 76.6 %), a disagreement a live screen settles; gavroche-v32 already has live
evidence as 8411 (9–21 public, max 96.6 M points, 3.4 % from the cap) and re-testing it violates the ledger rule.
The rating is decided by band opponents (ranks 68–84), not by the top ten.
**Supersedes:** Part B §14 T+0:20's `gavroche-v32` option; the legacy config panel. **Falsifier:** if band opponents
refuse or idle out (exclusions), re-derive from `/ratings` with activity as a filter.

## D-003 — Bridge patch to the legacy controller (control-following candidates)

**Changed:** three additive edits to `LIVE/system/controller.py` (backup `LIVE/state/controller.py.orig-1790585069`):
(1) after adopting an external incumbent, re-parent registry entries with `control_policy = "current"` to the new
control, save the registry, touch `state/runner.renew`; (2) an incumbent/plan mismatch requests a fresh plan and exits
0 instead of raising (the adoption and freezing already happened in `refresh()`); (3) an active/expected mismatch at
end of cycle with no open `switch`/`upload`/`intent` is adopted on the next cycle instead of raising. Candidates
without `control_policy` keep the legacy behaviour exactly.
**Why:** four incumbent changes by teammates between 06:33 and 08:41 UTC; each killed the controller (exit 1 →
`needs_review`) and orphaned the queue; the 08:13 change left the loop dead for 28 minutes with quota idle, and the
08:41 change orphaned the two candidates registered eleven minutes earlier. This is the brief's §6.4 behaviour
implemented in the smallest possible form.
**Supersedes:** the legacy "stop and wait for review" on external changes. **Falsifier:** any case where the
controller adopts a change while one of its own transactions is open (it must still raise there — see edit 3's guard).

## D-004 — Screens are the live evidence tier until the team agrees a testing window

**Changed:** the director treats a passed 60-game screen as the strongest live evidence obtainable today; no
confirmation is expected to complete. **Why:** a v1/v2 confirmation needs ≈ 7 executor-hours of an unchanged control;
the incumbent changed four times in two hours. **Falsifier:** 12 hours without an external activation.

## D-005 — The next-generation bot is a policy-layer rewrite on a hand-written host, with a 2×2

**Changed:** the S1 prompt (`docs/hub/prompts/2026-09-28-S1-swarm-dissolve.md`) asks for the swarm-dissolve policy to
be built on `ouroboros-v10-beacon` (or the gavroche/yuna-v02 host), not on `ouroboros-m01-vibing-mimic`, and requires
the production × dissolve 2×2 on seeded live-pool fixtures. **Why:** the mimic is a 1.6 MB boosted-tree imitation with
no explicit value function that under-produces and misses the r320 conversion (its own README); the self-audit showed
earlier conversion alone is null-to-negative (−1.3 / −6.4 pp) because production stops earlier. **Supersedes:** Part B
§9.4 / Part C §C.7's "production base". **Falsifier:** an S1 built on the mimic that passes the gate.

## D-006 — Portal explorers are a hypothesis (H-portal), not a role

**Changed:** the user's portal-explorer idea enters the framework as an option with a birth-certificate role
`portal_probe` and a report packet, tested as the third arm after (1) sonar echo ranging through portals and
(2) probabilistic entry. **Why:** bifrost 8540's public record is strongest on the portal-dense maps (Portals 11–5,
20 pairs; Schooltime 10–3, 12 pairs) and weakest on compact maps with few or no portals (Default 5–9, Devil 7–11 with
0 portals, Trophy 7–11 with 1); all 1,005 JKS friendly head-ons happened at portal exits, which exit memory and the
echo probe address without exploration. **Falsifier:** an arm that gains ≥ +5 pp paired on Portals/Schooltime/Default.

## Recorded facts that differ from the brief

- Incumbent at 08:33 UTC was 9943 "Heimdall v10" (teammate, Python), not 9663; by 08:41 it was 9663 again.
- The legacy controller had crashed at 08:13 UTC; `needs_review`; no requests since. Revived 08:44 UTC.
- Codex placed `state/runner.stop` at 08:51 UTC while stopping its session; the file was removed by the director at
  08:53; the running worker had already read it and will exit after its preflight; the hub's keep-alive (or the
  bootstrap script) restarts it.
- `local-tidus-t02-spread-only` passed the local runtime gate (Schooltime A 73.3 M / 52.5 M; Portals B 70.8 M / 54.0 M),
  was uploaded as 9980 `LV-local-tidus-t02-spread-only-2b8331b2-ai` at 08:50 UTC and has 20 dev games queued.
- No scheduled tasks exist under this Claude account; the Codex heartbeat is separate and now stopped.

## D-007 — Repository hygiene is automated under a stated policy

**Changed:** `tools/hub/gitkeeper.py` (run by the hub actuator every 3 h and on demand) commits quiet, parseable,
whitelisted paths with `[hub-git]` messages, merges `origin/main` with ordinary merges, stops on conflict, pushes when
clean; never stages wholesale, never deletes, never rebases or forces. Policy in `docs/hub/OPERATIONS.md`.
**Why:** the user asked for a semi-regular git process they do not have to run; the working tree carried 17 untracked
bot snapshots and run files from four lineages. **Falsifier:** a `[hub-git]` commit that breaks a teammate's checkout
(then `quiet_minutes` rises and modified tracked files are excluded).

## D-008 — Incomplete API payloads are missing fields, never losses (legacy harvest patch)

**Changed:** `LIVE/system/controller.py::harvest` (backup `LIVE/state/controller.py.orig-1790589489-D008`): a completed
game whose `/api/v1/battles/<id>` payload carries no `submissionAId`/`submissionBId` (observed for game 474236 at
09:33 UTC: status completed, winner and scores present, no submission ids, no replayKey) is stored as an unverified
row carrying the *requested* submission and `error = "incomplete API payload: no submission ids"`, and is re-fetched
on every harvest until the payload completes. Previously the controller crashed (`KeyError`, then a `None` sort in
`report()`), stopping all dispatch. **Why:** Part B §0 rule 5 (missing fields block conclusions, never count as
losses) and the loop must not die on one odd payload. Under protocol v1 the affected block is excluded and replaced
(legacy rule, unchanged). **Falsifier:** a payload that later completes with a submission different from the one
requested — then it is a `captured_mismatch`, which the verified path already handles.

Also recorded: the 470 screen block paired zero of ten maps because the server dealt the opposite starting layout
(map-hash) in every candidate game; the legacy fill logic (alternating arms, ≤ 6 fills) handles it, at the cost of
field quota. Layout assignment is not under our control and not random-looking (0/10 vs 9/10 and 8/9 in the other
two blocks) — a question for the calibration stream.

## D-009 — Failure triage: the executor retries transient failures and stops only on real ones

**Changed:** legacy controller: bounded retries for read-only API calls; per-game harvest isolation; robust report;
exit code 3 for transient-class failures with no open transaction. Legacy runner: back-off and retry on exit 3, stop
after three in a row, `runner.restart` between jobs. Hub daemon: honours restarts, auto-clears transient reviews
(≤ 3/h), notifies the rest. 52 legacy tests (50 + 2 new) pass on the patched code. **Why:** the user asked for
robustness; the controller's fail-stop-on-anything design turned every API oddity (external activation, a payload
without submission ids) into hours of idle quota until a human cleared it. **What stays fail-stop:** anything with
an open upload/switch/intent, reconciliation failures, duplicate/identity conflicts, rule violations (map roster,
decision rules, team id). **Supersedes:** the "every controller failure needs review" rule of the legacy RUNBOOK.
**Falsifier:** an auto-cleared failure that repeats three times within an hour is a real defect (the cap stops the
loop and pages the director); an auto-resume with an open transaction would be a bug in the guard.

## D-010 — Live-versus-offline calibration runs every cycle; expectations are shrunk to the live band until it earns trust

**Changed:** `tools/hub/calibration.py`: each cycle maps live sources to repository bots (legacy fingerprint),
reads the shared local ledger on the ten live maps, stores `absolute` rows (local share vs live field share, per
source) and `paired` rows (local common-cell delta vs live block delta, per running experiment), fits
`live = a + b·local` over sources with ≥ 20 live and ≥ 30 local games, and prints an expected live share for every
queued candidate. With fewer than five such sources the model is the **band mean**: the expected live share of a
candidate is the mean live share of our sources (0.41 today) whatever its local number. **Why:** the first four
comparable sources disagree by −2, −5, −16 and −32 pp (local overstates live in three of four), so a local number is
not yet an expectation. **Falsifier:** five or more sources with a residual SD below 8 pp — then the linear model
replaces the band mean and the local score may enter the priority score.

## D-011 — Lost battle acknowledgements are reconciled by exact identity, not parked for a human

**Changed:** `LIVE/system/controller.py::reconcile_battle_intent` (backup `controller.py.orig-*-D011`): an open
`POST /battles` intent is matched against the server's recent series (our requester ids, ±5–15 min window,
opponent, submission, game count, map); exactly one match → the game ids are attached to the reservation; none after
ten minutes → the reservation is released; ambiguous → still stops for review. The runner (on restart) also launches
recovery when only an intent is open. 56 legacy tests pass. **Why:** at 10:23 UTC a fill batch's POST returned HTTP
502 with the candidate already restored; the legacy design parked the whole loop for a human ("never automatically
repeated" — still true: nothing is re-posted), and the loop sat idle 84 minutes. **Falsifier:** a reconciliation that
attaches ids the server later shows under a different requester (then identity matching needs the series id).

## Audit — has the A/B system changed the live bot? (12:00 UTC)

No. Every change of the live submission on 28 Sep was a teammate's manual activation: 9508 → 9808 (06:33) → 9663
(06:48, a JKS upload chosen by a teammate) → 9943 Heimdall v10 (08:13) → 9663 (08:41) → 9508 (11:47). The system's
verdicts to date: 8540 `reject_screen` (−2 net over 30 pairs vs 9508), 9639 `reject_screen` (−2 net), 9663 vs 9508
`superseded_by_external_activation` after one block, 9980 vs 9663 `superseded_by_external_activation` at 11:47 with
block vs 45 at −0.11 over 9 pairs, block vs 62 excluded (incomplete payload), block vs 470 unpaired (opposite layouts).
No confirmation has ever opened; no promotion has ever happened; no candidate has been "kept". The system has
correctly declined two candidates and been interrupted four times.

## D-012 — Replace the legacy executor with the hub executor (protocol v2), by staged cutover

**Changed:** the mutation path moves from `LIVE/system/controller.py` to `tools/hub/executor.py` (design and failure
matrix in `docs/hub/EXECUTOR_V2.md`): reconciling stateless cycles, durable intents with identity reconciliation,
unknown-tolerant harvest, re-queue on control change, honest block completion, ranked-exposure guard, server-derived
quota, protocol v2 with fixed α. Staged: shadow (read-only, ≥ 3 clean cycles) → `cutover_mac.sh` → live;
`rollback_mac.sh` restores the legacy worker. **Why:** the user approved major changes; the legacy design's fail-stop
reflex and single-JSON state cost the team most of a day of idle quota and made promotion unreachable.
**Supersedes:** D-001's "observer only" scope; D-004's "screens are the tier" once a confirmation completes under v2.
**Falsifier:** a live cycle that re-posts a batch (duplicate series for one request) or leaves a candidate active
after its batch — either reverts to legacy by rollback and is a P0 defect.

## D-013 — Concurrent lineages: the director commits only files it owns, and the deploy gate is the hub's own tests

**Incident:** the 12:24 UTC bundle commit (D-012) force-wrote `tools/hub/analysis.py` and overwrote the A1 analysis
session's additions (loss anatomy, exact-pair contrasts, layout rule, runtime, sonar), breaking
`tests/test_hub_analysis*.py`. The A1 session recovered its own work at 12:31 into `tools/hub/analysis_a1.py` with a
lazy, exception-guarded merge in `analysis.run`/`packet_lines`; that version is adopted as-is. A restoration the
director had drafted meanwhile was discarded, not committed. `tests/test_hub_analysis_a1.py` (12:12, superseded by
`tests/test_hub_analysis.py`) still imports names that no longer exist; it is the A1 lineage's file and is left for it.
**Changed:** `bootstrap_mac.sh` gates deployment on `test_hub_core`, `test_hub_git`, `test_hub_legacy_ops`,
`test_hub_executor` (33 tests) and reports the full `test_hub_*` discovery without gating. **Rule:** the director
never commits a file whose on-disk copy is newer than its staged copy (stage, diff, then commit with the recorded
mtime); other lineages' files are never written. **Falsifier:** a hub cycle failing on an `analysis_a1` exception —
the guard in `analysis.run` is meant to make that impossible; if it happens the packet must still render.

## D-014 — The operator runs one command, once; everything else is the daemon's job

**Changed:** `executor.mode = "auto"` is the default: the daemon shadows the legacy worker and, after three
consecutive clean cycles, performs the cutover itself (stop request → drain, never forcing an open transaction →
unload the legacy LaunchAgent → adopt the record → live), recording every step. New code is deployed by request:
`tools/hub/request_redeploy.py` writes `hub-state/control/redeploy.json` with sha256 of the files; the daemon
refuses a mismatch (a device write on 28 Sep silently kept a stale `bootstrap_mac.sh`, so hashes are the guard),
runs the gate tests, snapshots `tools/hub` including `vendor/` (the previous snapshot omitted the vendored decoder,
which would have broken every harvest in the deployed daemon) and restarts itself through launchd.
**Why:** the user asked why the cutover needed them at a terminal. The only step that does is the first execution
of new code as a macOS process — the director's shells (cloud container, Cowork VM) have no `launchctl` and no API
route. Waiting for a human between shadow and live was a checkpoint by habit, not a requirement.
**Falsifier:** an auto-cutover that unloads the legacy worker while it holds an open upload/switch/intent, or a
redeploy that restarts the daemon with an open intent (both must be impossible by construction; either is P0).

## D-015 — Blocks request each map on both starting orientations; screens are 60 exact pairs

**Changed:** protocol v2 blocks are one 20-game request per arm listing the maps as `M0..M9, M1..M9, M0` (positions of
opposite parity for every map), so each arm plays both orientations of every map and a block yields 20 exact pairs
(map, side, opponent submission, layout) with no fills (`orientations = 2`, `max_fills = 0`, `min_pairs = 14`,
futility scaled to 40 % of pairs seen; `stats.paired_blocks_v2` pairs by exact cell with multiplicity). If the server
refuses a 20-map request (HTTP 400 on a request longer than the map list) the executor records `request_shape =
single`, excludes that block and continues with the legacy shape and fills. Screens are therefore 3 × 20 = 60 pairs
(120 field games); confirmations 12 × 20 = 240 pairs (480 games — see the open question in D-017).
**Why:** A1-Q3 (446 of 446 games): the starting orientation is `f(map, game-id parity)`; game ids in one request are
consecutive; a standard 10-map batch is uniform, so two arms pair on all ten maps only when their first ids share
parity — a coin flip decided by other teams' traffic, which is why 470's block paired 0/10 and the legacy fill policy
cost up to 6 batches per block. A1-Q2: a 30-pair screen rejects only at |Δ| ≳ 0.25; 60 pairs halves that.
**Falsifier:** a 20-game request whose returned ids are not consecutive, or fewer than 10 distinct (map, hash) cells
per orientation in a completed block (`hub-state/…/pairs` will show 10, not 20, exact pairs).

## D-016 — The S1 generation is closed on the v10 host; two bots are admitted as calibration probes

See `docs/findings/2026-09-28-director-S1-evaluation.md`. kazuha-s01 (priority 150) and sakura-s01 (140) are
registered below every queued candidate; chaewon-y04/y05 need manifests from their lineage; eunchae s01–s06 are
benchmarks. S2 starts from the economy on a band host (yuna-v05 / fenrir-v18 family), not from the clocks.
**Falsifier:** an S1 bot winning a live screen against 9508 at p < 0.05.

## D-017 — Statistics programme: what is adopted, what is authorised, what is deferred

Adopted from the A1 pass (Claude v2 Q1–Q10 superseding the Codex v1; GLM's findings come through the S1 bots):
1. Request shape and 60-pair screens (D-015) — deployed.
2. Probe fixtures extended to Slithery Fight (A) and Trauma (B) — deployed (A1-Q6: yuna-v02 peaked 97.5 M on the
   never-probed Slithery; the pair Schooltime/Portals missed it).
3. Local instruments do not order the queue (A1-Q4/Q10: local overstates live by 7–35 pp on 6 of 6 sources; the
   campaign table's Spearman vs live ≈ 0). Priority stays evidence-tier based; calibration keeps the band-mean
   expectation until ≥ 5 paired sources exist. D-010's "−2/−5/−16/−32, three of four" is corrected to
   "−12/−7/−14/−14/−35/−11, six of six overstate".
4. Opening stage points r25/r50 in the decoder (A1-Q1: 85–95 % of losses already trail at r100; the record's first
   stage is too late). This is a new `decoder_revision`; the legacy record is not re-decoded in place — new games
   carry the extra stages, and a one-off re-decode pass over the 446 replays is scheduled as a task.
5. Screen panel: keep 45 (band-like) and 62 (the elimination stress test); replace 470 once a band team is profiled
   (A1-Q5) — until then the screen share is not a rating proxy.
6. tidus-t02's registry hypothesis did not reproduce live (A1 memo) — its priority (420) is left for now because the
   queue is otherwise empty of measured candidates; it is not evidence of strength.

Authorised (the executor performs these when the queue allows; no human action):
(a) the judge-divergence **tap dev game** (A1-Q8 spec) — one upload of a stdin-logging bot and one dev game vs 752
on Trophy; the analysis session owns the bot, the hub runs it through the dev pool; (b) a **refetch of the four 9663
ranked series** (463004, 467153, 468473, 474275) to book the Elo cost of testing (A1-Q9); (c) the **band corpus**:
≤ 60 newest public replays for each of 790, 133, 977, 75, 19, 406, 534, 875, 473, 241 into `public_replays/band/`
(the daemon downloads through the credential path; nothing is uploaded) — these three are control requests to the
daemon (`fetch.json`) in the next revision; until then they are tasks in the hub ledger.

Deferred with reasons: the 12-block confirmation now costs 480 field games (~11 hours of the executor's cap with zero
teammate usage); a 6-block confirmation with a pair-level efficacy test (120 pairs, α = 0.025 one-sided → ≥ 71 wins)
is statistically at least as strong and half the cost, but changes the protocol the brief fixed — presented to the
user for a decision rather than taken; clones of 62/545 and teammate-upload recovery are lineage work (S2 prompt);
the autoscrim draw-semantics study waits for (b).

**Falsifier for the programme:** after five candidates under D-015, the live-vs-local residual SD on the calibration
rows is not below 8 pp (then local panels, however designed, are not a selection instrument and the queue must be
ordered by live screens alone).

## D-018 — Workshop of the A1 statistics (Claude v2): what the executor now does differently

**Changed (deployed by self-redeploy, 28 Sep 14:2x UTC):**
1. **Variable server response is a budget, not a failure.** Each cycle spends at most `snapshot_seconds` (240) on
   the server history and `harvest_seconds` (240) on replay verification; a cut-short history marks the quota
   *unknown* and nothing is requested that cycle (never over-request on a stale picture), harvest continues next
   cycle with running blocks first, and the daemon mirrors the phase it is in (`hub-state/daemon.json`). The
   ten-minute cadence is a minimum gap between cycle starts; the first live cycle took 17 minutes on the legacy
   backlog and that is now visible rather than silent. API read timeout 60 s.
2. **Stage points r25 and r50** (`decoder_revision gzip-errors-v3-r25r50`, schema 3): A1-Q1 shows 85–95 % of losses
   already trail at r100 and the record could not see earlier; the vendored decoder already records every round, so
   this is a superset of the stored snapshot, not a decoder change. The 446 legacy replays are re-decodable in place
   by a one-off pass (task).
3. **Ranked-series-in-flight guard** (A1-Q9): a candidate is never activated while a ranked series involving us is
   non-terminal in the server's recent history — autoscrims start 4–36 minutes after the even hour and other teams
   challenge at arbitrary times, so a fixed window covers only the request moment. The 8/12-minute window stays.
4. **`dev_only` candidates** (manifest flag): uploaded, dev-covered (20 dev games), then `dev_done` — never screened.
   This is how the A1-Q8 stdin-tap bot runs: the analysis session builds `bots/tap-v01` with `dev_only = true`; the
   director registers it; the executor uploads it, plays the dev games (20 replays instead of the one the spec asked
   for, at no field cost), and the analysis compares logged stdin with the rebuilt round block.
5. **Screen panel [45, 752, 62]** replaces [62, 45, 470]. 470 (rank 6) is lost by both arms (share 0.32) and yields
   few discordant pairs; 752 (dev test 2, rank 85) is band-adjacent, beaten 0.66, and played from the **dev**
   allowance, so a screen now costs 80 field games instead of 120. Confirmation panel unchanged.

**Interpretation the director takes from the A1 pass (the workshop):**
- The live loss is *one* mechanism seen from five angles: out-produced before r100 (Q1), flips are r250 material
  (Q2), no local opponent produces that pressure (Q4), runtime and sonar are not it (Q6, Q7), and the local rating
  table cannot see it (Q10). Every S1 lineage independently confirmed the same thing from the build side (D-016).
- Therefore the next build is not a strategy but an *opponent*: until the local panel contains something that
  produces 20 units by r100 and 80 total by r250 against us, local numbers select for the wrong thing. Clones of
  62/545 (lineage task) and the band corpus (authorised, Q5) are the two data items that unlock everything else.
- Testing capacity is the binding constraint, not ideas: 60-pair screens at 80 field games each, ~45 field
  games/hour executor cap, teammates' usage, and live-slot churn. The protocol is now as efficient as the evidence
  allows; the remaining lever is social (announced incumbent changes, D-004).

**Falsifier:** a first live block under D-015 with fewer than 20 exact pairs (then the two-orientation request is
not what the server does and the fallback is in effect), or a `quota_unknown` cycle that still dispatched.

## D-019 — Protocol v2.1: six-block confirmation with a pair-level efficacy test; the public corpus

**Changed (29 Sep 00:xx UTC, self-redeployed):** confirmation = 6 blocks × 20 exact pairs (120 pairs, 6 distinct
opponents from the confirmation panel, 240 field games) instead of 12 × 20. Efficacy at 6: mean paired delta
≥ +0.03, one-sided exact sign test over all confirmation pairs p ≤ 0.025 (e.g. ≥ 72 of 120 discordant pairs), at
least 4 of 6 blocks positive, no map mean ≤ −0.25, zero candidate faults. Futility interims at 3 (mean ≤ 0) and 5
(mean ≤ +0.01) blocks. A control change keeps ≥ 3 completed confirmation blocks as evidence (`superseded_incomplete`).
Experiments record `protocol_label = v2.1`. **Why:** the user asked the director to pick; 240 games is ~5.5 hours of
the executor's cap against ~11, and the pair-level test on 120 pairs is at least as strong as a block-level
sign-flip over 12 means (which needed ≥ 11 of 12 positive blocks at α = 0.025). **Falsifier:** a promoted candidate
whose probation win share falls ≥ 0.10 below its confirmation share (then 6 blocks over-fit the panel and 12 return).

**Also:** the daemon now collects a public replay corpus (`tools/hub/corpus.py`, `public_replays/corpus/`): top 30
teams, ranks 55–85, 306's whole history, the screen/dev opponents and the band teams that played us; 40 replays per
pass within 150 s, ladder snapshot per pass, header bot names per game for decoy detection (the user's suspicion
about 306). Analysis handoff: `docs/hub/prompts/2026-09-29-A2-corpus-statistics.md`. Build handoffs:
`…/2026-09-29-P1-pace-bot.md` (the user's pace hypothesis) and `…/2026-09-29-S2-economy-on-a-band-host.md`.

## D-020 — An auto-activated executor upload is restored, never adopted as the control (P0, 28 Sep 14:26 UTC)

**Incident:** kazuha-s01's upload (10357) was activated by the server on completion of its build; the executor's
control observer, which runs before upload reconciliation, read that as a teammate's activation, adopted 10357 as
the control, froze the running tidus screen (`superseded_by_external_activation`), and opened yuna-v03 vs 10357;
the same happened at 14:51 with sakura's upload 10376. Our own S1 bot was the team's live submission for roughly
half an hour, inside the 14:00 autoscrim's start window. A teammate or the server put 9508 back by 14:58. No field
quota was spent (none was available), but D-012's falsifier — a candidate left active — fired.
**Changed:** `observe_control` now recognises an active submission that belongs to an open upload transaction, or
that is a fresh executor upload (`-ai` name, a candidate's submission, uploaded within the hour), as an
auto-activation: it schedules the restore (live mode restores in the same cycle), raises `upload_auto_activated`,
and neither adopts it nor freezes anything. Regression test reproduces the sequence. The three spurious experiment
rows stand as recorded (verdicts are never rewritten); the next cycle re-opens the screen against the real control.
**Falsifier:** any future cycle whose `external_actions` names a submission the executor uploaded within the hour.

**D-020 addendum (15:08–15:13 UTC).** The first automatic repair restored 9943 (Heimdall v10, a teammate's 08:13
activation) instead of 9508, because the walk back through `external_actions` treated every registered candidate's
submission as "our upload" and skipped 9508 (registered as the legacy candidate `bifrost-v18-control`). Corrected:
"our upload" means the executor's `LV-…-ai` naming only. A director restore control (`hub-state/control/restore.json`,
`force: true` with a reason to override a non-upload activation) was added and used once: 9508 restored and set as
control at 15:13:02, before the 16:00 autoscrim. Net exposure: the team's live submission was kazuha-s01 from ~14:26
to ~14:51, sakura-s01 from ~14:51 to 15:08, Heimdall v10 from 15:08 to 15:13.

## D-021 — A running experiment whose control is no longer the control is frozen, whatever moved the control (28 Sep 16:28 UTC)

**Incident:** after the D-020 director restore (9508 back at 15:13:02) the experiment `aa8dd5be` (yuna-v03 vs 10376)
stayed `running` with `control_submission = 10376`, because `freeze_running` was only called from the *observer* on
an activation it classified as external, and the restore path set the control directly. The next-block rule waits
for `active == the experiment's control`, so from 15:13 to 16:28 the executor dispatched nothing at all (field quota
45 available the whole time; the only requests were dev coverage), while the team's rating was being decided by
autoscrims. A teammate's activation of `tyr-v01-yuna-momentum` (10413) at 15:21 was classified correctly as a
teammate upload and adopted as control — which made the stale experiment doubly stale.
**Changed:** at the top of the running-experiment step, any `running` v2 experiment with
`control_submission != control` is frozen through the existing `freeze_running` (reject if the evidence already
says so, `superseded_incomplete` with ≥ 3 complete confirmation blocks, else `superseded_by_external_activation`;
`frozen_reason = 'control changed old->new'`), and the candidate is re-opened against the real control in the same
cycle. The cycle summary now carries `ranked_recent`: our ranked series in the server's recent history (series,
opponent, our submission, W/L, Elo delta), so the packet says what the rating is actually being decided on.
Regression test: `test_running_experiment_with_a_stale_control_is_frozen_and_replaced`.
**Falsifier:** any cycle summary with a `running` experiment whose control differs from `control`; any cycle with
`quota.field.available ≥ 20`, a `dev_ok` candidate, no ranked series in flight, not in blackout, and nothing
dispatched.
**Rating context (corpus ladder snapshots, team 7):** 1754 (14:57) → 1746 (15:04) → 1701 (15:13) → 1701 (15:2x–16:0x)
→ 1691 (16:15); rank 62 → 95. The −53 fell inside the D-020 exposure window (our S1 bots and Heimdall v10 live
14:26–15:13, i.e. through the 14:00 autoscrim's start window); the −10 at 16:15 was played by 10413. That is the
cost of D-020, recorded here so it is not read as a bot regression.

## D-022 — One game per distinct map per request: block arms are posted as two waves, fills are paired (28 Sep 16:43 UTC)

**Incident:** the first v2.1 field block (yuna-v03 10013 vs Tyr V12 10473, opponent 45, 16:31 UTC) asked for 20
entries per arm (each map twice, rotated — the A1-Q3 pattern) and the server returned 10 games per arm: it creates
one game per *distinct* map in a request and does not refuse the list. Under the stored parameters (`max_fills 0`,
`min_pairs 14`) the block would have been excluded once harvested and replaced by another 40-game request every
cycle — a quota drain with no decision — and the request rows' recorded counts (20) had already halved the
executor's own hourly cap (field available 5 with 20 games in flight).
**Changed:** a block arm is two waves posted back to back inside one activation — the block's maps, then the same
maps rotated by one (`waves_of_distinct_maps(rotation(maps))`) — so consecutive ids give every map both starting
layouts and the block still has 20 exact pairs from 40 games; each wave is its own request row whose count is the
games the server created. Fills are paired: both arms request the missing maps back to back, the second arm's odd
waves led by a spare block map so the two arms' ids align on the same parity (`aligned`), which pairs whatever
layout the fill lands on; single-arm alternating fills paired only by luck and never when foreign traffic locked
the parity. Defaults: `max_fills 3`, `min_pairs 10`; running v2 experiments opened with the old values are migrated
(`params_migrated` event); accepted request counts are corrected to the games created (`request_count_corrected`).
The 400-refusal fallback to single-orientation blocks stays as dead code (no wave exceeds the map count). The cycle
summary carries `candidate_games` (requested / verified / unverified by error kind per registered candidate).
**Falsifier:** any `unexpected_game_count` after this deploy; any block with `fill_attempts ≥ 2`; any field block
whose two arms' first waves are not parity-aligned when the ids are consecutive.

## D-023 — The battle payload no longer carries submission ids or a replay key; games are attributed by the request (28 Sep 17:02 UTC)

**Incident:** every game fetched since about 14:20 UTC comes back with `match` lacking `submissionAId/BId` and
`replayKey`, and with `games[].hasReplay` instead (sample recorded in `kv incomplete_payload_sample`, game 506472).
The executor's verifier treated that as "incomplete API payload" and held the game: the S1 uploads' dev passes
(kazuha 10357, sakura 10376: 20 games each) never completed, the first v2.1 field block could never verify, and
the 131-game legacy backlog was the same thing. The last games in our record verified through API-reported ids are
yuna-v03's dev games (harvested ~14:1x). Replay downloads (`/api/v1/battles/{id}/replay`, signed redirect) are
unaffected — the corpus fetched 800+ replays through them today.
**Changed:** a game whose payload reports no submission id is attributed to the submission the executor activated
for that request (`stats.attribution = 'request'`; API-reported ids, when present, still win and a mismatch still
excludes the game); the replay is downloaded and verified exactly as before (API winner = replay winner, stages,
runtime, faults); `hasReplay: false` is the transient "replay not yet available" (re-fetched), and only a
non-completed status is an infrastructure failure. Harvest keeps re-fetching a transient game for 24 hours after
its request, every cycle for running blocks and every 30 minutes after six tries otherwise (no attempt cap for
transient errors). What is lost: the opponent's submission id (pair cells now match on opponent team) and the
observer's ranked-exposure attribution by submission (`ranked_recent.our_submission` is null).
**Falsifier:** any verified game whose replay-side runtime fingerprint contradicts the attributed submission (the
A1-Q6 runtime table per submission is the check: a candidate that suddenly "looks like" the control); any
`attribution = 'api'` game after this date (the server put the ids back — then the mismatch check is live again).

**D-022 addendum (17:25 UTC).** The 16:43 cycle, still on the pre-D-022 code, had excluded the first block
(`295b7287`, "0 pairs after 0 fills (min 14)") because its games were all fetched but none verified (D-023). Blocks
excluded by exactly that rule under a running experiment are reinstated at cycle start (`block_reinstated`); the
block's 10 exact pairs then triggered the first paired fill at 17:29 — control 509479–509488, candidate
509489–509498, consecutive ids, both arms on the odd parity, the opposite layout family to the first wave — and no
`unexpected_game_count`. Kazuha-s01 and sakura-s01 passed their dev gates (20/20 verified, no faults) once D-023
let their games verify; they queue behind yuna-v03 for screening against 10473.

## D-024 — The corpus keeps collecting after its targets are met (28 Sep 19:13 UTC)

**State at 19:06 UTC:** 1,601 replays (1.2 GB) from 68 watched teams in 4.2 hours, ~380 per hour, zero fetch
errors; 690 ranked, 688 inside autoscrim windows; 41 ladder snapshots; team-game targets 2,400 of 4,860 reached,
306 Cutlery 68 of 400 (its public history is paged newest-first, so the backfill continues). At that rate the
targets would all be met in ~6 hours and the collector would then stop, because targets were caps.
**Changed:** targets are floors. Each pass reserves 10 of its 40 downloads for *refresh*: the six least recently
checked teams already at target have their newest public page read and any new game fetched; the remaining 30 go
to the backfill as before. `teams.json` records `checked_at` per team. Cost stays ≤ 40 replays per ~6 minutes.
**First reading of the decoy question (A2-Q1), with the caveats that n is small and challengers self-select:**
as the *target* of other teams' unranked tests, rank-1 306 wins 0.53 of 64 games; the other top-six teams win
0.78–0.88 of theirs (70: 0.84 of 50; 801: 0.78 of 76; 20: 0.88; 46: 0.88; 566: 0.86). 306 lost 1–4 to rank-96 241
and 3–7 to rank-55 456 between autoscrims. Its four ranked games in the corpus are 2–2. Since D-023 the API gives
no submission ids and server replays carry no bot names, so a decoy can only be identified behaviourally from the
replay (runtime and opening fingerprints) — A2-Q1's method must change accordingly.

## D-025 — Corpus throughput: own thread, shared pacing under the key's 120/min limit (28 Sep 19:23 UTC)

The collector had been self-throttled (40 replays per 5-minute pass, inline with the executor loop, re-paging every
team's public history each pass): ~380 replays an hour. The documented limit is 120 requests a minute per key
(30 for `/leaderboard` and `/ratings`), 429 + `Retry-After` over it; a replay costs two API requests. Now: the
corpus runs in its own thread, continuously, through the one paced client every caller shares (0.55 s spacing under
a lock ≈ 109/min); it stops its pass while an executor cycle runs; any 429 pauses every caller for the server's
Retry-After (≤ 2 min) and slows the corpus to one pass per 5 min for 10 min; discovery listings are cached 30 min;
ladder snapshots are written on change. First full pass: 78 replays in 121 s, ~75 API calls/min, no 429 —
~2,300 replays an hour.

## D-026 — The screen runs on the dev allowance (28 Sep 19:40 UTC)

Team 545 is the organisers' swarm reference bot at rank 13–15 (1972) and 752 a weak one; games against dev teams
draw on a separate 60-an-hour allowance that no other team competes for and that never touches the field
allowance or the rating. Our bots win 10–30% against 545. Screen panel is now `[545, 752, 45]`: two dev blocks and
one field block (45) for calibration of dev-vs-field transfer; block quota is checked and charged on the opponent's
pool (`pool_of`), so a dev block is never deferred on the field allowance and the field allowance is left to
confirmations — roughly three times the screening throughput. Falsifier: a candidate that passes the dev screen and
fails the field confirmation twice in a row means 545 is not a proxy for the band, and the panel goes back.

## D-029 — Ares is the production line; the cx work folds into it (29 Sep 11:55 UTC)

**What came in overnight.** The teammates ported Tyr V12 to C++ on the anna-a02 runtime scaffold (`ares-v02…v04`),
proved output parity with the golden harness (168,123 turns, 5,089 dragons, zero divergences), fixed the two
`separation.py` exceptions (`ares-v05`) and restored the historical Bifröst/Skadi search profile plus a size-matched
support rule (`ares-v06`): 160 target nodes, deeper room floods, the 12-length three-step horizon — at p99 7.4 M and
max 8.6 M points a turn. On the 8-bot fixed panel V06 is 122–38 (76.3 % expected score) against V05's 118–41;
dragons at r100 +12.9 % normalised, length r100 +2.6 %, r100 pearls +4.8 %, hygiene within the 10 % guard. It was
held back only by the +0.05 economy-mean gate. C1-B (Opus) delivered the router and the ablation the same night:
on the live pool the router beats the cheap chassis on length and pearls (176/61 pairs) but not on units (p = 0.69);
on the unseen panel the pearl edge vanishes and only +2 length survives (p = 0.036); the atlas carried two thirds of
the pool gain and the mill on Dilemma/Autarky/Slithery carried the rest. **Routing is not the lever; survival is.**
It also found that `maps/pub/*_rec.map` share edges with Portals/Slithery, so the atlas matches them: they are not
an unseen test and leave the generalisation panel.

**Decisions.**
1. **Ares is the production C++ line.** It is Tyr V12's strength with the exceptions fixed and 90 M points of
   headroom; the cx chassis line is the survival-first clean room and stays as a testbed. Ares V06 (500) and V05
   (480) are registered; the hub accepts `c++` manifests and uploads with the CLI's spelling (this deploy). The dev
   screen against 545 decides; nothing is hand-activated.
2. **The gate for retention changes is the BENCHMARKS logic, not the +0.05 economy delta**: hygiene and retention
   may improve while the economy curve holds. V06's r50 dip (−0.017) is inside that; V06 passes on those terms and
   goes to the live pipeline for the field to decide. It still needs seed 2 and the unseen panel with the atlas off
   (Ares carries `atlas.hpp` from the scaffold; whether its policy consumes it must be measured, not assumed).
3. **Search depth is the next lever on Ares, not on cx.** V06 used 8.6 M of 100 M. A depth ladder (2×, 4×, 8× node
   caps and horizons under the same saturation/late guards), each rung measured on both panels with the CPU probe
   on the dense fixtures (Schooltime late game at 60 units, Slithery), finds where the curve flattens or the budget
   binds. The out-of-sample rule applies: caps key on tile count and unit count, not on the map.
4. **The cx work transfers as parts, not as a bot**: the 2-core dead-end peel and tree costing, arrival maps, the
   enclosure-aware room check (tuned not to cost pace), and the panel/atlas-off measurement discipline go into Ares
   as `params.hpp` switches; C1-F's leak fixes are re-targeted at Ares (its wall 7.7 and self 3.7 per 1k are now the
   top leaks on a proven economy) rather than at the chassis.
**Falsifiers:** Ares V06 failing the dev screen against 545 (then the local panel has been fooling us again);
a depth rung that raises the panel expected score but not the unseen-panel numbers (memorised pool); any sandbox
max over 80 M on the dense fixtures.

**D-029 addendum — C1-F read (29 Sep 12:10 UTC).** GLM's leak fixes are in (`docs/findings/2026-09-30-cx-f01-leaks.md`,
merged from `cx/f`; main's C1-B versions of `tools/cx/{arena,bench,ablate}.py` were kept where the two branches
conflicted — `benchmarks_table.py` and `cx_f_summary.py` came in intact; reconcile the tool divergence when either
tool is next touched). Verdict: **no fix passes on the chassis, because the chassis does not have the leaks** —
it transits 6 times a game where yuna transits 75 on Portals, its trapped losses are small, it never sprints
usefully. F-1 neutral (37/167/36); F-2 rejected in five configurations, all reducing to a volume throttle (steps −31 %,
deaths −30 %, per-step flat, pearls −4.4 %: the sakura trap), confirmed with the replay-level instrument; F-3
negative; F-4 never flips a decision. Two findings stand regardless: the atlas is an *economy* switch, not a safety
switch (+17 % pearls, doubled portal deaths, inert off-pool — the generalisation panel is a real gate, 35/683/26);
and gating the trapped split by room size is fatal on Slithery (it is the survival pump: 356 trapped vs 27 greedy
splits per 100 rounds). The delivered plumbing (`pair_mem`, `exit_known(pair)`, one-ray probe with echo attribution,
enclosure probe, corpse gate) is all `params.hpp` switches. **Consequence:** this is the strongest evidence yet for
D-029.4 — the leaks are in the Tyr/yuna lineage code and must be fixed there. The F-1/F-2 switches are re-tested on
Ares V06 at its real transit volume (49/game live), where C1-D's numbers say the gates pay.

**D-030 — C2-0 read: S-3 (leader-coordinated fights) is dropped; fights enter the programme as a cost, not a
protocol (29 Sep 12:55 UTC).** GLM 5.3's corpus study (`docs/analysis/C2-fight-anatomy.md`, 182,788 contact events
over 10,331 ranked games, `claude/c2-0-status.md`) finds no movement-observable coordination signature in the top
ten: fight rate (8.96 vs 8.58 group fights per side-game), pre-contact convergence (0.29 vs 0.27), synced entries
(~23 % both) and pre-fight sonar (2.7 vs 2.5 rays/head) all match the 55–85 band. The pooled +3.7 pp initiator edge
is composition: the top ten arrive ahead in units at 53.6 % of contacts vs 44.8 %, and at matched parity initiate at
the band's rate. Director's reading beyond GLM's: the "trade while ahead" separation (55.1 % vs 44.2 %) is also
mostly composition (the ahead-at-contact mix differs by 8.8 pp), and the top ten initiate *more* than the band
when behind (50.2 % vs 45.0 %), so "never trade when behind" is not supported; what survives as a behavioural
signal is the refusal of fights far from beds (initiate 38.5 % vs 54.8 % at bed distance >6, n=562) and the
post-fight material swing (+1.08 vs −0.81 pearls over the next ten rounds). Fights do not decide non-top-ten
games (win rate flat across net-kill buckets in the band and ranks 11–30). Team 7's gaps are not initiation
(48.3 % vs 49.9 %) but reinforcement (convergence 0.18 vs 0.27; 0.12 on compact maps) and cost: 11.6 own deaths and
32.9 length lost per fight against the band's 6.8 / 18.9 — the same trapped/newborn/crowd leak picture as C1-C.
**Consequences:** (1) S-3 as a messaging protocol is dropped; nothing protocol-shaped is built without a
payload-decoding study of teams that do send fight direction. (2) The fight cost lands on R-3 (leaks on Ares),
which is where twice-as-bloody fights are actually fixed. (3) Two cheap local rules go to the R-2 open lanes as
candidate mechanisms with their expected sign stated: refuse to initiate contact when the nearest observed bed is
>6 cells (expected: kill-against and own deaths per fight down, economy flat), and converge-or-refuse (do not
enter a group contact without a second own head within the window; expected: length lost per fight down).
GLM's note that these would go "on the C1-A chassis" is overridden by D-029: everything is on Ares. (4) The
parity-at-contact decomposition is the method to keep — every cohort comparison in this programme should be
checked for composition before it is read as behaviour.

**D-031 — executor to shadow: no automated uploads, game requests or activations while the teammates own the
submission interface (29 Sep 12:50 UTC, lead's instruction).** The hub executor had been live since the 28 Sep
cutover (uploads with the `-ai` suffix, unranked A/B requests, automatic promotion after confirmation). The lead's
teammates are handling the submission system by hand, so the executor now runs in `shadow`: it still harvests,
keeps the corpus, registers candidates, runs the git keeper and logs the plans it would have dispatched, but posts
nothing. Mechanism: a new control, `hub-state/control/mode.json` ({"mode": "off|shadow|auto|live", "by", "note"}),
which writes `[executor] mode` into `HUB/hub.toml` and restarts the daemon (`actuator.mode_check`, gate test
`test_mode_request_sets_hub_toml_and_restarts`; app `c52433c10-20260929T124718Z`). Registered candidates
(`ares-v05`, `ares-v06`, `ouroboros-s02-portal`) stay queued; nothing is uploaded until the mode is set back to
`live` by the same control, which is the switch to flip when systematic live tests resume. Local panels
(BENCHMARKS gate) are the only gate in the meantime.

**D-032 — the lane gate is revised: paired, multi-seed, interval-based, phase-aware (29 Sep 23:40 UTC).** Three lanes
reported against the +0.05 single-seed economy bar: Renoir (33 mechanisms, 0 accepted; best real effects +0.01 to
+0.02; the seed alone moves the same bot's economy by +0.071), Lune (the recommended search level at +0.026 with every
r100+ metric up and no hygiene cost, failing the bar because a late-phase change cannot move p@50/p@100), and Sciel
(one mechanism at +0.067, killed by a guard). Renoir's reading is adopted: fishtest works because its bound matches
patch size. The gate becomes two-tier. **Accept into a lane's stack:** paired fixtures, seeds 1–3, live pool and
generalisation panel, both seats; bootstrap 90 % lower bound of Δ(economy mean) > 0 on the pool; generalisation
Δ(economy) lower bound > −0.02; units@100 and length@100 lower bounds not < −0.02; no tier-2 rate up > 10 %; win
lower bound > −0.02; per-checkpoint deltas reported, and a change that acts only after a phase boundary is judged on
the checkpoints it can move with the earlier ones as guards. **Promote to the dev screen:** the accumulated stack
against Ares V06 at the original +0.05 (or the phase-aware equivalent), on both panels. The desktop's throughput
(~2,900 games/h) makes the 1,200-game accept test a 25-minute step. Consequences: BENCHMARKS §"How to use it" step 4
is superseded for lanes by this decision; R-4's scorecard implements the interval form; Renoir's 17a/17d/18a/18c and
Lune's late-cap level are re-scored under it before anything else runs.

**D-033 — Ares V06 carries map identity, and the lanes' base drops it (29 Sep 23:40 UTC).** Renoir found three
`policy.hpp` terms that fire only when `W == 32 && H == 16` (`devil_center_bonus`, `devil_lane_bonus`,
`ally_body_buffer`): Devil is won 16/16 with them and 17 % on the transposed Devil; they *hurt* on Prisoners
Dilemma, the other 32×16 map; Trophy likewise falls from 80 % to 17 % transposed. This is the out-of-sample rule's
case exactly. Decisions: (1) every R lane's base from now is `lune-r1-07-latecap8x-only` with those three terms
inactive (`<lane>-01-nodevil`), so lane deltas are measured on a bot that does not know the pool; (2) the finding
goes to the teammates as a Qualifier risk with a proposed structural replacement (a midline race keyed on observed
spawn geometry), which is theirs to build on Ares; (3) the ledger gets a row (L28) and the pool-vs-generalisation
gap of V06 (0.762 vs 0.524 win) is the number to close.

**D-034 — registrations and lane state (29 Sep 23:40 UTC).** `lune-r1-07-latecap8x-only` is registered for the dev
screen (priority 510, above Ares V06) — queued only, since the executor is in shadow (D-031). Sciel-03b (the
ally-saturation discount on the EW food-density memory) is the single most promising unbuilt mechanism in the
programme and is the first item in the guided lane's prompt. Lane `ra` (Renoir) is closed with its report; `sciel`
continues on the desktop if GLM is re-issued there; two new desktop lanes are issued: `rb` (Basquiat, blind — reads no
findings or ledger, an independent draw) and `rc` (Cézanne, ledger-guided). Monoco (GPT's lane) has no branch on
origin and is read when it is pushed.

**D-035 — R-3 and R-4 read; merged to main (30 Sep 00:20 UTC).** R-4 delivered all four parts on `r/r4` (tools/cx
reconciled — cx/f's multi-direction portal walk and `eaten_r*` fields restored; C++ parity incl. `meter.py --mode cxx`
and `golden.py suite`; `run_panel --panel gen` with `GEN_MAPS` and fingerprint-keyed candidate grids; the single-bot
scorecard with a `GATE:` line). R-3 delivered on `r/r3` (contains r4). Both merged with `-X theirs` on
`tools/cx/bench.py` (main's `map_name` fix re-applied by hand). R-3's reading: **Ares V06 carries the Tyr leak
profile at real transit volume** (trapped 36.1 len/1k vs top-10 18.5; portal deaths 29.4/100 steps vs 306's 12.5;
crowd23 4× the top ten) — the lineage claim holds. But every pre-entry portal rule is a throttle on Ares too
(r3-01/02: transit volume −22 %/−68 %, per-100-steps *worse*, economy −0.05/−0.12), so C1-F's result transfers; the
kelp/room surcharge (r3-04) is the strongest hygiene lever measured (wall −27 %, trapped −30 %, newborn −15 %) and
fails on economy (−0.072, −0.107 stacked); and r3-03 escape-early is a **production lever, not an escape fix**:
+5.0 pp win replicated at two seeds, economy +0.026 pooled, length +0.049, own-body +11 % (the churn of the extra
cramped splits), neutral off-pool. Sciel-02a already tested R-3's "post-transit navigation" open item (portal leak
−21 %, economy paid). Consequences: (1) R-4's scorecard becomes the lanes' gate tool and gets one more task: the
D-032 interval form and a corpse-share diagnostic (L29). (2) r3-03 is a hold under D-032 (own-body +11 % vs the
10 % guard) — the attribution to pay down is newborn churn from `ACT:tsplit` children; the guided lane may take it
after the density line. (3) The portal leak is closed as a *crossing-side* problem on both hosts: what remains is
the exits (contact and post-transit navigation), which Sciel's steering did not solve either; the ledger row for
portal fixes drops to 0.2 with that stated as the shape of any revival. (4) Every finding this phase agrees:
hygiene bought with caution costs economy one for one on this lineage; the economy levers that have appeared are
state (Sciel-03a), search phase (Lune) and production (r3-03).

**D-036 — the per-map line (30 Sep 00:50 UTC, lead's direction).** Diagnose per map, fix per structural signature,
measure globally, with a transfer test against the unseen maps that share the signature. Adds a "local hold" verdict
tier to D-032 for mechanisms whose gain transfers within a signature cluster while the pooled interval is not negative;
those become structure-gated switches (gate = observable structure, never the map) and are tested as such. Issued as
M-1 (GLM 5.3). All lanes report per-map deltas from now on so the map × mechanism table accumulates.

**D-037 — the per-map, per-phase programme: optimise the opening per map aggressively and measure what it costs
(1 Oct 00:30 UTC, lead's direction).** S-1 Q3 measured where the loss is: the gap to the top ten opens in the first
25 rounds and is economy, not deaths — bed conversion, production, early portal use, territory (L36). Esquie's
map anatomy shows the bricks are different kinds of opening (starved, bed-desert, transit-collision) and that a
structure-gated opening mechanism can be silent off its cluster (L35). So the programme adds a phase axis to the
map axis of D-036: for each map cluster and each of the four components, mechanisms are optimised against the
field's *per-map opening percentiles* (r25, r50) with r100/r250 economy, hygiene and the off-pool panel as guards
— not as targets. Local gains are kept as local holds and structure-gated; global losses are recorded, not
avoided, because the point is to find what the components are actually coupled to (the lead's diagnosis: too many
changes pull on other threads, yet other teams optimise these independently, so the coupling is in our bot, not
the game). Overfitting risk is bounded by the D-036 transfer test and by K-1's synthetic maps. Gate arithmetic
adopts S-1 Q2: per-map contributions weighted by predictability. Every open lane (rc, SF-1, RL-1, M-1, K-1, S-1)
reports the r25/r50 per-map percentiles from now on; RL-1's curve-matching reward is this decision in learned form.

**Git state at D-037.** Merged into main: `r/ra` (Renoir's final commits), `r/monoco`, `r/sciel`, `r/esquie` (M-1),
`cx/b`. `cx/a` (two commits of pre-R-4 chassis tooling) conflicts with the reconciled `tools/cx` and stays
unmerged as history. The desktop lanes (HB-1, rb, rc, SF-1 "Sophie", RL-1) have no branches on origin yet.

**D-038 — HB-1 read; `hb1-12-direction-prior` and `hb1-13-phased-prior` registered at the head of the queue; X-1
issued (1 Oct 02:00 UTC).** HB-1 found Heartbreaker to be a rule wrapper around one learned decision (direction), a
static policy 27–29 Sep, and — the result that matters — that its direction model used as a prior inside Ares's
search gives 139–21 on the z1 panel (V06: 122–38) with economy +0.03–0.04 and every death rate down 30–40 %,
replicated at seed 2 (hb1-12; hb1-13 fades the prior after r150 with similar numbers). Under D-032 this is an
accept on every guard; it is registered for the dev screen at 530/525 (executor still shadow). The lead's
three-tier design (CNN/RNN representation → XGBoost decision heads → policy improvement, cycled, over an
algorithmic map memory) is issued as X-1 with expert iteration (search relabels, trees distil) as the improvement
operator and hb1-12's search-plus-prior as the starting architecture; RL-1 may be folded into it. Sonar is split
into receiving (observations, learned use) and sending (a head under a fixed L32/L33 protocol); emergent
communication is out of scope. Ledger: L27 → 0.7.

**D-039 — the desktop lanes read; the queue re-ordered for the 4 MiB upload cap (1 Oct 03:00 UTC).** Merged to main:
`r/verso` (X-1), `r/tt` (top-team anatomy: cheji bt, Stockfish), `r/rb` (Aline, blind lane, closed), `r/rc` (Gustave,
paused), `r/maelle` (SF-1, wrapped), `r/alicia` (RL-1, running). Readings: (1) the two mechanisms that passed D-032 are
both information mechanisms — Heartbreaker's direction prior inside Ares's search (verso-01: win +0.15, econ +0.052)
and Aline's symmetry inference (econ +0.025, dragons +0.05, win +6 pp); every continuous weight move on V06's
evaluation sits in a flat bowl (Maelle's zero-weight optima, Alicia's ES drift), which is the local minimum the lead
described, now measured; (2) the TT lane found the submission zip is capped at 4 MiB, so `hb1-12`/`hb1-13` (17 MiB)
can never upload — `hb1-14-prior-r540` (3.74 MiB, 141–19) and `verso-05-hb800-prior` (3.38 MiB) are registered
ahead of them (540/535), `aline-17-sym-seal` at 515 and `gustave-07c-mouthroute` at 505 (their manifests repaired
as director housekeeping); registration now rejects archives over 4 MiB; (3) the top teams' edge after r200 is
deliberate endgame conversion (L39) and their rules do not port — the trigger to build is Ares's own feeder logic
keyed on state (opponent units at r300), which is the phase switch of L31/L32 at game scale; (4) Maelle and Alicia
are closed as weight-tuning efforts; their platforms (state module, feature dump, ES loop) are inherited by Verso.

**D-040 — the rules changed with `unswbc 1.2.3`; phase 2 opens with six instances (1 Oct 22:30 UTC).** The toolkit on
PyPI moved to 1.2.3 (protocol 3 unchanged; engine wasm, helper comments and the verdict logic changed). Verified by
diff and by running it: (1) sprint cost — a dragon of length L takes its first ⌈L/4⌉ steps free and pays one segment
per step after, keeping at least 2 (was x−1 per x steps); (2) round-limit tiebreak — queen length (the team's
lowest-id robot) first, then longest dragon, then total length (was longest, total). The docs site still shows the old
text. Consequences: all pre-1-Oct numbers are pre-rules; the corpus and the BENCHMARKS references must be split by era
once the live server's switch time is observed; sprint caps and the cramped-split/conversion findings need
re-measurement; the endgame is a queen race, which changes L39's trigger to a queen trigger. Phase 2 (`docs/hub/PHASE2-PROTOCOL.md`):
three analysts (hypotheses, targets, readings; the Claude analyst is the sole replay puller) and three testers
(gate-tested experiments), one per model, sharing the repository through per-lineage status files, `docs/hub/BOARD.md`
(append-only traffic), `docs/hub/TARGETS.md` (analysts' targets) and the ledger; prompts `P2-analyst` and `P2-tester`.
The desktop venv and the Mac hub venv move to 1.2.3 (lead and director respectively); the harness pin follows.


## D-041 — Manual submit control; hb1-14 uploaded and activated for the new server round (1 Oct)

The lead reported a new server round with nothing of ours live and asked for the best bot to go up. The executor
stays in shadow (D-031); instead a director-only control `hub-state/control/submit.json` `{candidate, activate, by,
note}` was added to the actuator (`submit_check`): it verifies the frozen archive against the registered
`source_files`, uploads it as `LV-<name>-<fp8>-ai`, records the submission id on the candidate row and, on
`activate`, activates it and takes hub control as `director`. Two server-side facts learned: the server rejects
`language = "c++"` ("Pick a language.") — the CLI normalises bot.toml's spelling to `python|cpp|c` before posting,
and the actuator and executor now do the same; and activation of a fresh upload returns 409 until the build is
ready (~2 min), so activate is retried. Choice: `hb1-14-prior-r540` (the Heartbreaker direction prior inside
Ares's search, 141–19 on z1, 3.74 MiB; hb1-12 at 139–21 is 17 MiB and cannot be uploaded; verso-05 is the same
mechanism with a smaller prior). Uploaded as submission **14265** `LV-hb1-14-prior-r540-ed7e4515-ai`, activated
17:00 UTC; hub `control = 14265`, owner director. Caveat: its 141–19 was measured under pre-change rules
(unswbc 1.2.2); nothing has been measured for it under 1.2.3 yet — the live games it now plays are the first
post-change evidence and the P2 analysts should read them as such. Teammates may activate over it at will;
the executor will not restore it.

## D-042 — Phase 2 first-wave rulings and the handoff (1 Oct 19:40Z / 2 Oct ACST)

All ten lane branches read and merged to `main` (`41f23e04e`): analysts Antioch, Himeji, Nara; testers Carthage, Kyoto,
Rome; stewards Clair, Obscur, Expedition; TT. Summary in `docs/PHASE2-SUMMARY-2026-10-02.md`, handoff in
`docs/HANDOFF-2026-10-02.md`. Rulings: (1) era rule `started_at ≥ 2026-10-01T06:00Z` (Antioch's; Nara's 09:00Z is
equivalent — no game started between 05:58Z and 09:23Z); (2) decoder: FRAME_VERSION 7 on main combines Carthage's
body-inferred queen (`queen_body`, `FRAME_RULES=pre123`) with Antioch's engine verdict and header queen field
(validated 300/300); every FRAME_VERSION 5 score on post-change replays is superseded by Himeji's official re-reads;
(3) gate: Himeji's win-led rule for predeclared 1.2.3 adaptations (pool win lb > 0, gen win lb > −0.02, econ lb > −0.03
both panels, units/total lb ≥ −0.02, no Φ guard, no queen exemption); Clair's BENCHMARKS 1 Oct revision stands as
written, its implied flips (verso-02/05, tt-05) are accept-shaped holds until recomputed on the desktop; the units
guard form is referred to the analysts; (4) `carthage-05-free-sprint` passes the win-led rule as a bundle (pool win
+0.045 [+0.019, +0.074], gen +0.017 [+0.003, +0.031], econ flat) — CANDIDATE.toml written by the director as
housekeeping, registered at 545, next upload after hb1-14; the 05−04 increment is inconclusive and gets a five-seed
run; (5) `carthage-04` is the rules-era baseline once its fingerprint is frozen; (6) ledger moves (log line 1 Oct
19:30Z): L02 0.5, L04 0.2, L11 0.3, L12 0.3, L14 0.4, L16 0.7, L20 0.3, L21 0.1, L24 0.3, L29 0.9, L30 0.3, L31 0.6,
L34 0.3, L36 0.85, L38 0.75, L39 0.8 (re-keyed to the queen), L40 0.3; L41–L47 (Obscur's numbering), L48 (Clair's
atlas row), L49 (queen survival, 0.5), L50 (sprint adaptation, 0.8); L03 kept at 0.7 against Obscur's 0.5; (7) one
ledger steward (Clair); Obscur's `gates.py`/`phasegate.py` to be ported into the shared scorecard; Expedition paused
until it has a post-change roster; gustave-07c's registration to be withdrawn (mouth tax negative on three hosts);
(8) `.gitattributes` with `merge=union` for BOARD/TARGETS/CORPUS/HYPOTHESES, and the keeper's include list extended
to it. Outstanding for the director: Mac hub venv → 1.2.3 and the harness repin; collector targets for the five
teams Antioch named; the gustave-07c withdrawal.

## D-043 — live maps in the repo (4 Oct 2026, director)

The server replaced six ladder maps on 2 Oct 03:49Z (Autarky, Default, Prisoners Dilemma, Schooltime, Slithery Fight,
Trophy; Shenzhen/Chongqing, map era `post-m2`) and restored seven non-ladder maps at 04:31Z (Australia, Islands, Around
UNSW, Maze, Stripes, Tower Defense, weakhold). The repo's `maps/*.map` predate both changes. Ruling: (1) the 22 map
templates of `unswbc==1.2.9` are added unchanged in `maps/live/` (sha256 in `docs/maps-live.md`); `maps/*.map` stays
as the pre-swap set so that running and completed pairs remain readable; (2) `run_panel.LIVE_MAPS_M2` (17 maps:
the ten ladder maps + the seven restored) is the pool for every new arm; `LIVE_MAPS` is for finishing or re-reading
pre-swap pairs only; (3) testers re-measure their base on `LIVE_MAPS_M2` before the next arm; the parent for new
1.2.3-adaptation arms is `carthage-05-free-sprint` (live since 2 Oct 04:22Z), not hb1-14; (4) gen twins derived from
the six swapped maps (`var/*_tr`, `pub/*_rec` of autarky/default/dilemma/schooltime/slithery/trophy) model old
geometry and are flagged, not deleted; regenerate them from `maps/live/` before using them as transfer evidence;
(5) all post-m2 references are per `map_era` (Chongqing's store column) — no pooling of old- and new-map numbers.
Not verified: byte identity of `maps/live/` with the server's maps (Shenzhen reproduced the live Schooltime cage on
the 1.2.9 template; `unsw.map` is assumed to be "Around UNSW").

## D-044: hand rules are probes, and learning is where we are going (4 Oct 2026, director, at the lead's instruction)

The programme's goal is discovery with a view to learning the right policy, by imitation, value fitting and RL. We are
not building a long-term collection of hand-coded rules. A hand rule is worth building for what it teaches us: its dose
response (does it move the outcome we target, and how much?) and its side effects (what else does it move?).

1. **Every new hand arm is a dial, not a switch.**
   - Declare at least three doses before the run, with the parent as dose 0. Examples: reserve slots 0/1/3/5, a minimum
     number of free exits 0/1/2, a premium of 0/x/2x.
   - Report a response curve for the targeted outcome, plus side effects on: economy, deaths by cause, units, length,
     and win split by regime (elimination vs round-limit maps) and by map_era.
   - Screening dose arms may use seed 1 on both panels. The full D-042 gate applies only to the dose proposed for
     deployment.
2. **Every finding about an arm or a mechanism ends with an RL translation section with four parts:**
   - (a) **observation**: the features a policy or value model needs to see this situation;
   - (b) **action**: the actions it needs (for example, a deliberate invalid command, a choice of split size, a sprint
     length);
   - (c) **value/reward**: which terms the outcome depends on;
   - (d) **demonstration**: whether top-team replays already demonstrate the behaviour (cloneable), or only search and
     self-play could find it (an exploration problem).
3. **A hand rule may ship in the short term** when it is a clear live gain (the Schooltime cage fix C+D+E is the
   current case). It is tagged `temporary` in its CANDIDATE.toml and gets a learned replacement target: the learned
   prior must reproduce or beat it on held-out states and panels. Once it does, the rule is removed.
4. **Analysts prioritise what learning needs.** That means features, labels, value targets and facts about our state
   distribution: unit-cap saturation, id-ordered movement within a round, queen-state observability, and where sonar
   echoes reach. A one-off rule recommendation comes second.
5. **The learner lane (Osaka, `docs/briefs/osaka-learner-lane.md`) consumes three things:** the dose tables, the RL
   translation sections, and the logged search scores. A hypothesis is resolved for learning when its feature or action
   is in the encoder, and its effect shows up in held-out accuracy of the value model V and the policy prior P.

## D-045 — Prospective 1.2.5 learned-arm local gate (4 Oct 2026)

Adopt the win-led Himeji criteria prospectively for learned-policy and
learned-search arms evaluated under `unswbc==1.2.5`. This resolves the learned
track's gate prerequisite without changing D-032, D-042's historical scope,
or any completed verdict. The complete rule, rationale, and implementation
are in [`2026-10-04-antioch-learned-arm-gate.md`](2026-10-04-antioch-learned-arm-gate.md).

The nominee is compared to a predeclared parent on complete pool and gen panels,
seeds 1–5, both seats, with FRAME_VERSION 7 and successful 1.2.5 run records.
The paired fixture bootstrap uses 1,000 resamples, seed 7; gates use the 5th
percentile. Require pool expected-score lower bound > 0; gen expected-score
lower bound > −0.02; normalized `econ~` lower bound > −0.03 on both panels;
normalized units@100 and total@100 lower bounds ≥ −0.02 on both panels; the
existing tier-2 ≤10% guard on both panels; and zero new invalid-action deaths.
Missing fixtures, unsuccessful runs, timeouts, or missing runtime records are
INCOMPLETE. The separate CPU check must remain within the official points
budget without errors. The gate applies to one frozen nominee; its five-seed
panels stay out of training and model selection. A local ACCEPT advances the
candidate to the experiment stack and does not promote it; fresh live
confirmation remains required.

`tools/carthage/lane.py score ... --gate learned125 --seeds 1,2,3,4,5` encodes
this rule as an opt-in mode. The existing default `--gate d032` is unchanged.
This closes only the evaluation-gate prerequisite. H-S1 and the all-family
hand-mining stop condition remain open, so training entry is still gated on
those separate conditions.

## D-046 — Phase 3 charter: deadline, engine, splits, gate, ladder, promotion, rollback, rosters, seats (4 Oct 2026 10:50Z, Chair: Ushijima)

**Numbering.** The Phase 3 macro and prompts (`docs/learning/`) call the Chair's first record "D-045". That number
was already taken by the learned-arm local gate above. Wherever `docs/learning/` says "D-045", read **D-046** for the
charter (deadline, splits, engine, promotion, rollback, rosters, seats) and D-045 for the gate thresholds as amended
in §4 here. No earlier record is rewritten. Later Chair records continue from D-047.

**Training entry.** D-045's last paragraph kept training gated on H-S1 and on a hand-mining stop condition. D-044 and
the Phase 3 macro, both at the lead's instruction, make the learned policy the main line; H-S1 was since rejected as
implemented (Himeji H27-04). Training entry is therefore open from R0, and the ladder's own gates govern it.

### 1. Deadline and freeze schedule (provisional)

- No final submission time is recorded in the repo, and the contest pages (docs, game-format, tournaments) show no
  date in fetched text. The lead is asked once, in the Chair's first session (human-in-the-loop item H1,
  `claude/chair-status.md`).
- Until answered, the deadline is **assumed to be 2026-10-11 10:30Z** (7 days). All times below move with it.
  - T−72 h = **8 Oct 10:30Z**: no new mechanism types. A new head, feature block, search change or hand rule may not
    start its gate after this time. Re-fits and predeclared doses of mechanisms that already passed may.
  - T−24 h = **10 Oct 10:30Z**: freeze. No promotion.
  - T−6 h = **11 Oct 04:30Z**: rollback only.
- Ladder aim under this horizon (targets, not gates): R0 passed by 5 Oct 12Z; R1 and R2 offline by 6 Oct 12Z; R2
  deploy gate and live screen by 7 Oct 12Z; R3 heads up to T−72 h; R4/R5 only if R2 is live by 7 Oct. R6 only at
  small scale and by a later D-record; R7/R8 deferred (no GPU, macro §8).

### 2. Engine and maps (checked by the Chair, 4 Oct)

- The PyPI wheels `unswbc` 1.2.3, 1.2.5 and 1.2.9 carry a **byte-identical engine**: `unswbc_engine.wasm` sha256
  `26e68680e45eb0f221db702aead9eefde776c2ad2ba066f4ddf8c12500c6a546` and `python-metered.wasm` sha256
  `48342178e7ca…f78125` in all three. A recursive diff of 1.2.3 against 1.2.9 shows only the version string, the
  replay-viewer extension and map templates; 1.2.3 against 1.2.5 shows only the first two.
- Consequences: (a) results recorded under 1.2.3 (Rome's D-043 zero and dose screens), 1.2.5 (Carthage) and 1.2.9
  (Shenzhen's fixtures) are comparable when the maps are the same; (b) Nara's 07:05Z question (verdict classes and
  sprint pricing differing between 1.2.3 and 1.2.9) is answered: they do not differ; (c) the Phase 3 runtime is
  **any wheel carrying that engine hash**, with maps from `maps/live/`. Every result card records the wheel version
  and the engine hash.
- Not verified: that the server runs this engine, and that `maps/live/` is byte-identical to the server's maps
  (D-043). Data checks the second from map text in post-m2 replays (R0, engineering, no council).

### 3. Frozen splits (constraints frozen now; hashes recorded in D-047 from Data's manifests)

Data proposes, the Chair approves, and nothing below is re-drawn afterwards.

- **Held-out maps.** At least three of `LIVE_MAPS_M2`: one from each of the behavioural classes A, B and C
  (Chongqing C7-03: A = devil, trophy, stripes, tower_defense, queen_of_spades, default, autarky; B = australia,
  unsw, islands, maze, schooltime; C = trauma, weakhold, dilemma). Classes D (slithery_fight) and E (portals) have
  one map each and are not held out as maps; they are covered by held-out series.
  - Default selection: within each class sort the map names ascending and take index
    `int(sha256("D-046/" + class letter), 16) mod n`. Data may propose a different map only with a written reason
    that does not use any model's or bot's per-map results (for example too few teacher games on the drawn map, or
    a mechanic that exists on one map only and must stay learnable).
  - The default draw gives **trophy (A), maze (B), trauma (C)**. Known cost: Trauma is the map with the largest
    opening gap (Chongqing C6-03), and 84 % of its round-limit games are queen-decided (C5-02), so teachers' Trauma
    games do not train P or V. That cost is accepted: held-out maps stay out of training for the whole phase. They are the only
    honest transfer test, and the server replaced six maps in one day (D-043). A pre-registered final re-fit on all
    maps, judged live only, is not allowed unless a later D-record allows it; it may be proposed by card once the
    deadline is known.
  - Every game on a held-out map is held out, in every dataset, for the whole phase.
- **Held-out series.** Whole series only, never single games: `bucket = int(sha256("D-046/" + series id), 16) mod 10`;
  bucket 0 is held out (test), bucket 1 is validation (early stopping and model selection), buckets 2–9 train. The
  same rule applies to our own games.
- **Gating fixtures and seeds.** Pool = ZOO × the 17 `LIVE_MAPS_M2` maps × both seats; gen = `maps/new` plus twins
  regenerated from `maps/live/` (the stale twins of the six swapped maps are excluded until regenerated). Seeds 1–3
  are the gate seeds; seeds 4–5 are a reserve that is touched only when a card declares five seeds before its run.
  Games on gate seeds are never training rows, never used for model selection, and never used to tune a dial. Training
  rollouts, self-play and search-target logging for training use **seeds ≥ 1000**. Search-target logs written during
  gate runs are kept for diagnosis, tagged `gate`, and excluded from training by Data's leakage audit. This narrows
  the Evaluator prompt's "every panel game becomes training data" to non-gate panels.
- **Already consumed.** The 94-game holdout (index 192–285) used by Kanazawa and Himeji is consumed (H25-04) and is
  descriptive only.
- Manifests with hashes and row counts go to `docs/learning/splits/`; D-047 records them.

### 4. The Phase 3 local gate (reconciles D-042, D-045 and macro §8)

Thresholds are D-045's, unchanged: candidate minus declared parent, pool expected-score lower bound > 0, gen > −0.02;
`econ~` lower bound > −0.03 on both panels; units@100 and total@100 lower bounds ≥ −0.02 on both panels; tier-2
death-rate guard ≤ 10 %; missing fixtures, failed runs and timeouts make the result INCOMPLETE, never a loss. Deploy
limits are part of the gate: zip ≤ 4 MiB, ≤ 30 M points per turn including turn-0 model load, zero runtime errors,
golden parity with the switch off. Amendments for Phase 3:

1. **Runtime.** D-045's "1.2.5 run record" becomes "a run record carrying the §2 engine hash", which today means
   wheel 1.2.3, 1.2.5 or 1.2.9. `lane.py --gate learned125` hard-codes `runtime_version == '1.2.5'` (Nishinoya's
   probe 3) and is left untouched; the Evaluator implements this section as a separate opt-in mode `phase3` in its
   own copy of the scorer.
2. **Seeds.** Seed 1 on both panels is a screen for every candidate. The full gate is seeds 1–3 for a nominee the
   Chair names (macro §8). Five seeds only if the card says so before the run. No extension after results are seen.
   Three seeds instead of D-045's five lower the gate's power; they cannot make a lower-bound clause easier to pass.
3. **Interval convention (provisional until the auditor's first review, frozen before the first nominee's gate).**
   Paired fixture-cluster bootstrap, cluster = map × opponent × seat with seeds kept together, 1,000 resamples,
   seed 7, gate on the 5th percentile. Every card states the convention it used.
4. **Designed invalid commands.** D-045's "zero new invalid-action deaths" applies to unintended ones. A mechanism
   whose action is a deliberate invalid command (the cage child cull, the R3 cull head) declares it in its card;
   those deaths are reported separately per map and must occur only in the declared trigger states.
5. **Screens are not verdicts.** After a seed-1 screen the Chair decides whether the candidate becomes a nominee.
   Default: advance if the pool point estimate is ≥ 0, gen ≥ −0.02 and nothing breaks.
6. **Map-local mechanisms.** A mechanism that fires on one map class cannot easily clear a pooled lower bound. The
   Evaluator therefore also reports a stratified readout: target stratum (maps where the trigger fires in the
   parent's games, named before the run) and off-target stratum, with trigger counts per map. The pooled gate letter
   is never relabelled. If the pool clause is inconclusive (point estimate > 0, lower bound ≤ 0) while the
   target stratum improves and the off-target stratum is non-inferior, the Chair calls an immediate council round.

### 5. Ladder state: R0 open

- **Incumbent and parent:** `carthage-05-free-sprint`, submission 14585, hub name
  `LV-carthage-05-free-sprint-ebeba55f-ai`, live since 2 Oct 04:22Z. **Fallback:** `hb1-14-prior-r540`, submission
  14265.
- **Zero** (Rome, D-043, wheel 1.2.3, seeds 1–3, both seats, official outcomes): pool 656–160–0 of 816 (expected
  score 0.804); gen 1,038–353–1 of 1,392 (0.746), and 861–338–1 of 1,200 (0.718) without the stale twins; queen
  reached r490 and alive in 2 of 816 pool games.
- **R0 exit checklist** (all must be recorded in `docs/learning/ladder.md`): encoder Python = C++ on 1,000 turns;
  labels agree with HB-1 above 99 %; leakage audit; split manifests (D-047); post-m2 decode finished; registry in
  use; gen twins regenerated from `maps/live/`; the `battles.json` control and the live monitor.
- **Outside the ladder:** the cage rule C+D with E = 0, tagged `temporary`, enters only through §4 and §7. Its
  learned replacement target is R3/R4.
- Each ladder candidate is built on the incumbent at hand-over. If the incumbent changes while its gate runs, the
  gate finishes against the declared parent; before promotion the switch is re-applied on the new incumbent and
  must pass golden parity and a seed-1 screen.

### 6. Evaluator queue (initial order)

1. **Cage C+D, E = 0, against carthage-05.** Frozen objective: target stratum = live Schooltime; expected sign +
   on queen alive at r490 among reached and on wins (Rome's seed-1 package screen with E = 1: 11/12 alive, wins
   16/16 against the parent's 0/16 and 14/16). Off-target: the other 16 pool maps and gen, expected zero trigger
   firings and no change. Stop rule: seed 1 first; continue to seeds 2–3 only if the Chair advances it under
   §4.5; HOLD and a diagnosis card otherwise. Expected side effect to check: invalid deaths confined to Schooltime.
2. **H-KZ12 entry-capacity dial, H29 contract, doses k = 0/4/8/16.** Rome has k = 4 on seed 1 (pool 0.8309 → 0.8456,
   current gen 0.7200 → 0.7225, no verdict). Remaining: k = 8 and 16, and the gen diagnostics, with veto firings
   per 1,000 queen moves per map as a first-class column. A dose with no firings is "did not reach", not a null.
3. Ladder candidates from the Learner pre-empt items 1–2 at a fixture boundary.

Not queued as hand arms: H-KZ26 (standoff radius against enemy sprint reach), H-SZ31/32/34/35, H-H7, H-H8, the E
reserve dial, queen hunting. Their findings feed R3–R4 as features and labels (D-044 §4–5). Any of them can be
proposed as a `temporary` dial with a card (macro §3); H-KZ26 has the strongest case by evidence (20 of 43 queen
head-on deaths are enemy sprint strikes, 15 of 20 approximately avoidable, Kanazawa units 11–12 with Himeji's H31-02
qualification).

### 7. Promotion rule

A candidate is promoted only by a Chair D-record, and only when all of these hold:
- it is registered (`docs/learning/registry.md`) and passed the §4 gate against its declared parent;
- a live screen against the incumbent on a roster named before the screen: same opponents, maps and seats, same
  window, unranked, at least 60 matched games; paired difference in score minus Elo expectation with a whole-series
  bootstrap; **lower bound (5th percentile) > −0.02 and point estimate > 0**;
- no rise in errors or timeouts;
- at least 12 h since the last promotion, and not inside the freeze (§1).

### 8. Rollback rule

Live ops rolls back automatically, and the Chair reviews afterwards, when either holds:
- after 40 ranked games on the new submission, score minus Elo expectation is below −0.08 and the series-bootstrap
  upper bound (95th percentile) is below 0;
- any crash or disqualification.
Rollback activates the previous submission through `submit.json`. A human activation that changes the live
submission pauses all automation until the Chair resolves it.

### 9. Rosters (Live ops maintains them; a test names its roster before it runs)

- **band:** the teams we actually met in ranked over the last 48 h;
- **top:** the current top ten of the ladder;
- **style:** one team each for keeper, cull-feeder, hunter and elimination specialist, from Data's top-team pages;
- **regression:** opponents the incumbent beats (score ≥ 0.7 over at least 10 games).

### 10. Roles and seats

- Chair: Ushijima (Claude; this record).
- Data, Learner, Evaluator, Live ops: named by the lead when started; recorded in D-047 onward and in
  `claude/chair-status.md`. Until a role has a lane, its queue items wait; no other lane takes them.
- Council pool at 10:55Z: **Tanaka** (GPT, standing auditor, `r/tanaka`), **Sugawara** (Claude, mechanism) and
  **Nishinoya** (GLM, probe, `r/nishinoya`). Other instances join as the lead starts them. A round seats three
  reviewers from at least two model families; if fewer than three seats are available, it runs with those seats and
  the D-record states the vacancy. Promotion and rollback rounds are immediate.
- First audit request, not a card: Tanaka reviews §3 (split hash rules) and §4.3 (interval convention) and
  replicates §2 (engine hash) in `docs/learning/reviews/D-046-tanaka.md`. §4.3 is frozen after that review and
  before the first nominee's gate.
- Phase 2 lanes are inputs, not roles (macro §7). Himeji, Nara, Chongqing and Seoul have wrapped up. Whether Rome,
  Shenzhen and Kanazawa continue is the lead's decision.

### 11. Answers to the council intake (Sugawara, 10:40Z, `docs/learning/reviews/intake-sugawara.md`)

- §1 of the intake, and Tanaka's 10:43Z request (number collision, gate and seeds, runtime, training entry):
  resolved by the numbering note, §4, §2 and the training-entry note of this record. The runtime conflict
  disappears because the engine is the same binary in 1.2.3, 1.2.5 and 1.2.9.
- §4 (held-out maps): option (a) is adopted, as written in §3. The default draw already lands on two large-gap queen
  maps (maze, trauma), which gives the held-out test power; trophy covers the elimination class.
- §2 and §3 (encode from the IO round block; queen-knowledge features from own-view history only, sonar-relayed
  knowledge as a separate R4 block): adopted as R0 design constraints for Data and the Learner, recorded in
  `docs/learning/ladder.md` with the intake's falsifier. They are engineering constraints and need no council round.
- Nishinoya's 10:52Z probes (unaudited): (1) the decode queue is 7,617 and growing, so R0 item 1 is a re-run of
  the native decode and is on the human-in-the-loop list; (2) every live map has 666–1,050 in-scope post-m2 games,
  so the §3 default draw is supportable; Tanaka's audit note replicates the counts for trophy, maze and trauma;
  (3) the gate-tooling contradiction is ruled in §4.1.

