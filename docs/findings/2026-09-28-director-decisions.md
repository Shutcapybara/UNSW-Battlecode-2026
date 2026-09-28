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
