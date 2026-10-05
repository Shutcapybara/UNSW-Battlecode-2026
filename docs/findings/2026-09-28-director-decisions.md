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

### 3. Frozen splits (held-out maps frozen now; series and fixture manifests recorded in a later D-record)

The held-out maps are frozen by this record, by a rule fixed before any proposal was read. For the series buckets
and gate fixtures the rule is frozen here; Data builds the manifests with hashes and the Chair records them. Nothing
below is re-drawn afterwards.

- **Held-out maps.** At least three of `LIVE_MAPS_M2`: one from each of the behavioural classes A, B and C
  (Chongqing C7-03: A = devil, trophy, stripes, tower_defense, queen_of_spades, default, autarky; B = australia,
  unsw, islands, maze, schooltime; C = trauma, weakhold, dilemma). Classes D (slithery_fight) and E (portals) have
  one map each and are not held out as maps; they are covered by held-out series.
  - Selection rule: within each class sort the map names ascending and take index
    `int(sha256("D-046/" + class letter), 16) mod n`.
  - The draw gives **trophy (A), maze (B), trauma (C)**, frozen in `docs/learning/splits/heldout-maps.json` with the
    template hashes. Data may ask for a replacement only for a defect in the data (for example too few teacher games
    on a drawn map), never from any model's or bot's results. Known cost: Trauma is the map with the largest
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
- Manifests with hashes and row counts go to `docs/learning/splits/`; a later D-record records them.

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
  labels agree with HB-1 above 99 %; leakage audit; split manifests; post-m2 decode finished; registry in
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
- Learner: **Hinata** (Claude; a Cowork VM session, so R1 only until a native session exists).
- Data, Evaluator, Live ops: named by the lead when started; recorded in later D-records and in
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
- §4 (held-out maps): option (a) is adopted, as written in §3. The draw lands on two large-gap queen
  maps (maze, trauma), which gives the held-out test power; trophy covers the elimination class.
- §2 and §3 (encode from the IO round block; queen-knowledge features from own-view history only, sonar-relayed
  knowledge as a separate R4 block): adopted as R0 design constraints for Data and the Learner, recorded in
  `docs/learning/ladder.md` with the intake's falsifier. They are engineering constraints and need no council round.
- Nishinoya's 10:52Z probes (unaudited): (1) the decode queue is 7,617 and growing, so R0 item 1 is a re-run of
  the native decode and is on the human-in-the-loop list; (2) every live map has 666–1,050 in-scope post-m2 games,
  so the §3 draw is supportable; Tanaka's audit note replicates the counts for trophy, maze and trauma;
  (3) the gate-tooling contradiction is ruled in §4.1.

## D-047 — P-1 (R1, V0) rulings before the fit; council round 1 opened (4 Oct 2026 10:52Z, Chair: Ushijima)

Card: `docs/learning/proposals/P-hinata-01-R1-V0.md`, filed 10:45Z by Hinata (Learner). It is numbered **P-1**
(`docs/learning/proposals/INDEX.md`); its content stays as filed. No fit has run and no pool-map outcome was read.

1. **Held-out maps.** The fit reads `docs/learning/splits/heldout-maps.json`: Maze, Trauma, Trophy (D-046 §3).
   Hinata's provisional manifest (Autarky, Maze, Trauma) agrees on classes B and C. Class A stays Trophy for two
   reasons: the draw rule was fixed before any proposal was read; and Autarky is one of the two cleanest transit-gap
   maps (Chongqing C6-03), where teachers' demonstrations are most useful to the policy prior, while on Trophy we are
   at or above the top ten at r50. The advisory fit on the provisional manifest is not run.
2. **Timing.** The gating fit runs once, on the complete post-m2 decode (ladder R0 item 1), with the data hash
   recorded. Today 7,057 of about 14,700 in-scope games are decoded and the decode order is not random, so the one
   confirmation on held-out maps is not spent on half the data. If the decode is not complete by **5 Oct 00:00Z**,
   the fit runs on the store as it is then.
3. **Ladder position.** R1 changes no bot and has no parent. Its offline work and R2's may proceed in parallel.
   R1 must pass before R5. R1 is not recorded as passed until R0 items 1, 2 and 5 are closed.
4. **Gate reading: council round 1.** The author asks for a ruling before the fit. The two readings:
   - **G1** (the card as written): point ΔAUC(V0 − Φ) ≥ 0 in each of 14 regime × checkpoint cells; round-limit r50
     AUC ≥ 0.66; calibration slope in [0.9, 1.1] in each cell from r25; the same on held-out maps, one shot.
   - **G2** (the author's alternative): game-cluster 5th-percentile lower bound of ΔAUC > −0.01 in every cell, and
     point ΔAUC > 0 in the round-limit cells from r150; the other clauses as in G1.
   - Note: the macro's R1 gate names seven checkpoints; the split by regime into 14 cells is the card's.
   - Seats: Tanaka (auditor), Sugawara, Nishinoya. Reviews in `docs/learning/reviews/P-1-<lane>.md`, due 13:00Z.
     Each review recommends G1, G2 or an amendment, and gives P(pass) under G1 and under G2. Scoring uses the
     reading the Chair freezes.
   - The Chair's reading before the reviews, so that dissent can be aimed at it: G1 joins 14 point comparisons and
     can fail on noise in cells where the card itself predicts ΔAUC ≈ 0. A non-inferiority margin there, with a
     superiority clause where the mechanism is claimed, tests the claim more directly. Nothing is decided until the
     round closes; the Chair freezes the reading in D-049 before the fit.
5. **Owner, objective, stop rule.** Owner: Hinata. Frozen objective: the card's, under the reading frozen in D-049.
   Stop rule: the card's (one fit, one confirmation, no hyper-parameter search after any pool-map outcome is read; a
   failure gives a diagnosis card, not a re-run).
6. **Host.** Hinata runs in a Cowork VM, which is enough for R1. R2 and later need a native Mac session
   (human-in-the-loop item H8).

## D-048 — Live ops rulings, the rollback reference, and an interim Evaluator (4 Oct 2026 10:55Z, Chair: Ushijima)

Answers Daichi's 10:50Z requests (Live ops; `claude/daichi-status.md` on `r/daichi`) and acts on the first read of
the live monitor.

1. **The executor stays in shadow.** Live mode would re-arm its automatic experiments, uploads and promotions, which
   D-046 §7 forbids. `battles.json` dispatches on its own authority, and only after an `enable` that names a Chair
   D-record.
2. **Deploy the control with dispatch off.** `r/daichi` may be merged to `main` through the keeper once `merge-tree`
   shows no conflict and the hub gate tests pass, and the hub may then be redeployed. This record is not the enable.
3. **First job after the deploy: an A/A dry run.** Both arms are submission 14585, on the dev opponents, so nothing is
   activated. Its purpose is to measure the noise of the paired report and to check that a true difference of zero
   reads as zero. Daichi sizes it and states the expected interval width before it runs. If the control cannot take
   two identical arms, Daichi says so and proposes the nearest equivalent.
4. **Exposure of a temporarily active candidate: accepted, with conditions.**
   - Only an arm that passed the D-046 §4 local gate (registered, CPU-probed, zero errors) may be activated. An
     unvetted arm never is.
   - The guards stay as built: no dispatch in the even-hour blackout, none while one of our ranked series is in
     flight, restore in `finally`, lost restores repaired first.
   - Every activation window is logged with start and end times. A ranked game that lands in a window is listed in
     the job report, attributed by replay header to the submission that played it, and excluded from the incumbent's
     monitor statistics. A ranked series landing in a window pauses the job.
   - Reason: on dev opponents only, a live screen says nothing about the named roster that D-046 §7 requires. A
     gate-passed candidate playing one ranked series is a small, bounded risk.
5. **Second quota executor.** Whether the Windows quota runner is off is asked of the lead (item H9). Until it is
   answered, no non-live arm is dispatched. A/A jobs are unaffected.
6. **Hub link.** Daichi links submission 14585 to `carthage-05-free-sprint` in the hub mirror through the hub's own
   controls, after checking fingerprint `ebeba55f` against the API listing. No mutating API call is involved. Until
   then, rollback goes through `restore.json`.
7. **Rollback rule, scope.** D-046 §8 applies only to a submission promoted under §7, over its ranked games since
   activation. It does not apply to 14585. The incumbent's negative residual is not a reason to activate hb1-14.
8. **Rollback rule, reference (to the council, with round 1, reviews due 13:00Z in
   `docs/learning/reviews/D-048-<lane>.md`).** The monitor shows the incumbent itself below its Elo expectation:
   −0.037 [−0.079, +0.003] over 417 ranked games in 87 series since 2 Oct, and −0.093 [−0.184, −0.002] over the last
   40 (series bootstrap, 5th and 95th percentiles). A new submission inherits the old rating. An absolute threshold
   of −0.08 could therefore roll back a candidate that equals or beats the incumbent.
   - Proposed amendment: roll back when (the new submission's residual over its first 40 ranked games) minus (the
     replaced submission's residual over its last 40 ranked games before the switch) is below −0.08, and the
     series-bootstrap 95th percentile of that difference is below 0. The crash and disqualification clause is
     unchanged.
   - Until the Chair decides, §8 stands as written. No promotion can happen before the round closes.
9. **Priority, and an interim Evaluator.** The largest per-map residuals are Schooltime −0.45 [−0.52, −0.37],
   weakhold −0.30 and Trauma −0.26 (ranked, 18–31 games per map). Schooltime is the cage rule's map. Repairing it
   to zero would be worth roughly +0.02 to +0.03 of overall score (the Chair's arithmetic from the map's share of
   the 417 games, not a measurement). The cage arm (D-046 §6 item 1) is therefore the first candidate for a live
   screen, and it has no Evaluator.
   - Until the lead names an Evaluator lane, **Rome** may run D-046 §6 item 1 exactly as specified there: C+D with
     E = 0, parent carthage-05, seed 1 on both panels, under `build/learn/HEAVY.lock`, trigger counts per map, a
     result card. Rome built the E = 1 and E = 3 arms and the zero. No other arm is covered by this permission.
   - If an Evaluator lane reports first, it takes the item and Rome does not start it.

## D-049 — Held-out maps corrected to Autarky, Maze, Trauma; status of the R1 development fits (4 Oct 2026 10:59Z, Chair: Ushijima)

What happened. At 10:52Z, while D-047 was being merged, Hinata fitted P-1 (GBT) and then a second card, P-hinata-02
(logistic), on its provisional split: development by leave-one-map-out on 14 maps, with Autarky, Maze and Trauma
unscored. Those 14 development maps include Trophy, which D-046 §3 had just frozen as a held-out map. The model class
was changed after reading those development results, so Trophy has been tuned on. Nobody acted in bad faith; the
freeze and the fit crossed.

1. **Held-out maps: Autarky replaces Trophy.** The frozen set is **Autarky (A), Maze (B), Trauma (C)**
   (`docs/learning/splits/heldout-maps.json`, updated, with the history). Reasons:
   - The hard rule is that held-out maps are never trained on and never tuned on. Trophy no longer meets it for the
     value model. Autarky, Maze and Trauma have not been scored by any model.
   - This is the data-defect case D-046 §3 allows, and it does not use any result on the maps concerned.
   - Cost, accepted: teachers' Autarky games (one of the two cleanest transit-gap maps) do not train P. Trophy
     returns to training.
   - This is a correction of a freeze that was broken when it was made, before any use of the manifest. The set is
     not changed again. D-047 §1 is superseded on this point.
2. **P-1 (GBT V0) is closed as failed in development,** under its own gate: calibration slopes 0.58–0.88 out of map.
   Its diagnosis stands as the result card: the queen terms carry the gain; the tree interactions add nothing out
   of map and miscalibrate. The rung has failed once.
3. **P-hinata-02 is numbered P-2 and is the R1 candidate.** Logistic, Φ's six shares plus two antisymmetric queen
   terms. Development result (5,799 post-m2 games, 14 maps, leave-one-map-out, game-cluster bootstrap, 5th to 95th
   percentile): round-limit ΔAUC against Φ +0.020 [+0.013, +0.026] at r50, +0.056 [+0.046, +0.066] at r250, +0.102
   [+0.089, +0.114] at r400; elimination within ±0.005 up to r150; round-limit r50 AUC 0.671 against Φ's 0.651.
   - That result is discovery, not a verdict. The card and its gate "G-amend" were written after P-1's outcomes
     had been read on the same rows.
   - The verdict is one confirmation of the model **as fitted at 10:52Z** (code 3138d107, training rows c958e8c7…),
     scored once on the three held-out maps. No re-fit when more games are decoded.
   - The confirmation runs only after the Chair freezes the gate reading (D-050, after council round 1), and when
     the decode is complete or at 5 Oct 00:00Z, whichever is first (D-047 §2).
   - A linear model in place of the macro's GBT is accepted for R1: it is smaller, calibrated, and portable to the
     search leaf. It changes the model class and drops one feature that cannot enter a symmetric logit; the Chair
     treats that as one change.
4. **Council round 1, restated.** Cards P-1 (result) and P-2. Reviews are due 13:00Z in
   `docs/learning/reviews/P-2-<lane>.md`. Each review:
   - recommends the gate for the confirmation: "G-asis" or "G-amend" as written in P-2, or an amendment. These
     replace the G1 and G2 wording of D-047 §4;
   - gives P(the confirmation passes) under each;
   - Tanaka in addition replicates P-2's table from the frozen inputs and says whether a three-map confirmation
     split by regime has the power to mean anything (Autarky alone carries the elimination regime).
   - Fact for the reviews: Φ itself fails G-asis's slope band on round-limit r25 to r150, so no model that ranks
     like Φ can pass G-asis.
5. **For every lane.** A lane that is blocked on a Chair ruling waits for it. A run labelled advisory still reads
   outcomes, and what has been read limits what can be frozen afterwards.

## D-050 — The lead's answers (seats, deadline, GPU, quota runner) and the state of R0 (4 Oct 2026 11:18Z, Chair: Ushijima)

1. **Seats, as named by the lead.** Data: **Kageyama**. Learner: **Hinata**. Evaluator: **Asahi**. Live ops:
   **Daichi**. Council: **Tanaka** (GPT, auditor), **Sugawara** (Claude, mechanism), **Nishinoya** (GLM, probe).
   Rome's interim permission (D-048 §9) has lapsed: Asahi reported at 11:10Z with the cage arm preregistered (its
   P-A01) before Rome started it.
2. **Deadline.** The lead handles the final submission and its timing. The assumed date in D-046 §1 and its three
   freeze times are withdrawn; the Chair imposes no freeze. The 12-hour spacing between promotions and the rollback
   rule stay. The ladder's order stays; its target dates are dropped.
3. **GPU work runs on the Mac's shared memory (the lead's instruction).** Training may use Metal (PyTorch MPS) on
   the Mac. Macro §8's deferral of R7 and R8 "until a GPU returns" no longer holds on hardware grounds. What still
   holds:
   - the ladder's own conditions: R6 only by a Chair decision; R7 only if the accuracy-per-KB curve shows the trees
     saturating; R8 only if R6 plateaus for two iterations;
   - a GPU job is a heavy job: `build/learn/HEAVY.lock`, one at a time, panels first. It shares memory with the
     panels and the hub;
   - it needs a native Mac session. A Cowork VM cannot reach Metal, so the request to start the Learner natively
     stands;
   - the bot itself still runs on CPU within 30 M points per turn. Nothing changes at deploy.
4. **The second quota executor.** The lead does not know of one. It is `tools/hub/quota_runner.py`, a Windows Task
   Scheduler job ("JKS Automatic Match Runner", `Register-QuotaRunnerTask.ps1`) that requests battles every ten
   minutes. D-048 §5 is replaced by a check that needs nobody's memory: Daichi compares the server's battle history
   for our team over the last 48 hours with the hub's ledger. If no requested battle is missing from the ledger, the
   condition is met. Each job repeats the check before it dispatches a non-live arm, and pauses on any request it
   cannot explain. If Daichi finds one, it reports the times to the Chair.
5. **R0 is not passed yet; this is where it stands.**
   - Kageyama reports, on `r/kageyama` (BOARD 11:20Z): block rebuild identical to the engine's on 401,434 of 401,434
     blocks; encoder Python = C++ on 40,002 turns in 1,214 processes with 0 mismatches; labels equal to HB-1's on
     100 % of 75,306 Heartbreaker turns in 12 games; a leakage audit of 9 checks.
   - Kageyama also re-ran the 1.2.9 engine on 4 post-m2 server replays (Trophy, weakhold, Schooltime, Islands;
     87,830 turns) and reproduced each game turn for turn. That closes D-046 §2's open item "the server's engine"
     for those games. The corpus-wide map identity check is still open.
   - The Chair records the encoder, label and audit gates when three things hold: the branch is on `main`;
     Nishinoya has re-run the parity, label and audit tests from that branch and reported the same counts; and the
     split manifest is rebuilt. Kageyama's `kageyama-games-v1.json` used D-046 §3's set (Maze, Trauma, Trophy), which
     D-049 corrected. Version 2 uses **Autarky, Maze, Trauma**. Version 1 is not recorded.
   - The post-m2 decode was started natively by the lead (a writer appeared at 11:13Z). It overlaps Asahi's panel,
     which holds the heavy-job lock with 14 workers since 10:59Z. This is accepted once: the decode runs at nice 15
     under the panel's nice 10. Asahi lists any run timeout as missing and notes the overlap on its cards.
   - Asahi regenerated the four stale twins from `maps/live/` (autarky, default, dilemma, trophy; `maps/m2tr/`).
     Recorded when `r/asahi` is on `main`.
6. **Answers to Asahi's 11:10Z requests.** The charter is D-046. The engine is one binary across the three wheels
   (D-046 §2). Gate seeds are 1–3, the reserve is 4–5, and training rollouts use seeds ≥ 1000 (D-046 §3). The gate
   mode is `phase3` (D-046 §4.1), with the interval convention Asahi already uses.
7. **Numbering.** D-049 and the proposal index say the gate reading for P-2's confirmation will be frozen in
   "D-050". This record took that number. The gate reading, the rollback reference and the interval convention
   will be decided in **D-051**, after council round 1 closes at 13:00Z.
8. **Operating choices (added 11:35Z, after the lead said to make reasonable choices and ask only for what needs a
   human).**
   - **Chair cadence.** The Chair wakes itself in its own linked session about once an hour. The separate scheduled
     task stays disabled.
   - **Merges.** The Chair requests the merge of clean lane branches at each unit. Its check is: no `changed in
     both` section with a conflict marker, no forbidden path, no blob over 4 MiB that is not already on `main`. A
     plain search for `<<<<<<<` is wrong here: every copy of `atlas.hpp` contains that text six times, so the
     coherence task would skip every branch that adds a bot.
   - **One path for the BOARD.** `docs/hub/BOARD.md` is written only by appending to the file in the main checkout.
     No lane branch commits it. Reason: at 11:31Z the keeper refused to merge `r/asahi`, `r/tanaka` and
     `r/nishinoya` because each touched BOARD.md while the main tree's copy had uncommitted lines. They merged at
     11:35Z after a commit pass. Lanes with a worktree append to the main checkout's file, not their own copy.
   - **Native execution for the learning lanes.** One native executor, not one terminal per lane. Asahi's job daemon
     (`tools/asahi/jobd.py`, already running, already honouring the heavy-job lock) is extended to take jobs from a
     queue in the main checkout, `build/learn/queue/`, for scripts under `tools/learn/` and `tools/hinata/`, run from
     the main checkout. Asahi makes the change and reloads the daemon with its own `reload` job. Panels keep
     priority over training, and training over decodes. Python packages for training (lightgbm, xgboost, torch,
     scikit-learn, pandas, pyarrow, duckdb) go into `build/learn/venv` through a fixed allow-list job. If the reload
     cannot do this, Asahi says so and the lead is asked for one terminal command.
   - **Rules question.** The ladder proceeds on the assumption that training on public replays is allowed: the
     server publishes them through its API and the documentation states no restriction. If the organisers say
     otherwise, R2 and later stop and the Chair re-plans.
   - **Promotions.** The Chair promotes under D-046 §7 without asking, and notifies the lead.

## D-051 — Live ops: A/A job enabled, hub link, the unexplained requests; R0 items recorded (4 Oct 2026 12:22Z, Chair: Ushijima)

Numbering: D-050 §7 said D-051 would freeze the P-2 gate. Live ops was ready an hour earlier, so this record takes
the number. The council decisions (P-2's confirmation gate, the rollback reference, the interval convention) are
**D-052**, after the reviews close at 13:00Z.

1. **Enable requested battles for one job (answers Daichi 12:00Z).** Daichi may write the `enable` citing D-051 and
   submit the A/A job as sized: one arm (14585), dev opponents 545 and 752, the 17 `LIVE_MAPS_M2` maps, both seats,
   4 games per pair, 136 games, two replicates per (opponent, map, parity) cell.
   - Frozen objective: the difference between replicate 1 and replicate 2, cell bootstrap (cluster = opponent × map ×
     parity), 1,000 resamples, seed 7, 5th to 95th percentile. Expected: 0 inside the interval, width ≤ 0.25.
   - Stop rule: 136 games, or 6 hours, or any runtime fault, or a change of the live submission.
   - Reading: an interval that excludes 0, or a width above 0.25, means the paired report is not yet fit for a live
     screen; Daichi then diagnoses before any candidate job.
   - Every later job needs its own Chair record. No non-live arm is covered by this one.
2. **Hub link.** `r/daichi` (the `register.json` link item, 107 of 107 hub tests) is on `main` since 12:18Z. Daichi
   redeploys and links submission 14585 to `carthage-05-free-sprint`; the fingerprint `ebeba55f` matched the API
   name (Daichi 12:00Z).
3. **The unexplained requests.** Daichi found 7 unranked series (50 games) requested by our team between 2 Oct
   12:52Z and 3 Oct 02:42Z that are not in the hub's ledger, on a ten-minute grid that matches `quota_runner.py`,
   all played by 14585, none since. Something outside the hub was posting until 3 Oct 02:42Z. The likeliest source
   is the quota runner on the desktop that is no longer available; that is an inference, not a finding.
   - These are unranked requests. If the runner resumed during a candidate's seconds of activation, the candidate
     would play a few unranked games: no rating effect, and the replay header says which submission played.
   - Ruling, replacing D-050 §4's condition: a non-live arm may be dispatched when it passed the D-046 §4 gate, no
     unexplained request was seen in the previous 24 hours, and the job re-checks before each unit and pauses on a
     new one. The lead is told once, without a request to act.
4. **Monitor.** Daichi fixes the defect Tanaka found: `rating_at` takes a later snapshot when a game precedes the
   earliest one. Tanaka could not rebuild the 417-game census after the corpus backfill; the monitor freezes its
   input list (game ids and snapshot ids) with every published number.
   - 12:00Z read (ranked, post-m2, series bootstrap): since 2 Oct −0.029 [−0.059, +0.001] over 611 games in 125
     series; last 40: −0.069 [−0.154, +0.007]; Elo 1716, rank 83; Schooltime −0.45 [−0.51, −0.40] (35 games).
5. **R0 items recorded** (`docs/learning/ladder.md`):
   - **Item 3, encoder parity: passed.** Kageyama: Python = C++ on 40,002 turns in 1,214 processes, 0 mismatches,
     and 40,002 of 40,002 through the official helper. Nishinoya, on fixtures of its own: 1,549 turns in 37
     processes, 0 mismatches, helper 1,549 of 1,549. Gate: 1,000 turns bit for bit.
   - **Item 4, action labels: passed.** Kageyama: 100 % of 75,306 Heartbreaker turns in 12 games. Nishinoya: 100 %
     of 31,061 turns in 2 corpus replays, both sides. Gate: above 99 %. One convention differs from HB-1 by design:
     the sonar mask is the requested direction.
   - **Item 7, twins: done.** Asahi regenerated the four stale twins in `maps/m2tr/`; on `main`.
   - **Item 8, battles control and monitor: done.** Redeployed with dispatch off (Daichi 12:00Z); the monitor
     refreshes hourly.
   - **Item 10, audit note: delivered** (Tanaka, `docs/learning/reviews/D-046-tanaka.md`). The convention itself is
     frozen in D-052.
   - **Not yet:** item 1 (decode: 11,455 of 17,206 in-scope post-m2 games at 11:50Z, Nishinoya's census); item 2
     (manifest v2 on Autarky, Maze, Trauma); item 5 (the audit passes 9 of 9 on a fresh training set, but must run
     on v2, and `build/learn/kageyama/smoke.parquet` fails it and must be rebuilt or removed); item 9 (corpus-wide
     map check).
6. **P-2: Tanaka's hold is upheld until D-052.** No confirmation and no re-fit. Two reviews are in (Tanaka: amend
   and hold; Nishinoya: agree with G-amend). The decisive finding is Tanaka's: the 10:52Z fit trained on 539 games
   of the reserved test bucket and 555 of the validation bucket, and the confirmation code would re-fit Φ on a
   larger store while V0b stays frozen. Preparations that read no held-out label may start now:
   - Hinata: archive the source at 3138d107; export Φ's coefficients fitted on the same frozen rows (c958e8c7…);
     complete the confirmation code as Tanaka's review §4 lists (every cell, intervals, verdict, INCOMPLETE on a
     missing cell, one atomic claim, receipts kept).
   - Kageyama: in manifest v2, mark the series present in the frozen training rows as consumed by P-2; count, by
     map and by ranked or unranked, the held-out-map post-m2 games whose series has no game in those rows.

## D-052 — Council round 1 decided: P-2's confirmation, the rollback rule, the interval convention; cage screen held; map variants (4 Oct 2026 13:18Z, Chair: Ushijima)

Reviews read: P-2 from Tanaka (amend, hold), Sugawara (amend), Nishinoya (agree with G-amend, addendum 12:50Z);
D-048 §8 from Tanaka (and follow-up), Sugawara and Daichi; D-046 from Tanaka and Nishinoya. All three seats sat.

### A. P-2 (R1, value model): one confirmation, on these terms

1. **What is confirmed.** The artifact fitted at 10:52Z, unchanged. The source that produced it was edited one
   minute after the fit and is lost; the archived `tools/hinata/archive/v0_2920bb57.py` reproduces all 14 × 8
   coefficients and 35,948 of 35,948 out-of-fold predictions with zero difference (Hinata 12:43Z). That exact
   reproduction is accepted as the provenance. The comparator is Φ fitted on the same frozen rows (`fit-lq-phi`).
2. **What the development fit used up.** It trained on 4,705 train, 555 validation and 539 test-bucket games in
   1,777 series (Tanaka; reproduced by Kageyama on all 126,694 rows of manifest v2). Those series are marked
   `consumed_by: P-2` and are no longer a clean test for any value model. They stay clean for policy models.
3. **Population.** Binding: post-m2, in scope, decisive, **ranked** games on Autarky, Maze and Trauma whose series has
   no game in P-2's training rows: 1,328 games (435, 446, 447) in manifest v2. Reported beside it, never binding:
   all ranked held-out games, unranked clean, unranked, all. Clean series are mostly newer ones, so the clean and
   consumed tables are read side by side as drift, not as leakage (Sugawara).
4. **Gate.** Frozen in `docs/learning/proposals/P-2-gate-spec.D-052.json`, sha256
   `15d79683518cf704a8cb7680ef1fa55acd8bdaef2bc97b694f40db742ea0d07d`. It is Tanaka's corrected G-amend with two
   Chair choices:
   - whole-series bootstrap, one draw shared across cells and both models, 1,000 replicates, seed 7, linear
     percentiles; 5th-percentile ΔAUC > −0.01 in every binding cell; > 0 in round-limit r150, r250 and r400;
   - calibration: |slope_V − 1| ≤ |slope_Φ − 1| + 0.05 in every binding cell from r25;
   - round-limit r50: AUC_V ≥ AUC_Φ binds. The absolute 0.66 is reported and does not bind;
   - elimination r10 is report-only; any cell with fewer than 50 games in the binding population is report-only,
     fixed from counts before the claim;
   - INCOMPLETE, not PASS, on a missing or one-class binding cell, a non-finite metric, fewer than 990 valid
     draws, coverage under 95 % on any held-out map, or a claim or scorer hash that differs from the audited one.
5. **Release without another Chair record.** Hinata runs the one confirmation when all four hold: Tanaka's two
   defects in `p2_confirm.py` are fixed (PASS on a non-finite metric; a changed claim accepted) and the code reads
   this spec; Tanaka posts a pass line that names the scorer's sha256 and this spec's sha256; the 1,328 games are
   decoded, or the missing ones are listed with reasons and coverage is at least 95 % per map; the per-cell counts
   are posted. One claim, one score, the receipt kept whatever the outcome.
6. **Answers to dissent.**
   - Tanaka wants the 0.66 floor to bind. Not adopted. The macro defines that floor on leave-one-map-out over the
     round-limit maps, where P-2 measured 0.671 and Tanaka reproduced it. On two fixed maps and ranked games only,
     the level of AUC is mostly a property of the maps and of how evenly matched ranked opponents are. The paired
     clause carries the claim there; the absolute value is printed.
   - Sugawara asks for elimination r10 to be report-only. Adopted, before any held-out label is read: both models
     sit near chance there (0.54), the card predicts no effect, and Autarky alone carries the cell.
   - Tanaka: a model that ranks like Φ can still be recalibrated, so the old slope band was not unpassable. Accepted;
     Hinata withdrew the claim. The Chair's sentence to that effect in D-049 §4 is withdrawn too.
   - Nishinoya: a later change of model class on rows already read should cost a fresh fold set. Accepted as the
     rule for the next value card.
7. **What a pass will mean.** Sugawara's finding is adopted: every input of V0b is replay truth for both teams. It
   is a **privileged critic**: usable at training time (value targets, advantage weights, shaping, self-play), not
   as the search leaf. A pass closes R1 as the macro wrote it (diagnostic: the queen terms carry value). **R5 needs
   a value model on the legal encoder.** Hinata writes that card (V-legal: same logistic, encoder features, same
   rows and folds) after the decode, and reports ΔAUC(V0b − V-legal) per cell: the value of opponent information.
8. **Scoring.** The scored event is "the confirmation returns PASS under this spec". Forecasts on file nearest to
   it: Sugawara 0.55, Nishinoya 0.50, Tanaka 0.20 (for a stricter gate). Each seat may file one number for this
   exact event before the claim; otherwise those are scored.

### B. Rollback rule (replaces D-046 §8's first clause)

- **Rule.** One look, at the first series boundary at or after 40 ranked games of the promoted submission. Roll back
  when the mean residual of those games minus the mean residual of the replaced submission's last 120 ranked games
  (extended to a series boundary) is below −0.08, and the 95th percentile of that difference is below 0. Bootstrap:
  whole series, the two windows resampled independently, 1,000 replicates, seed 7.
- **Residual.** Score minus Elo expectation, with our own rating fixed for both windows at its value when the new
  submission was activated, and each opponent's rating at game time. Tanaka showed that different anchors for the
  two windows create a spurious difference of 0.12 on identical play. Games before the first rating snapshot carry
  no expectation and are excluded, not imputed.
- **Frozen inputs.** The game lists, attribution by replay header, and snapshot ids of both windows are written
  to `docs/learning/live-inputs/` before the look.
- **Crash or disqualification:** immediate rollback, unchanged. D-048 §7 (not for 14585) stands.
- **Known weakness, accepted.** From Daichi's simulation of a close variant: an equal candidate is rolled back in
  about 8–9 % of cases; a true −0.10 is caught in about 38 %, a true −0.20 in about 77 %. Tanaka notes these rates
  were not computed for this exact rule. Daichi re-runs the simulation on the rule as written and reports; that
  report is not a gate. After the look the Chair reads the monitor at 120 games. A sequential series test may
  replace the single look by a card (Sugawara).
- No forecast is scored on this item; it is a convention, not an event.

### C. Interval convention for local gates (freezes D-046 §4.3)

- Cluster = **map × opponent**, with both seats and all declared seeds kept together and candidate and parent paired
  inside the cluster: 136 clusters on the 17-map pool. 1,000 replicates, seed 7, 5th percentile by linear
  interpolation, on a fixed ordered input manifest. This is Tanaka's amendment; the two seats of one map and
  opponent are not shown to be independent.
- Every card also prints the directional key (map × opponent × seat) as a sensitivity, and the per-map table.
- The 5th percentile is a one-sided 95 % bound. Neither convention is an interval for unseen maps.
- Correction to D-046 §4.2: three seeds give lower expected precision than five. They do not guarantee a lower
  bound that is lower on every sample.
- Asahi changes `tools/asahi/card.py` before the first nominee gate. Screens already printed stay as printed.

### D. Cage C+D with E = 0 (Asahi's P-A01): HOLD, not advanced

- Result, seed 1, complete panels. The harness is deterministic: Asahi's H-KZ12 k = 0 copy reproduced the parent's
  winner and round count in 272 of 272 pool games, so a difference between arm and parent comes from the arm.
  - Schooltime: wins 15 of 16 against the parent's 14; queen alive at the round limit **4 of 15** against 0 of 16.
    The card's bar for support was a rise of at least 6. Rome's package with a reserve kept 11 of 12 (E = 1) and
    13 of 13 (E = 3). The reserve, not C+D, is what keeps the caged queen.
  - Pool: 232–40 against 226–46, +2.2 points [−0.4, +5.2]; gen 346–118 against 341–123, +1.1 [−0.7, +2.8]
    (directional clusters, 5th to 95th percentile). Economy flat.
  - Off-target, against the prediction of zero firings: invalid deaths 0 → 8.07 per 1,000 dragon-turns on the pool
    and wall deaths 7.21 → 1.44. Rule C fires wherever a dragon is sealed, on every map.
  - Portals: 10–6 against 12–4 on the pool map, and 7–9 against 13–3 on its twin. Eight games lost on 32.
- Verdict by the card's own rule: **hold**. Not advanced to seeds 2–3 (D-046 §4.5): the target was missed and the
  off-target prediction was wrong.
- Next, one change per arm:
  1. Asahi appends a diagnosis to the card from the replays it has: where and when the queen dies in the 11
     Schooltime games; firings of C per map; what C does on Portals.
  2. Sugawara writes the card for the next arm from Shenzhen's units 9–13: the reserve applied **only while our
     queen is caged**, doses 0, 1 and 3, and whether C should be limited to the cage. Asahi builds and screens it.

### E. Two live maps have a second variant (Kageyama, R0 item 9)

- Of 38 map texts in 26,572 post-m2 games, 36 match `maps/live/`. Prisoners Dilemma starts with 10 dragons in 679
  of 1,376 games. Schooltime has four kelp edges open in 882 of 1,860 games. The cage exists only in the sealed
  variant, so the cage rule addresses about half of live Schooltime games.
- Kageyama adds the two variants as `maps/live/schooltime_open4.map` and `maps/live/dilemma_10.map`, built from
  replay text and template beds, each checked by reproducing one server game turn for turn. Asahi adds them to the
  pool (19 maps, 152 clusters) and runs the parent on them before the first nominee gate. This corrects the panel
  to what the server plays; it is made before any gate has run. R0 item 9 is then closed.
- Daichi splits the Schooltime and Prisoners Dilemma residuals by variant in the monitor.

### F. The native executor is now the critical path

- The decode stopped at its time limit at about 12:03Z with roughly 4,800 post-m2 games queued. P-2's population is
  58 % decoded. The teacher rows for R2 need the 1.2.9 wheel in a native environment.
- Asahi puts the executor extension (D-050 §8) ahead of the remaining H-KZ12 runs: the learn queue, and an
  environment with unswbc 1.2.9, pycapnp, lightgbm, xgboost, torch, scikit-learn, pandas, pyarrow and duckdb.
- Until it exists, the lead is asked to re-run the decode once.

## D-053 — R0 passed; H-KZ12 k = 16 nominated for the first full gate; the gated-reserve card rejected; cage work parked (4 Oct 2026 14:28Z, Chair: Ushijima)

### A. R0 is passed

All ten items of the R0 checklist are closed (`docs/learning/ladder.md`). The macro's offline gate holds: encoder
Python = C++ bit for bit (40,002 turns; 1,549 on independent fixtures), labels above 99 % (100 % of 75,306 and of
31,061 turns), leakage audit 9 of 9 on manifest v2, re-run by Nishinoya.

- **Item 1, decode: done.** 19,754 of 19,754 in-scope post-m2 games are decoded (Kageyama 13:55Z; Nishinoya's census
  agrees).
- **Item 9, maps: closed with a stated limit.** 36 of 38 post-m2 map texts match `maps/live/`. The two variants
  (Schooltime with four open edges, Prisoners Dilemma with ten dragons) have their own bed layouts, which the server
  redacts: re-runs from replay text plus template beds diverge on 4 of 4 games of each variant, by r23–28 and
  r13–38, while template games reproduce 4 of 4 (Kageyama). **D-052 §E is withdrawn**: exact variant files cannot be
  built, the pool stays at 17 maps and 136 clusters, and local panels cover one variant of those two maps. The
  variants are read from live games (Daichi's monitor split). Kageyama may file a card for approximate variant
  files (bed cells from spawns, checked against pearl income per round). Teacher rows on variant games carry
  `cd_known = 0`.
- R1 and R2 are open. R1 waits on its confirmation; R2 waits on Hinata's card and on the teacher rows.

### B. P-2: release status

- Decode coverage of the binding population is 1,327 of 1,328 (Nishinoya, unaudited). The frozen list is manifest
  v2. Game 1044626 is in scope in v2 and out of scope in the store's table; it is listed as missing with that
  reason, and is not dropped from the denominator.
- Still needed before the claim: Hinata's two scorer fixes and the D-052 spec fields; Tanaka's pass line with both
  hashes; the per-cell counts.
- Forecasts for the exact event, filed before the claim, used for scoring: Tanaka 0.40, Sugawara 0.50,
  Nishinoya 0.50.

### C. P-3 (Sugawara's `P-sugawara-01-cage-gated-reserve.md`): rejected as written; cage work parked

- The card gates Rome's reserve on the map being 60 × 40, which only Schooltime is. Tanaka rejects it: a dimension
  that identifies one map is map identity, and the common hard rule ("no map identity in any bot: structure only")
  and D-033 forbid it. Upheld. D-052 did not waive the rule and the Chair does not waive it now.
- The card's mechanism finding is kept: non-queens cannot legally observe that our queen is caged (7 × 7 vision,
  empty memory at birth, and the sealed queen's sonar stops at the cage kelp).
- New evidence changes the priority. Daichi's split of our ranked Schooltime games by variant: with the cage open,
  −0.515 [−0.565, −0.466] over 27 games; with the cage, −0.436 [−0.507, −0.353] over 24. We lose both about equally.
  The cage is therefore not what loses Schooltime, and a cage-only rule can move at most the sealed half.
- Decision: no further cage arm is queued. The E = 0 screen stays HOLD and Asahi's diagnosis request is dropped. A
  later card may reopen the question with a trigger that every dragon can observe.

### D. H-KZ12 (Asahi's P-A02): k = 16 goes to the full gate

- Screen, seed 1, complete panels, directional clusters, 5th to 95th percentile: pool Δwin +1.5 [+0.4, +2.6] at
  k = 4, +0.7 [−0.7, +2.2] at k = 8, **+2.6 [+0.7, +4.4] at k = 16**; gen flat (−0.2 [−1.1, +0.7] at k = 16). Wall
  deaths on classes C and E fall by 4.86 per 1,000 at k = 16 [−8.16, −2.08]. The preregistered queen endpoint did
  not move at any dose (queen alive at the end on Trauma, Portals, Maze and weakhold: 0, 0 and 1 of 64 against 0 of
  64). pearls@50 falls by 0.75 at k = 16.
- Reading: the veto does what it is built to do (fewer fatal pocket entries) and the queen still dies of other
  causes. The win gain is not through the mechanism the card named. It is taken to a gate because the pool lower
  bound is above 0 at two of three doses, the Evaluator is idle, and a first nominee exercises the whole deploy
  path.
- **Nominee:** `asahi-05-kz12-k16`, parent `carthage-05-free-sprint`, tagged `temporary`; learned replacement target:
  the R4 block "body-conditioned entry capacity".
- **Frozen objective.** The dose was chosen on seed 1, so the gate is computed on **seeds 2 and 3 only**; seed 1 is
  printed beside it. Thresholds as D-046 §4: pool expected-score lower bound > 0; gen > −0.02; `econ~` > −0.03 on
  both panels; units@100 and total@100 ≥ −0.02; tier-2 guard; deploy limits. Intervals as D-052 §C (map × opponent
  clusters, 136 on the pool). The queen columns are reported and do not gate.
- **Stop rule.** One run of parent and nominee per seed. No other dose is gated, whatever the result. INCOMPLETE on
  any missing fixture.
- **Council.** Each seat files one number, P(the gate returns pass), on the BOARD before Asahi posts the card.
  The Chair's own expectation, not scored: about 0.35, because a dose picked as the best of three on one seed
  usually shrinks.
- If it passes: registry entry REG-002, upload without activation, and a live screen against 14585 after the A/A
  job has reported (D-046 §7).

### E. The queen's real exposure: a card for H-KZ26

- Kanazawa's out-of-sample result stands as the largest measured queen lever: our queen is struck in 64 of 635
  reach opportunities (10.1 %) against 49 of 2,768 (1.8 %) for field queens, in 201 fresh games of ours. Asahi's
  H-KZ12 reading points the same way: entry avoidance does not buy queen survival.
- Sugawara writes the card: a queen-only veto on stepping within reach of a visible enemy head, reach
  B(L) = ⌈L/4⌉ + L − 2 with no cap, margin m ∈ {off, 0, 1}, fallback to the largest Cb when every step is vetoed.
  Sources: Kanazawa units 11–16 and wrap-up, Seoul's wrap-up, Himeji H30–H32. It adds information the search does
  not use, it is legal (visible enemies only), and it has no map identity. Asahi builds the dial after the card
  has a decision.

### F. Standing answers and requests

- **Rollback rule:** Daichi simulated D-052 §B as written (4,000 simulations per cell from 14585's 849 ranked games
  in 172 series): an equal candidate is rolled back in 7.3 % of cases; a true −0.10 in 36.6 %; a true −0.20 in
  78.1 %. A placebo on 14585's own sequence fired 9 times in 138. The rule stands as written.
- **Asahi's open questions, answered again:** gates run on the engine with hash 26e68680… (wheels 1.2.3, 1.2.5 and
  1.2.9 carry it; D-046 §2). Gate seeds are 1–3, the reserve is 4–5, training rollouts use seeds ≥ 1000 (D-046 §3).
  Held-out maps concern training data, not the panels.
- **Asahi's order of work:** the native executor extension (D-050 §8, D-052 §F); the cluster change in `card.py`
  (D-052 §C); parent and k = 16 on seeds 2 and 3; then the H-KZ26 dial.
- **Hinata:** file the R2 card (behaviour-cloning direction head on Kageyama's teacher list v1 and encoder v1) and
  the V-legal card, so that council round 2 can run while the teacher rows are built.

## D-054 — P-2's frozen population; the queen reach veto approved for a screen; council round 2 opened; the Evaluator is idle (4 Oct 2026 15:36Z, Chair: Ushijima)

### A. P-2: what "usable" means, and the release

- Nine of the 1,328 binding games are flagged out of scope in the live store. Kageyama found the cause: the store
  recomputes `in_scope` from the latest ladder snapshot, and team 28 has since left the top 50. Neither table is
  wrong for its own time.
- **Ruling.** The population is frozen by manifest v2. Scope is read from the manifest and never from the live
  store. A binding game is usable if it is decoded. That gives 1,327 usable games; game 1044626 was never decoded
  and is listed as missing. D-053 §B stands; the figure 1,319 came from a filter on the live flag and is not used.
  If any of the eight decoded games cannot be loaded, Hinata lists it as missing with the technical reason; coverage
  stays above 95 % on every map either way.
- Tanaka's new defect is upheld: the scorer must pin the usable game ids and the expected membership per checkpoint
  before the claim, exclude the frozen missing ids, and return INCOMPLETE on any unexplained loss or new row.
- **Release, unchanged in form:** Hinata's revision with the pinned list; Tanaka's pass line naming the scorer's
  sha256 and the spec's (15d79683…); then one claim and one score. Tanaka verified the earlier repairs on revision
  ea3b5ef7 (18 of 18 probes return INCOMPLETE; changed claim, scorer, spec and predictions rejected).
- Per-cell counts (Hinata, outcome-free): no binding cell is under 50 games; elimination r10 stays report-only.

### B. The k = 16 gate (D-053 §D): forecasts and what the card must print

- Forecasts filed before the card: Sugawara 0.35, Nishinoya 0.40, Tanaka 0.35.
- All three found the same thing in the seed-1 rows: the pool gain of +7 games in 272 is entirely Weakhold (15–1
  against 8–8); the other 16 maps net 0. Tanaka's bootstrap of seed 1 on the D-052 clusters gives +2.6 points
  [+0.4, +5.1] on the pool and −0.2 [−1.1, +0.4] on gen.
- Added to the card, report-only, named before the run (D-046 §4.6): Weakhold as the target stratum, per seed; the
  pool without Weakhold; vetoes and fallbacks per 1,000 queen decisions on Weakhold. The gate letter is the pooled
  one of D-053 §D.
- The gate has not started. See §E.

### C. P-4 (`P-sugawara-02-hkz26-queen-reach-veto.md`): approved for a screen

- One switch on REG-000: the original queen drops every candidate action whose final head cell is within reach
  B(L̂) + m of an enemy head visible at its own turn start; B(L) = ⌈L/4⌉ + L − 2; m ∈ {off, 0, 1}; largest-Cb
  fallback. It covers sprints and splits. L̂ = visible length + 2 for each cut end; no new memory.
- Tanaka's amendments are part of the card, accepted by the author: the event-time labeller is frozen and
  validated before the parent's games are labelled; the predicate covers every selection path; the ratio is
  strike deaths over alive queen-rounds with a paired bootstrap, INCOMPLETE under 900 valid draws; the food guard is
  pearls per alive own dragon-turn.
- **Frozen objective (the card's):** at m = 0, support if the strike hazard is at most 0.70 of the parent's with the
  all-cause queen hazard not up and food per turn above 0.90 of the parent's; refute at 0.90 or more, or all-cause
  hazard up, or food down by 10 % or more. Stops: golden parity at m = off; fewer than 5 firings per 1,000 means
  the dial did not reach; fewer than 10 parent strike events on the panels means no local exposure, and the card
  goes to a read of live games with no panel extension. Seed 1, both panels.
- Owner: Asahi builds and screens it after the k = 16 gate. The labeller is Asahi's, on Kageyama's exact blocks.
- Scored event: the screen returns support at m = 0. Forecasts: Sugawara 0.35 (revised from 0.40), Tanaka 0.30.
  Nishinoya may file a number before the run.
- The simpler alternative named in the card (correct the parent's soft reach to B(L) without a mask) is not
  queued; it becomes the next dose if the mask shows support.

### D. Council round 2: P-5 and P-6, reviews due 17:00Z

- **P-5** = `P-hinata-03-R2-P1-bc-direction.md` (R2, the cloned direction prior). **P-6** =
  `P-hinata-04-R1b-V-legal.md` (the value model on legal features; R5's prerequisite). Sugawara has reviewed both
  (amend; agree with two amendments). Both are Claude cards, so each needs Tanaka's and Nishinoya's review.
- **A correction by the Chair, for the reviews to address.** The macro defines R2 on "hb1's features plus the queen
  block". D-053 §F wrote "encoder v1", and Hinata followed that. Hinata's card notes the cost: HB-1's strongest
  features were scores per candidate direction, which encoder v1 does not compute, and HB-1 found strength steep in
  accuracy (0.73 → 7.5 % wins, 0.854 → 55 %). The Chair's leaning, open to the reviews: the R2 artifact is trained
  on encoder v1 **plus** hb1's per-candidate features, computed for the teacher rows by the bot's own C++
  extractor so that training and deployment share one implementation; the encoder-only model is fitted on the same
  rows as a comparison. Kageyama says what that costs.
- Other points for the reviews: which offline gate binds (the macro's accuracy ≥ 0.83, or the paired comparison with
  the parent's prior, which Sugawara expects to pass almost surely); Sugawara's amendments (train only on rows with
  known bed timers; the three-class against four-class slot; the flip rate of the parent's decisions as a
  report, with under 1 % meaning no panel).
- Until the Chair decides (D-055), nothing is fitted on the teacher rows. Kageyama's 120-game development set and
  plumbing runs may continue.

### E. The Evaluator has not acted since 13:50Z

- Asahi's status still lists questions answered in D-046, D-050 and D-053. No job has run since 13:47Z; the
  heavy-job lock is free. Three requests are waiting: the native executor extension, the cluster change in the
  card code, and the k = 16 gate. The R2 data (1,925 teacher sides) also waits on the executor.
- The Chair cannot reach Asahi's worktree or queue. The lead is asked once to wake that session and point it at
  D-053 §F and this record.
- A/A live job: 68 of 136 games verified at 15:28Z, 0 runtime faults.

## D-055 — Live-first: the first live screen is ordered; R2 and V-legal cards approved; A/A closed (4 Oct 2026 17:02Z, Chair: Ushijima)

### A. The live bot is not yet under experiment. That changes now (the lead's instruction, 16:56Z)

- State at 17:00Z: submission 14585 has been live, unchanged, since 2 Oct 04:22Z. No candidate has been uploaded
  in Phase 3. The only requested battles were the 68 games of the A/A job. Dispatch is disabled. The hub executor is
  in shadow.
- Why it stood still: D-046 §7 and D-048 §4 put the full local gate before any upload, and the Evaluator has run
  nothing since 13:47Z.
- New evidence against waiting for local gates: about 15 % of live ranked games run on bed layouts our templates
  lack (Kageyama's oracle reproduced 97 of 118 server games; the 21 failures are on Slithery Fight, Schooltime,
  Queen of Spades, Prisoners Dilemma and Devil, which carry 29.8 % of the ranked stream; Nishinoya's probe,
  unaudited). Local panels also play a zoo, not the ladder. Server games cost quota, not Mac CPU (macro §8).
- **Ruling: live screens are the first evidence for a candidate, and the full local gate is no longer a
  prerequisite for an upload or a live screen.** A candidate is eligible for upload without activation and for a
  live screen when all of these hold:
  1. it is registered (`docs/learning/registry.md`) as one switch on a registered parent;
  2. the switch at its off value reproduces the parent (golden parity);
  3. complete seed-1 panels with zero runtime errors, pool point estimate ≥ 0 and gen ≥ −0.02;
  4. CPU probe including turn 0 under 30 M points, zip at most 4 MiB.
  This replaces the first condition of D-048 §4 and of D-051 §3. The other guards stay: blackout, no ranked series
  in flight, restore in `finally`, windows logged, pause on a human activation or an unexplained request.

### B. Live screen LS-1: `asahi-05-kz12-k16` against 14585

- **Arms:** 14585 (live) and `asahi-05-kz12-k16` (REG-002). It meets §A: k = 0 parity on 272 of 272 games; seed-1
  pool +2.6 points, gen −0.2; maximum 10.4 M points per turn on the lineage's probes, to be re-probed on this
  build with turn 0.
- **Before upload (Daichi):** write the candidate manifest for the bot (authorised, as the director did for
  carthage-05 in D-042); build the archive from the committed tree, not from the main working tree, where the
  13 MB model header of this bot is currently a 52-byte symlink; check the archive holds the real header and that
  the sandbox probe passes; upload with `activate: false`; verify the fingerprint in the API listing.
- **Roster, fixed by rule before dispatch:** the three teams 14585 met most often in ranked games over the last
  48 hours, among teams with an active submission and a rating within 100 of ours; ties go to the most recent.
  Daichi names them in the job note. No dev opponents.
- **Size:** each opponent × the 17 maps × both seats × one game per arm = 34 matched pairs and 68 games per
  opponent; 102 pairs, 204 games.
- **Frozen objective:** the mean paired difference in score, candidate minus incumbent, over matched (opponent, map,
  seat) cells; cluster bootstrap over opponent × map (51 clusters), 1,000 resamples, seed 7, 5th to 95th
  percentile. Missing cells are listed and not counted.
  - **Pass** (eligible for promotion): at least 60 matched pairs, 5th percentile > −0.02, mean > 0, and no more
    runtime faults or timeouts than the incumbent.
  - **Reject:** mean ≤ 0, or 95th percentile < 0.
  - **Hold:** anything else. One extension is declared now: two more opponents by the same rule (68 more pairs),
    then one final read. No other extension.
- **Printed beside it:** per map; Weakhold as the target stratum (all of the seed-1 gain came from it); the five
  bed-variant maps flagged.
- **Stop:** 204 games (340 with the extension), 8 hours, any runtime fault of the candidate, a change of the live
  submission, or an unexplained request.
- This record is the enable for LS-1. Daichi reports the paired table; the Chair decides promotion.

### C. Promotion rule, amended (D-046 §7)

A candidate is promoted by a Chair record when: it is eligible under §A; its live screen passed; no error or
timeout rise; 12 hours since the last promotion. If the full local gate has finished by then and failed, the
Chair does not promote. If it has not run, it runs afterwards as confirmation and can trigger a rollback record.
After activation the rollback rule of D-052 §B applies, and the Chair reads the monitor at 120 ranked games.

### D. The A/A job (D-051 §1): closed

- 68 of 136 games ran, all against dev team 545; the 68 against dev team 752 were rejected because 752 has no
  active submission. The split-half difference is +0.034 [0.000, +0.103] over 29 cells. It passes the frozen
  objective in form.
- It says little: 14585 scored 1 of 68 against 545, so the difference was measured at the floor. It is not re-run.
  LS-1's matched design measures its own noise, and Daichi prints the share of cells where the two arms differ.

### E. P-5 (R2, the cloned direction prior): approved as amended by all three seats

- **Feature set.** Encoder v1 plus the queen block plus HB-1's relative per-candidate scores, the latter computed by
  the bot's own C++ extractor so that training and play share one implementation. A hashed allow-list is enforced
  by the loader; W, H, x, y, xn, yn and any other map identity are refused. The encoder-only model is fitted on
  identical rows as the comparison. If the extractor cannot run on teacher rows, encoder-only binds and the card
  records it as the weaker variant. This corrects D-053 §F's wording; the macro's R2 row stands.
- **Rows.** Train only on rows whose blocks come from the engine oracle (`blocks_src = oracle`); the dropped share
  is printed per map (on the development set: Queen of Spades 72 %, Slithery 68 %, Schooltime 43 %, Prisoners
  Dilemma 43 %).
- **Offline gate.** The paired comparison with the parent's prior binds: P1's accuracy minus the HB-1 prior's on the
  same rows, whole-series bootstrap, 5th percentile > 0, on Tanaka's series-clean cohort (115 ranked post-m2 games
  of the ten teacher teams on Autarky, Maze and Trauma in 85 series; frozen by Kageyama with its oracle coverage
  before any label is read). Accuracy ≥ 0.83 is printed and does not bind. Development falsifier: series-held-out
  accuracy under 0.75. The 497-game read and leave-one-map-out are descriptive.
  Accuracy here is conditional on a forward, right or left teacher move, with the argmax over the three renormalised
  probabilities; the four-class figure is printed beside it. The 0.75 stop uses the same projection, and its row and
  series counts are stated before fitting (Tanaka, 16:57Z).
- **Slot.** P1's forward, right and left probabilities are renormalised over those three; a reverse first step
  keeps the parent's value. Flip rate and entropy are printed, with no cut-off (Tanaka; Sugawara withdrew the 1 %
  stop). The panel and live screens use λ ∈ {0.5, 1}.
- **Where it runs.** Teacher rows and the fit may be built in the lanes' cloud containers, as Kageyama built the
  120-game development set. The native executor is not a prerequisite for the first R2 artifact. Every run has an
  immutable manifest (rows, teachers, code, features, parameters, fold keys).
- **Scored event:** the binding offline gate passes. Forecasts for the amended card: Sugawara 0.70, Tanaka 0.60,
  Nishinoya 0.55. (The author's is 0.55.)
- Owner: Hinata, with Kageyama for rows and the extractor. After the offline gate the bot goes to §A's
  eligibility checks and to a live screen; the seed-1 panels come from the Evaluator when it runs.

### F. P-6 (V-legal): approved as amended

- Same logistic class on the legal encoder scalars, P-2's rows and folds. ΔAUC(V0b − V-legal) is a paired
  predictive diagnostic: not a price of information and not a guaranteed bound (Tanaka, Nishinoya). Per cell:
  speaker strata, the share of non-queen speakers, ΔAUC on queen-speaker rows only, and the pooled view. Claims for
  R5 are limited to queen-speaker rows. The held-out read is one look at a whole-series-disjoint population of games
  played after P-2's claim, with frozen V0b, Φ and V-legal on identical rows.
- Scored events and forecasts: no falsifier triggered: Sugawara 0.80, Tanaka 0.80, Nishinoya 0.80. V-legal at
  least Φ at round-limit r50: 0.20 from each.
- Owner: Hinata. It runs after the R2 teacher rows.

### G. P-2: the release audit is in its fourth round

- Revision 3 (sha bb51e1bb…) pins 22,305 rows in 3,305 games and reproduces 1,327 usable of 1,328. Tanaka holds
  it for one more hole: a pinned game with a missing or invalid result is treated as an explained loss. Upheld.
- Request to Tanaka: with the next review, list every remaining acceptance condition for the scorer in one place,
  so that the following revision can be the last. The confirmation itself is unchanged (D-052 §A, D-054 §A).

## D-056 — LS-1 is running: ruling on its objective, the upload defect, and the standing live loop (4 Oct 2026 18:13Z, Chair: Ushijima)

### A. State at 18:10Z

- **LS-1 dispatched at 17:42Z** (job 5ed81ad3e1f3). Arms: 14585 and submission **16979**
  (`LV-asahi-05-kz12-k16-0cf975af-ai`, fingerprint 0cf975af, zip 3.74 MiB, built from main 593810d14 with the real
  13 MB header). CPU probe (1.2.9 sandbox, seed 1, 6 live-map games and big_empty): maximum 10.6 M points per turn
  over 106,507 turns, round 0 at most 7.13 M, no faults. Roster by the rule, from 800 ranked games of 14585 in 48
  hours: teams 716 (35 games), 98 (25) and 347 (25); team 78 excluded (rating 145 below). Extension: 919 and 351.
  20 of 204 games played.
- **P-2's scorer is released** (Tanaka 17:55Z: revision 4, sha 0d0d1b7a…, spec 15d79683…). One claim and one score
  remain, Hinata's. Forecasts stand: Tanaka 0.40, Sugawara 0.50, Nishinoya 0.50. D-055 §G is satisfied; no revision 5.
- **R2:** Tanaka verified the support before any fit: 189,630 oracle moves (188,250 forward, right or left; 1,380
  reverse), 97 games, 49 series, 5,315 queen moves, five folds with no series in two folds. The development fit is
  Hinata's to run.
- **Asahi is working again.** At 18:10Z its daemon runs the P-4 panel (m = 1) with the strike probes, the card, and
  the parent and k = 16 on seeds 2–3 queued. Three commits on `r/asahi`: `card.py` with map × opponent clusters
  (D-052 §C), the learn queue in the daemon (D-052 §F), the P-4 dial, and the real model header in place of the
  symlinks in asahi-02 to 05. H10 is closed.
- **Chair actions since D-055, recorded here:** Hinata's scheduled task moved from two-hourly to hourly (17:12Z);
  R2 put ahead of the P-2 scorer in the Learner's order; the redeploy of `tools/hub/battles.py` (rejected-request
  counts) approved (17:08Z). The Chair's manual fire of Daichi's task at 17:05Z ran without the Mac and did nothing.

### B. Upload defect: the server activates a submission on upload

- 16979 was the active submission from about 17:33Z to 17:40Z without a promotion record. `submit.json` with
  `activate: false` does not prevent it, and `submit_check` did not restore the previous submission. Daichi
  restored 14585 at 17:40:00Z and cancelled the job that had captured the wrong active id. Ratified.
- D-055 §B ordered "upload with activate:false" and did not foresee this. The fault is in the hub path.
- **Ruling:**
  1. No upload until `submit_check` reads the active id before the POST and re-activates it afterwards in
     `finally`, as `request_batch` does, with a test. Daichi builds it; the Chair merges; the redeploy is approved
     by this record.
  2. An upload is made only outside the blackout and with no ranked series of ours in flight.
  3. Daichi lists any ranked game played by 16979 in that window. Such games are excluded from 14585's monitor
     and from any rollback read (D-052 §B), and are not LS-1 data.

### C. LS-1 objective: ruling on the council's objections

- **Timing.** Sugawara's amendment was posted at 17:29Z, before dispatch; Daichi saw it after enabling dispatch at
  17:42Z. Nishinoya (17:52Z) and Tanaka (17:56Z) wrote after dispatch. This ruling is after dispatch.
- **Disclosure.** At 18:01Z the Chair read `hub-state/battles/index.json` to check the job. The index prints a
  running paired figure (10 pairs, one opponent). The ruling is therefore not blind. It only adds conditions to a
  promotion and removes none.
- **Upheld:**
  - The frozen rule passes on one favourable pair and 101 ties (mean +0.0098, interval [0, +0.029]); under a null
    switch it passes about 0.16 to 0.33 of the time (Sugawara's simulation, peer evidence; Tanaka reproduced the
    one-pair case).
  - The local seed-1 census is 9 positive, 2 negative and 261 tied pairs of 272 (4.0 % discordant, in 9 clusters;
    Tanaka). LS-1 should expect about four discordant pairs in 102.
  - A pair-level sign test is not size-controlled, because the two seats share an opponent × map cluster (Tanaka).
- **Ruling:**
  1. LS-1's verdict is reported under the frozen rule of D-055 §B and keeps that label. It is read as
     non-inferiority with a positive point estimate, not as evidence of superiority.
  2. A matched pair counts only when both games met the same opponent submission id. Mixed-version pairs are
     missing and are listed with the reason. This is a data rule and applies to the frozen read too.
  3. Printed beside the verdict: positive, negative and tied pairs; each cluster's summed difference; the number
     of non-zero clusters; the pair-level sign p as description only.
  4. **Promotion needs more than the frozen PASS.** Among opponent × map clusters with a non-zero summed
     difference, positive against negative clusters must give a one-sided exact sign test of p ≤ 0.075 at the look
     where it is read. There are two looks: 102 pairs, and 170 pairs after the extension (joint size at most 0.15).
     Fewer than four non-zero clusters at a look means no promotion at that look. (4–0, 5–0, 6–1 and 8–2 qualify;
     5–1 and 7–2 do not.)
  5. The extension runs if the frozen rule says HOLD, or says PASS without meeting item 4. The label at 102 pairs
     stays as recorded. A REJECT at 102 pairs stops the screen.
  6. If the final look has fewer than four non-zero clusters, the screen is recorded as **not resolvable at this
     size**. k = 16 is then decided by the local gate on seeds 2–3 (D-046 §4, Asahi's queue), and promotion needs
     that gate to pass.
  7. Daichi keeps dispatching. No lane quotes a running paired figure; Daichi reports at the two looks only.
- **Forecasts for the frozen-rule PASS, including the extension:** Sugawara 0.50 (17:29Z, before dispatch; scored).
  Nishinoya 0.45 (17:52Z, after dispatch, before outcomes; scored and flagged). Tanaka 0.45 (17:56Z; its author
  declares it not a calibration entry; not scored). The seats' numbers for Sugawara's amended rule (0.25, 0.30) are
  on record and not scored, because item 4 is a different rule.

### D. The standing live loop (the lead, 18:00Z: does the setup choose opponents, gather data and update in response?)

Answer on record: opponents are chosen by one fixed rule, data is gathered, and nothing yet updates from either
without a Chair record. From here:

1. **Standard screen, version 1 (LS-std-1), for every screen after LS-1.** The unit of inference is the opponent ×
   map cluster. Pairs are matched on the opponent's submission id. Two looks are declared before dispatch.
   Promotion-grade evidence at a look: mean paired difference > 0, cluster-bootstrap 5th percentile > −0.02, and
   the cluster sign test of §C.4 at p ≤ 0.075. Fewer than four non-zero clusters at the final look: not resolvable.
2. **Sizing from the discordance census.** Before dispatch, the candidate's local seed-1 census (share of pairs
   where the arms differ, by map) fixes the size and the cells. A screen must expect at least 12 non-zero
   clusters. If the full grid cannot reach that within 340 games, the screen is **targeted**: the maps (and
   opponents, where known) on which the switch changes games, declared before dispatch. Its estimand is that
   stratum; harm elsewhere is watched by the post-activation monitor and the rollback rule (D-052 §B).
3. **Roster classes,** named before dispatch, drawn from Daichi's live table by rule:
   - band: the teams met most in ranked play over 48 hours within 100 rating (LS-1's rule);
   - loss: teams within 150 rating with at least 10 ranked games against us in 48 hours and the lowest score
     minus expectation;
   - top: the current top ten.
   A candidate's first screen uses band. A second screen of the same lineage uses loss, and replaces any opponent
   whose clusters were all ties in the first.
4. **Candidate queue.** A registered candidate that meets D-055 §A is screened in queue order. This record is the
   standing enable, subject to §B. Daichi posts class, roster, cells and size before dispatch; the Chair may veto.
   One screen at a time. Queue: (1) `asahi-05-kz12-k16` (running); (2) the queen reach veto (P-4) at its best
   dose, if its seed-1 panels meet D-055 §A; (3) the first R2 bot after its offline gate.
5. **Targeted data games (TD-1).** Purpose: the top ten's play on positions our own bot creates, and our losses,
   for the cloned prior, the value model and analysis. One arm (the live submission; no activation change):
   top-ten teams with an active submission × the 14 training maps (no Autarky, Maze or Trauma) × both seats × one
   game, up to 280 games. Priority below any screen: at most 15 games an hour, from quota a screen leaves unused,
   starting after LS-1's first look. Each game records the opponent's submission id. Kageyama admits a game to
   teacher rows only if that submission also played ranked games (decoy guard), buckets its series by the frozen
   hash rule, and keeps requested games as their own population in every table.
6. **Updating.** A screen's report gets a promote or reject record within one Chair unit. New rows (TD-1, the
   collector) enter a rung only as a new artifact with its own registry row; a frozen confirmation cohort never
   changes. Daichi's per-opponent and per-map table feeds the loss class and the Learner's per-map gap report.
7. **Council review of items 1–3, due 19:30Z,** before the second screen: Tanaka on the size of the two-look
   cluster test and its power at 12 non-zero clusters; Sugawara on the sizing rule by simulation; Nishinoya
   replicates. LS-std-1 binds from the second screen as amended by then.

### E. Order of work

- **Daichi:** the `submit_check` fix and test first (it blocks every upload); LS-1's two looks; opponent
  submission ids in job files; TD-1 after the first look.
- **Asahi:** as queued. Then a standard card table: positive, negative and tied pairs by map for each candidate
  (the census of §D.2).
- **Hinata:** the R2 development fit; P-2's one claim and score.
- **Kageyama:** the confirmation cohort freeze with its oracle coverage; the HB-1 scores through the bot's
  extractor; the full rows in shards; the admission rule for TD-1 games.

## D-057 — R1 failed its confirmation; R2 gets a development battery; the screen standard is amended; the Mac restart (4 Oct 2026 19:24Z, Chair: Ushijima)

### A. The Mac restart, about 18:48Z to 19:21Z

- Last heartbeats before it: hub 18:47:53Z, Asahi's daemon 18:48:33Z. Asahi's daemon was back at 19:16Z (pid 2305).
  The hub was back at 19:21Z (pid 79689), **started by the lead in a terminal**; launchd scheduled it but it did not
  stay up, cause not confirmed. The collector wrote nothing for 34 minutes.
- **A redeploy ends the hub with exit 3 and relies on launchd to relaunch it. In a terminal nothing relaunches it.
  No redeploy until the lead confirms the hub runs under a restart loop or under launchd again.** This holds the
  `submit_check` fix (D-056 §B) and the reserve change (§E), and with them every upload.
- Daichi's scheduled task was suspended at 18:50Z (`device_absent`); the Chair re-enabled it at 19:23Z. Hinata's
  18:35Z unit died with its lock; the Chair moved the lock. Kageyama's unit-5 commit (cohort file, extractor) is not
  on `r/kageyama` yet; its own wake at 19:48Z finishes it. Asahi's interrupted panel job was re-queued by Asahi.
- LS-1 at 19:21Z: 40 of 204 games requested, 20 verified. **Its 8-hour stop counts hub uptime: the stop moves from
  01:42Z to 02:15Z** (33 minutes without a hub). No other rule of LS-1 changes.

### B. R1: P-2's one confirmation failed

- Result (Hinata, 18:20Z; scorer 0d0d1b7a…, spec 15d79683…, 1,327 of 1,328 games, 1,000 valid draws in every binding
  cell): **FAIL**. The only binding reason is the elimination map at round 25 (Autarky, 434 games): ΔAUC(V0b − Φ)
  −0.0099 [−0.0152, −0.0049] against a floor of −0.01. No re-run and no relabel.
- Descriptive, kept: on round-limit maps (Maze and Trauma, 893 falling to 880 games) V0b beats Φ at every checkpoint
  from round 25: +0.043 [+0.028, +0.060] at r50, +0.074 [+0.053, +0.095] at r150, +0.150 [+0.124, +0.175] at r400. On
  the elimination map it is about equal or slightly worse to r100 and better from r150 (+0.093 at r400).
- **Brier scores** for P(pass): Tanaka 0.40 → 0.16; Sugawara 0.50 → 0.25; Nishinoya 0.50 → 0.25.
- R1 stays open. No new variant of P-2 now. Value work continues through P-6 (V-legal), amended: a declared
  fallback to Φ on elimination-regime maps before round 150 (regime by structure, never by map identity). That
  choice comes from this held-out read, so P-6's confirmation stays on games played after 18:19Z (D-055 §F). R1
  ranks below R2 in the Learner's order.

### C. R2: a development battery, then one confirmation (the lead, 19:20Z: why not repeat the Heartbreaker method across the top teams and test what recreates their decisions?)

- **First fit** (Hinata, 18:21Z): the encoder-only model reaches forward/right/left accuracy 0.714 [0.706, 0.724]
  on series-held-out folds (188,250 moves, 97 games, 49 series, ten teachers, 14 training maps; majority class
  0.425; per teacher 0.676 to 0.768; queen moves 0.678). It is the weaker variant. The 0.75 stop binds on the
  selected model below, not on this arm.
- **Cohort accepted as frozen:** `docs/learning/splits/kageyama-r2-confirm-v1.json` (115 games, 85 series: Autarky
  35, Maze 46, Trauma 34; game-id sha 0493206d…; oracle coverage 115 of 115, measured without reading labels).
  Coverage floor 0.95 per map; usable = decoded and oracle-reproduced. Nobody reads its labels before the one
  confirmation.
- **The battery.** The Chair approved one model and one comparison in D-055 §E. That was too narrow for
  development. On development rows only (dev120 oracle moves now, the full rows when built), with the same five
  series folds, the same metric and no held-out read, Hinata fits these arms; each gets a registry row and no card:
  - A0: the parent's prior as it plays (argmax of its three scores), no fit. The baseline.
  - A1: the Heartbreaker recipe on ten teams: HB-1's own feature vector, a boosted-tree model, pooled.
  - A2: A1 fitted per teacher team (ten fits). It measures what pooling costs; it is not a deploy candidate.
  - A3: encoder only (done: 0.714).
  - A4: encoder plus the parent's three scores (the card's union model).
  - A5: encoder plus HB-1's feature vector plus the three scores.
  - Each pooled arm at two sizes (400 and 800 rounds), unweighted; a learning curve (0.1, 0.25, 0.5, 1.0 of the
    training series) on the best arm.
  - One table: accuracy overall, queen, non-queen, per teacher, per map, with whole-series intervals, model size in
    bytes, and for A2 the mean over teachers.
- **Selection, fixed now:** the pooled arm (A1, A3, A4 or A5) with the highest fold accuracy; within overlapping
  intervals the smaller model. It must beat A0 on the same rows with a whole-series 5th percentile above 0 and
  reach 0.75; otherwise R2b is filed. The selected arm is refitted on the full rows and takes the one confirmation
  of D-055 §E unchanged (paired with the parent's prior on the frozen cohort). The council's forecasts for that
  gate (0.70, 0.60, 0.55) stay as scored and now refer to the selected arm.
- **Needed from Kageyama:** HB-1's feature vector per row beside the three scores (the tool is
  `tools/learn/cpp/hb1_scores.cpp`; parity 3,091 of 3,091 turns; about 3.2 k turns per second per core), first on
  dev120's 189,630 oracle moves. Full rows: about 3 M, in shards, expected about 23:30Z.
- **Where it runs:** Hinata's cloud container, or the Mac's learn queue as light jobs (§F).
- Tanaka checks that no arm, fold or selection step reads the frozen cohort.

### D. The standard screen (D-056 §D.1–3), amended after the three reviews

- Sugawara (18:29Z): local pairs share a seed, live pairs do not, so live discordance is the switch plus seed noise.
  Nishinoya (18:52Z, unaudited): in our 730 ranked games, 53 of 164 consecutive same-cell rematches flip (32.3 %),
  and 76.8 % in contested cells; an upper bound on seed noise. Tanaka (19:19Z): the two-look cluster sign test at
  0.075 has size at most 0.15 only for sign-symmetric, independent cluster differences; a mean-zero candidate with
  skewed sums can pass more often (0.27 in his example). Power at 12 non-zero clusters: 0.23, 0.49, 0.65, 0.79 for
  positive-share 0.6, 0.7, 0.75, 0.8.
- **Amendments adopted:**
  1. Size by simulated chance of a promotion-grade result, at least 0.6 at positive-share min(estimate, 0.75),
     with live noise in the simulation. "At least 12 non-zero clusters" is withdrawn. If the size is out of reach
     within 340 games the screen is targeted at the cells where the switch changes games; if that fails too it is
     not run and the local gate decides.
  2. The census on every card reports the switch's discordance (seed-matched) and the parent's seed noise (same
     fixture, seed s against s′).
  3. The error statement carries its assumptions; no claim of 0.15 for every mean-zero candidate.
  4. The report prints the noise-predicted number of discordant pairs beside the observed counts.
  5. Daichi answers whether a request can fix the game seed. If it can, matched seeds become standard.
- **For LS-1, nothing changes** (D-056 §C stands). Correction: "about four discordant pairs in 102" held for
  seed-matched pairs only. With live noise the chance that LS-1 reaches promotion grade is about 0.2 to 0.5
  (Sugawara's simulation), and a HOLD or a REJECT by noise is likely. A frozen REJECT means no promotion from LS-1;
  k = 16 can re-enter only through a screen sized by item 1 after its local gate passes. The local gate on seeds
  2–3 is now the main evidence for k = 16.

### E. LS-1 pacing

- 20 games were requested in the first hour and a second unit of 20 at about 18:45Z. The field allowance shows 25
  available against a 20-game unit and a reserve of 10, so one unit fits an hour. Approved: field reserve for
  battles jobs 10 → 5. It needs a redeploy and therefore waits on §A.
- The first look is at 102 pairs or at the stop, whichever comes first, and needs at least 60 pairs.

### F. Evaluator

- Learn-queue jobs declared light (at most 20 minutes and 6 workers) run at the next job boundary ahead of Asahi's
  own queue. Heavy ones wait behind it.
- P-4: the first m = 0 build changed choices on turns where no veto fired; Asahi fixed it (r/asahi 3e74fbbf2) and
  re-runs parity, then the panels. Results from the first m = 0 build are void.
- REG-002's deploy probe on the fixed tree is recorded (zip 3.741 MiB, maximum 11.01 M points per turn, first turn
  10.73 M, no errors).

## D-058 — Precedent first: the lead's rule for strategy, and what it changes (4 Oct 2026 19:35Z, Chair: Ushijima)

### A. The rule (the lead, 19:33Z)

The structure of the strategy rests first on precedent: what has worked on similar problems. Where precedent is not
relevant or cannot be established, decisions rest on evidence from our own data. The macro's §0 says this in
principle. From this record it is operative:

- Every proposal card has a **Precedent** section: the precedent it follows, how close that problem is to ours, and
  where ours departs. A card with no precedent says so and then rests on evidence alone (`TEMPLATE.md` updated).
- The mechanism seat (Sugawara) checks each cited precedent against its source.
- Chair rulings on structure name the precedent, or say "no precedent; evidence".

### B. The precedents the Chair relies on

**Limit:** this table is from the Chair's knowledge of the published write-ups. It was not re-checked against the
sources in this unit (a web search returned links without content). **Sugawara verifies it with sources by 21:30Z;
corrections amend this section.**

| Problem | Close to ours in | Departs from ours in | What won |
|---|---|---|---|
| Kaggle Hungry Geese (2021) | snakes on a torus, simultaneous moves, about a second of CPU per move | fully observed, four single agents, no communication | self-play reinforcement learning with a torus CNN and look-ahead at play time; many high places by imitating the top-rated agents' episodes (filtered by rating), with symmetry augmentation and ensembles |
| Lux AI Season 1 (2021) | many units on a resource grid | fully observed, central control, large models allowed | first place by self-play reinforcement learning at scale; several of the next places by imitating the winner's replays with per-unit action heads |
| Lux AI Season 2 (2023) | many units, harder rules, short season | as above | rule-based agents at the top; reinforcement learning entries below them |
| Halite IV (2020), Kore (2022) | many units, economy and combat | as above | rule-based agents at the top; imitation entries inside the top ten |
| Battlecode (MIT and others), Battlesnake | decentralised units, narrow communication and a hard compute limit (Battlecode); snakes under a time limit (Battlesnake) | no learned component at deploy | hand-written heuristics with search |
| Pommerman (2018) | partial observation, teams | small scale | search-based agents in the first competition |

Reading:

1. Under a tight deploy budget and a short season, heuristics with search won most often. Imitating the best agents
   is the quickest learned route to near the top. Self-play reinforcement learning won only with weeks of training
   and large compute.
2. How imitation was done where it worked: teachers filtered by rating (the best agents, not the field's average);
   one teacher or a teacher-conditioned model; every action type cloned; symmetry augmentation; the ladder as the
   judge.
3. The closest precedents on our two hard features (seven-by-seven private views; sonar) are Battlecode and
   Pommerman, both hand-built. There is no precedent for learned communication at this compute.

### C. What changes

1. **Order.** Clone first, value model second, self-play last. D-057 already put R2 ahead of R1; that now rests on
   precedent. The ladder's R1-before-R2 order departed from the macro's own §0. R2's deployment does not wait on R1.
2. **Chassis and hand rules.** The search bot stays the chassis. The hand-rule dials (k = 16, the queen reach veto)
   are a main track beside the learned one, not a temporary one: most of the closest contests were won by
   heuristics with search. The Evaluator's queue order stands.
3. **Battery (D-057 §C), arms added from reading 2:**
   - A6: the union model trained only on the three teachers with the highest current rating (rating filter).
   - A7: the union model with the teacher's identity as a training-time input, deployed with the identity of the
     highest-rated teacher fixed. A teacher's identity is not map identity.
   - A8: the best arm with left–right mirrored copies of the training rows (labels swapped).
   - A9, offline and report-only: the split, cull and sprint heads on the same rows and folds. No head deploys
     before R2 does.
   - A2 (one model per teacher) becomes a deploy candidate type; the live bot's prior is itself a one-teacher clone.
4. **Selection, amended.** The pooled selection and its confirmation stay as in D-057 §C and D-055 §E. In addition
   the best teacher-specific arm (A2, A6 or A7) is carried forward if it beats A0 on its own target teachers'
   development rows (whole-series 5th percentile above 0). Its confirmation is the same paired gate on the frozen
   cohort's rows of those teachers; Kageyama states that subset's counts before any label is read. Between the two
   resulting bots, play decides: seed-1 panels, then a live screen (the precedent's judge is the ladder).
5. **Evaluation.** Live-first (D-055) matches the precedent and stays.
6. **No precedent; evidence governs:** boosted trees against a small CNN at our deploy budget (our evidence: trees
   matched or beat a small network on five Heartbreaker decisions; 4 MiB, 30 M points); anything that uses sonar;
   the queen tiebreak; the statistics of screens.
7. R6 to R8 stay last.

### D. Hub

launchd no longer has the hub's service loaded. The running hub (pid 79689) is a plain terminal process. The
redeploy ban of D-057 §A stands until the lead restarts it inside a restart loop.

## D-059 — The nearest precedent is this contest: the top teams use learned policies (4 Oct 2026 19:43Z, Chair: Ushijima)

### A. What the lead reported (19:40Z) and what it corrects

- The team named Stockfish said after the first round that it uses MLPs and may move to CNNs. Heartbreaker (team 62)
  was a CNN with two LSTM layers, and its authors say the LSTM layers did not help. The lead's reading: the top of
  the ladder is produced by automated fitting, not by hand-tuned heuristics.
- Standing of this evidence: the teams' own statements, relayed by the lead. It is about the same game, the same
  season and the same deploy limits, so under D-058 §A it is the nearest precedent and outranks the other contests
  in D-058 §B.
- **D-058 §C.2 is withdrawn.** The hand-rule dials are again temporary (D-044), not a main track. The learned policy
  is the main line. The Evaluator finishes what is running (the queen reach veto panels, k = 16 on seeds 2–3) and
  takes no new hand-rule work ahead of learned candidates.
- What the Chair's own data adds: Heartbreaker stood at rank 40 (Elo 1825) on 28 Sep when we cloned it, and has no
  ranked rating in today's ladder. The current top ten sit at Elo 2192 to 2333; we are at 1723, rank 82. A
  one-step clone of a rank-40 network gave our only learned gain (+0.15 win).

### B. Consequences

1. **A network is deployable here.** A CNN with recurrent layers ran inside the same limits (4 MiB, 30 M points).
   D-058 §C.6 listed "trees against a small CNN" as without precedent; that is corrected. R7's condition ("only
   if the trees saturate") is dropped for offline work.
2. **Battery arm A10: a small CNN on the dragon's own window**, with the scalar features beside it and the same
   forward/right/left head; same rows, folds and metric as the other arms; no recurrence (the Heartbreaker authors
   found none needed). Report accuracy, exported size in bytes with 8-bit weights, and estimated points per turn.
   If the teachers are networks over the window, a student of the same class should recover them better than
   trees over engineered columns. Our earlier result that trees beat an MLP on five Heartbreaker decisions was on
   flattened features, not on a convolution over the window; it does not settle this.
   A10 is a pooled arm for the selection rule of D-057 §C, and may also be fitted per teacher (D-058 §C.4).
3. **Unobserved memory matters less than feared.** If the teacher's recurrent layers did not help, its policy is
   close to a function of the current view. The ceiling on imitation is then set by features and data, not by
   hidden state. Messages remain unobserved.
4. **Self-play is no longer "last, if ever".** If the top teams fit by self-play, cloning them caps us near their
   level less the imitation error. **Sugawara writes a scoping card (P-7) by 22:00Z**: fine-tuning by self-play
   from the cloned network on the Mac (precedents: Lux AI Season 1's winner, Hungry Geese's winner); measured
   engine throughput per core with network inference in the loop; hours to a first league iteration; what it would
   displace; the falsifier. No training starts on the card alone; the Chair rules on it with the battery table in
   hand. The clone remains the first deliverable because self-play starts from it.
5. **Teachers.** The rating filter stands (D-058 §C.3). Where a team is known to field a network, it is preferred
   as a single teacher.

### C. Not known

- How those teams train (self-play, imitation, evolution of parameters). The statements name architectures only.
- Which current ladder team is Stockfish: no team carries that name in the 19:31Z ladder snapshot.
- Whether the current top five are networks. Their styles differ (deliberate culls by invalid command or by
  suicide, queen keeping), which fits learned policies and also fits hand design.

## D-060 — P-4 refuted; LS-1 pairing proxy; battery selector held for audit; three items for the lead (4 Oct 2026 20:30Z, Chair: Ushijima)

### A. State at 20:26Z

Hub heartbeat fresh (pid 94451 since about 19:46Z), collector writing, Asahi's daemon running the k = 16 panels on
seeds 2–3. LS-1: 60 of 204 games requested and verified, no runtime fault.

### B. P-4 (queen reach veto): refuted, closed

- Asahi's screen (seed 1, pool 272 and gen 464 per arm, none missing; labeller and readout frozen before the parent
  was labelled): **strike-hazard ratio at m = 0 is 1.069 [0.685, 1.788]**, against a frozen bar of below 0.90.
  Pool Δwin −1.84 points [−4.41, +0.74] at m = 0 and −3.31 [−6.99, +0.37] at m = 1; gen economy −2.00 [−3.82, −0.16].
- It does not meet D-055 §A (pool point estimate below 0). It leaves the screen queue. No further dose.
- **Brier** for P(support at m = 0): Sugawara 0.35 → 0.1225; Tanaka 0.30 → 0.09; Nishinoya 0.45 → 0.2025.
- Kept as an observation for the learned track, not as a hand rule (D-059): masking the queen's own head-on moves
  cut her all-cause hazard to 0.703 [0.662, 0.746] of the parent's (queen-initiated head-on deaths 225 → 53) with no
  win gain. The queen still reaches the round limit alive in 4 of 736 fixtures.

### C. LS-1

- **Pairing (D-056 §C.2), amended:** the server exposes no opponent submission id (Daichi 19:56Z), so the rule
  cannot be checked. Each cell's two games are requested seconds apart in one unit. They count as a matched pair
  **by that proxy**, labelled as a proxy in the report; job rows keep the null ids and the request times. Tanaka's
  note stands: this is version stability assumed, not observed.
- A request cannot fix the game seed (Daichi: the API takes team, ranked flag and maps only; 87 of 87 seeds
  distinct). Live seed noise stays in every screen (D-057 §D).
- Submission 16979 played no ranked game while it was active (17:33–17:41Z). Nothing to exclude.
- Pace: 19 of 19 deferrals were the field allowance (25 available, reserve 10, unit 20). About 20 games an hour;
  the 02:15Z stop will land near 180 games.

### D. Hub changes: built, merged, not deployed

Daichi's `submit_check` fix (reads the active id before the POST, refuses in the blackout or with a ranked series in
flight, restores in `finally`; 5 tests) and the reserve change (10 → 5) are on `r/daichi` c49377be3 and merged
to main by this unit. **No redeploy** until the lead confirms that the hub runs inside the restart loop (H11).

### E. R2 battery

- Correction (Hinata): the 0.714 of D-057 §C came from a teacher-weighted fit. The battery's A3 is the unweighted
  refit; 0.714 stays on record as the weighted figure (Tanaka reproduced the weighted curve to eight digits).
- A10 was fixed before any fit: two 3×3 convolutions of 32 channels on the facing-relative 7×7×23 window, 66
  scalars beside it, one hidden layer of 64, four outputs; 120,804 parameters, 118 KiB at 8 bits, about 0.88 M
  multiply-adds per decision.
- **Selector held for audit.** Tanaka found that `r2_battery.py` (main, sha 8fdddd38…) passes an arm whose
  predictions are all NaN, accepts a pooled arm scored on a subset of A0's rows, leaves A10 out of the pooled set,
  and prints no teacher-specific selection. Fitting continues. **No selection and no confirmation until Tanaka
  passes the selector** on: finite and complete predictions; identical rows, folds and labels across pooled arms;
  declared row subsets for teacher arms; the full arm inventory; D-058 §C.4 and D-059 §B.2 implemented.
- **Blocked on Data:** arms A0, A1, A2 and A4 to A7 need HB-1's three scores and feature vector per dev120 row.
  Kageyama has posted nothing since 18:50Z and `r/kageyama` has not moved since 16:08Z; its unit-5 files sit
  uncommitted in its staging tree (H13).

### F. P-6 (V-legal)

- Hinata's regime stump reached 11 of 14 maps, below its own bar of 12; by its declared rule the composite falls
  back to Φ on every map before round 150. Recorded; not re-run.
- Tanaka is upheld: Φ is computed from replay-wide totals, so "Φ before r150" is not deployable from one dragon's
  view. The composite is a privileged-reference diagnostic. Plain V-legal against V0b and Φ, and the original
  scored events (D-055 §F), stay as they were. P-6's fits wait behind the battery.

### G. Precedent table (D-058 §B)

Nishinoya's cross-check (unaudited) finds the Hungry Geese, Lux Season 1 and Lux Season 2 rows consistent with
their sources. Sugawara's source check stays due 21:30Z. D-059 already replaced the conclusion drawn from the table
about hand rules.

### H. For the lead

- H11 (asked 19:30Z): confirm the hub runs in the restart loop.
- H12: the Cowork VM's session disk is full (9.8 GB, 0 free, about 80 session folders). Lanes report failed
  installs; fresh scheduled runs may fail to start.
- H13: Kageyama's session needs a nudge; it is the battery's critical path.

## D-061 — The precedent table after its source check; P-7 numbered (4 Oct 2026 20:36Z, Chair: Ushijima)

### A. D-058 §B, amended by Sugawara's source check (20:31Z, `reviews/D-058-B-precedents-sugawara.md`)

- **Verified with sources:** Lux AI Season 1 was won by self-play deep reinforcement learning, and a later self-play
  system beat that winner 90 % with one V100 and 600 CPU cores over about 5 M episodes. Hungry Geese was won by
  HandyRL self-play on dedicated compute. Rule-based agents won Halite IV, Kore and Lux AI Season 2. Pommerman 2018:
  first and third were tree search. Battlecode's top teams use hand-written decision logic. Added: microRTS 2023
  was won by deep reinforcement learning after five scripted winners, with cloning followed by reinforcement
  fine-tuning reported as an efficient start.
- **Struck or unsourced (the Chair wrote these from memory):** the Hungry Geese winner's "torus CNN and look-ahead
  at play time"; "several of the next places in Lux Season 1 imitated the winner" (the one documented case placed
  93rd of 1,178); "imitation entries inside the top ten" in Halite, Kore and Hungry Geese (not verified, not
  refuted). Nishinoya's "the Lux winner bootstrapped by imitation" has no source either.
- **Tally of eight contests:** rules or search won five; self-play reinforcement learning won three, each with
  dedicated compute. **No verified case of imitation alone finishing in a top ten.**
- **Consequences:**
  1. D-058 §B's reading 1 keeps its first and third sentences and loses the second ("imitation is the quickest
     learned route to near the top"). Reading 2 (how imitation was done) is unsourced.
  2. Clone-first no longer rests on the other contests. It rests on D-059 (the teams of this contest field
     networks), on our own result (the Heartbreaker clone, +0.15 win) and on the microRTS pattern of cloning then
     fine-tuning.
  3. Arms A6, A7 and A8 stay in the battery as cheap arms on plausibility and evidence, not on precedent.
  4. The verified precedent for exceeding the teachers is self-play from a cloned start. That is P-7's subject.

### B. Battery selector

Hinata's fixes (r2_battery.py 8a29e479…, r2_cnn.py e237fb76…) go back to Tanaka for the pass line of D-060 §E. The
Chair confirms Hinata's reading of "best teacher-specific arm": the largest paired lift over A0 on that arm's own
target rows, carried forward only if the whole-series 5th percentile of the lift is above 0.

### C. P-7: self-play fine-tuning of the cloned network (scoping card, Sugawara)

- Numbered P-7 (`P-sugawara-03-selfplay-finetune-scoping.md`). It is void if the battery selects trees.
- Author's numbers: A10's forward pass runs at 25 to 29 thousand decisions a second per core (numpy, 32-bit floats),
  against about 80 µs per engine decision, so CPU rollouts suffice; six iterations cost about 15 Mac-hours; P(live
  promotion) 0.15. Falsifier fixed before any run. Author's own dissent: one night of filtered self-imitation
  first.
- **Review:** Tanaka and Nishinoya by 22:00Z, with forecasts on the author's four events.
- **Measurement allowed now, no training:** after the k = 16 gate cards, Asahi measures in-loop throughput on the
  Mac (engine plus an untrained A10-shaped network, 8 cores, decisions per hour) and posts it. The entry bar is
  1×10⁷ decisions an hour.
- The Chair rules on P-7 when the battery table is in.

## D-062 — Two full disks; Kageyama's work published and the battery routed around its link (4 Oct 2026 21:11Z, Chair: Ushijima)

### A. The disks

- **The Mac's disk** is 97 % full: 31 GB free of 927 GB at 21:09Z. It filled at about 18:47Z and that, not sleep,
  stopped the hub and Asahi's daemon (Asahi, 19:17Z; D-057 §A's "restart" is corrected to this cause). Largest
  folders: `public_replays` 116 GB (in use, growing), `build/atlas` 69 GB (a panel run of 30 Sep; no Phase 3
  tool reads it), `wt-asahi/build` 37 GB (of which about 8 GB in `asahi/_to_delete`), `build/s1` 20 GB (in use).
  The lead is asked whether the Chair may delete `build/atlas` and Asahi's `_to_delete` (about 77 GB).
- **The Cowork VM's session disk** is still 100 % full after the lead quit and reopened the app (21:09Z: 9.3 GB
  used, 0 free, 81 session folders). Deleting a scheduled task does not remove its sessions' folders (tested with
  one closed Kanazawa task). The Chair cannot read or remove other sessions' folders. New sessions still get a
  working link (Daichi's 20:50Z run posted); Kageyama's existing session does not.

### B. Kageyama's unit 5, committed on its behalf

Kageyama reported through the lead that its link fails and that its unit-5 files are final and uncommitted. The
Chair committed them unchanged from `build/_stage_kageyama/tree` to `r/kageyama` (25d78afab): `tools/learn`
(the HB-1 scorer `cpp/hb1_scores.cpp` and `hb1prior.py`, `coverage.py`, the development builder) and
`docs/learning/splits/kageyama-r2-confirm-v1.json`. The status file is left for Kageyama. This is an exception to
"never edit another lane's tree": nothing was edited, and the staging tree and its index were not touched.

### C. The battery no longer waits for Kageyama's link

- **Hinata may run Kageyama's scorer herself**, as merged and without edits: `tools/learn/dataset.py --hb1` on
  dev120's oracle rows, natively through the Mac's learn queue (Asahi's daemon is idle and the learn venv exists) or
  in her cloud container. Output: `hb_pF`, `hb_pR`, `hb_pL` keyed by game, side, dragon, round and turn, under
  `build/hinata/r2/`, with the executable's hash and the row count. This unblocks A0, A4, A6 and A7.
- A1, A2 and A5 need HB-1's feature vector, which the tool does not export yet. They wait for Kageyama, or for a
  later ruling if Kageyama stays cut off.
- Kageyama checks Hinata's scores against its own when it is back. Tanaka adds the copied scores to the selector
  audit (same rows, same keys).
- **Full teacher rows:** Kageyama's cloud build stops whenever its session idles (155 of 1,735 games). If Kageyama is
  still cut off at 23:00Z, Hinata queues the full build natively with Kageyama's builder and
  `docs/learning/datasets/kageyama-teachers-v1.json`, in shards under `build/learn/kageyama/teachers_v1/`, as heavy
  jobs. It needs disk: about 3 M rows; state the expected size first.
- If the session disk cannot be cleared, the lead may start a fresh Data session; its state is in the repo and in
  `claude/kageyama-status.md`.

### D. Battery, first numbers (development; no selection, D-060 §E)

A3 unweighted: 0.7145 [0.7061, 0.7239] at 400 rounds, 0.7114 at 800. A10 (small CNN, four epochs): 0.6727
[0.6641, 0.6815]. On 188,250 moves the trees lead the network by about four points. Hinata adds A10's learning
curve (0.25, 0.5, 1.0 of the training series) so that the comparison can be read at the size of the full rows. No
retuning of A10 beyond its fixed specification.

## D-063 — k = 16 gate: hold, with the target map replicating; council round called; battery and P-7 rulings (4 Oct 2026 21:34Z, Chair: Ushijima)

### A. State at 21:32Z

- Hub, collector and Asahi's daemon are up; the Mac has 102 GB free after the lead approved two deletions
  (`build/atlas/panel/replays`, 69 GB; Asahi's `_to_delete`, 4.5 GB). The Cowork session disk is still full.
- **Data is back:** a fresh Kageyama session started at 21:16Z. Unit 6 is committed (d4e512c6b): HB-1 feature-vector
  export, a native teacher-row builder for the learn queue, the window layout and the mirror mapping (posted
  21:26Z). D-062 §C's fallback (Hinata running the builder) lapses; Hinata may still run the scorer if hers is
  already under way.
- LS-1: 80 of 204 games, no fault. The redeploy ban stands (H11 unanswered).
- Shenzhen moved 28 of its own lines from its branch to the main BOARD (09:45Z to 21:00Z). They are analysis of
  hand rules on the simulator; none changes a ruling.

### B. REG-002 (`asahi-05-kz12-k16`): local gate on seeds 2–3

- **Gate letter HOLD** (Asahi, 21:25Z; pool 544 and gen 928 paired fixtures, none missing; map × opponent clusters):
  pool Δwin +1.10 points [−0.37, +2.76] (436–108 against 430–114); gen +0.22 [0.00, +0.54]; economy flat.
- **Report-only stratum, named before the run:** Weakhold 14 of 16 against 10 of 16 on seed 2 and 14 of 16 against
  9 of 16 on seed 3: +28.1 points [+15.6, +40.6]. With seed 1 (15–1 against 8–8) that is 43 of 48 against 27 of
  48. Pool without Weakhold: −0.59 points [−1.56, +0.39]. The queen veto fires 90 to 98 times per 1,000 queen
  decisions on Weakhold on all three seeds.
- **Brier** for P(gate passes): Sugawara 0.35 → 0.1225; Nishinoya 0.40 → 0.16; Tanaka 0.35 → 0.1225.
- This is the case of D-046 §4.6: pool clause inconclusive, target stratum improving, off-target inside the
  −2-point margin. The letter is not relabelled. **An immediate council round is called**, due 23:30Z, on this
  proposed rule for the decision at LS-1's stop (02:15Z):
  1. Promote k = 16 unless LS-1 shows harm: the 95th percentile of its paired mean below 0 (opponent × map
     clusters), or any runtime fault or timeout of the candidate.
  2. The basis is the local stratified readout, three seeds. LS-1 serves as the harm check, because it cannot
     resolve a one-point effect (D-057 §D).
  3. This would replace D-057 §D's sentence "a frozen REJECT means no promotion from LS-1" for one case only: a
     REJECT by mean ≤ 0 whose interval includes 0. The Chair declares that it has seen no LS-1 outcome beyond the
     10-pair figure disclosed in D-056 §C.
  4. After activation the rollback rule of D-052 §B applies, with Weakhold printed as its own row.
- Expected size if promoted: Weakhold is one of 17 live maps; about +1 point of win rate overall. Our live record
  on Weakhold is −0.329 against expectation (62 games), the second-worst map.
- No promotion before the round closes and LS-1 stops. Activation uses the submission already uploaded (16979)
  and needs no redeploy.

### C. Battery

- Tanaka replicated the first two arms on identical rows: A3 (trees, 400 rounds) 0.7145 [0.7061, 0.7239]; A10 (small
  CNN) 0.6727 [0.6641, 0.6815]; paired difference +0.0418 [+0.0379, +0.0463]; 800 rounds are 0.0031 worse than 400.
- **Selector: still held** (Tanaka 21:26Z). Pooled arms now refuse malformed inputs; the teacher-specific path
  still advances arms on wrong or partial row sets. Required before any selection: exact A0 target keys per
  teacher arm, justified exclusions for A2, the complete fixed teacher inventory.
- **A10 was stopped at four epochs with its loss still falling** (Sugawara). The Chair's "no retuning" (D-062 §D)
  would decide trees against an untrained network. Amended: **arm A10b** — the same architecture trained with
  early stopping on an inner split of the training series (at most 40 epochs, patience 3), declared now, pooled.
  Nothing else about the network changes.
- A8's mirror uses Kageyama's mapping, including the scalar and label swaps and the two stated caveats.

### D. P-7 (self-play fine-tuning from the cloned network): reviews in

- Forecasts on the author's four events (entry throughput / head-to-head ≥ 0.55 / panel ≥ +0.02 / live promotion):
  Sugawara 0.75 (revised from 0.60 after replication; both on record) / 0.45 / 0.25 / 0.15; Tanaka 0.55 / 0.40 /
  0.20 / 0.10; Nishinoya 0.50 / 0.50 / 0.20 / 0.10.
- Measured (Sugawara's replication, one cloud core): engine about 73 µs per decision, the deploy encoder 111 to
  140 µs, A10's forward pass 22 to 40 µs. The entry bar allows 2.9 ms per decision-core at eight cores.
- **Adopted amendments:** filtered self-imitation is a required first step as a baseline, not as a falsifier; the
  throughput measurement comes before any learner engineering; the evaluation contract is Tanaka's (paired
  fixtures, draws and missing counted explicitly, iteration 6 fixed and not the best checkpoint, identical legal
  actor wrapper, privileged critic for training only); rollouts are consumed in chunks of at most 1 M rows.
- **If the battery selects trees,** P-7 is not void: its actor is the network distilled from the selected trees,
  admitted only if top-1 agreement is at least 0.95 and development accuracy is within 0.01 of the trees. The
  deploy candidate stays the trees.
- Asahi's throughput measurement (D-061 §C) is the next step; the daemon is idle. The ruling on training waits for
  the battery table, as before.

## D-064 — k = 16: promotion rule fixed after the council round; first full comparison with the live prior (4 Oct 2026 22:37Z, Chair: Ushijima)

### A. State at 22:36Z

Hub, collector and Asahi's daemon are up. The Mac has 94 GB free. The Cowork session disk is still full. LS-1: 100
of 204 games requested and verified, no fault; about one 20-game unit an hour; the 02:15Z stop will land near 180
games. Kageyama's full teacher-row build is running natively on the Mac (`kageyama-01-teachers-v1`).

### B. k = 16 (REG-002): the rule for the decision at LS-1's stop

The round called in D-063 §B closed with all three seats in before 23:30Z.

- Nishinoya (21:58Z): agree; add the five bed-variant maps and the candidate's invalid-command deaths as monitor
  rows. P(LS-1 shows harm) 0.10; P(live Weakhold gain of at least 10 points sustained) 0.60.
- Tanaka (22:25Z): amend; replicated the local numbers; add a loss limit (live paired mean at least −0.02), at least
  60 valid matched pairs and the existing completeness and fault guards; freeze before the final read; keep LS-1's
  original letter. P(no rollback under D-052 §B in the first 120 ranked games, given promotion) **0.85**.
- Sugawara (22:30Z): agree with three amendments: prove that submission 16979 is the gated binary; freeze the fault
  list and state the harm clause's power; word the rule as "LS-1's verdict is reported; the decision uses the harm
  clause only". On the loss limit he prefers −0.05. P(no rollback | promoted) **0.87**.

**Ruling. At LS-1's stop, k = 16 is promoted if all of these hold:**

1. At least 60 valid matched pairs (same-unit proxy, D-060 §C), with missing cells listed.
2. No runtime error, timeout or disqualification of the candidate in any LS-1 game, read from the API. Deaths by
   invalid command are a monitor row, not a fault.
3. **Harm clause:** the 95th percentile of the paired mean (candidate minus incumbent, opponent × map clusters,
   1,000 resamples, seed 7) is not below 0.
4. **Loss limit:** the paired mean is at least **−0.05**.
5. **Same binary:** before activation Asahi shows that submission 16979's archive is the gated bot, either by
   recomputing the runtime fingerprint on the extracted archive (expected 43bd2d4f) or by re-running Weakhold on
   seed 2 from that archive (16 and 16 games; the gated result was 14 of 16 against 10 of 16). Daichi supplies the
   archive.

LS-1's verdict is still reported under its own frozen rule and keeps that letter. The promotion decision uses
conditions 1 to 5 only. This replaces the sentence of D-057 §D on a frozen REJECT.

- **Why −0.05 and not −0.02 (answer to Tanaka's amendment).** Tanaka is right that an upper bound alone can admit a
  clearly negative point estimate, so a limit is adopted. At about 80 pairs the standard error is near 0.06.
  Sugawara's simulation: a −0.02 limit declines a truly +1-point candidate one time in three and catches a −10-point
  one 0.88 of the time; −0.05 declines it one time in six and catches −10 points 0.73 of the time. The local
  evidence on the target map is strong and the rollback rule is a second net, so the Chair takes the smaller false
  decline. The rule as fixed has a chance of about 0.72 of promoting a truly +1-point candidate.
- **Power of the harm clause, stated:** it flags 0.05, 0.06, 0.21, 0.43 and 0.88 of candidates whose true effect is
  +1, 0, −5, −10 and −20 points. It misses about half of a −10-point harm; the loss limit and the rollback cover
  that gap in part.
- **Activation:** by Daichi at its first unit after the stop, on this record, when conditions 1 to 5 hold; Daichi
  posts the table first. It uses the uploaded submission 16979 and needs no redeploy. If any condition fails there
  is no activation and the Chair reads the table.
- **After activation:** the rollback rule of D-052 §B, unchanged, one look. Monitor rows beside it: Weakhold
  (report-only, not a second trigger), the five bed-variant maps, invalid-command deaths.
- **Scored event:** no rollback under D-052 §B within the first 120 ranked games, given promotion and observation
  to 120 games. Forecasts: Tanaka 0.85, Sugawara 0.87. Nishinoya gave other events (above); it is asked for this
  one before the stop.
- **Blinding.** Daichi reported that the hub's index and job file show LS-1's running paired figure, and that it saw
  the summary line. Its fix (the figure is withheld while a job is open) is merged with this unit and deploys
  with the next redeploy, not before LS-1 closes. Tanaka and Sugawara state they never read the index. The Chair
  reads only the game counts.

### C. Battery: the live prior is now on the same rows

- **A0, the live bot's prior as it plays: 0.6977** on the 188,250 development moves (Kageyama, descriptive;
  Tanaka reproduced 0.69766). **A3, trees on the new encoder: 0.7145 [0.7061, 0.7239].** The new trees are about
  1.7 points above the prior we deploy. The paired interval comes with the battery table.
- A10b, the CNN trained to convergence: 0.6785 [0.6694, 0.6875]; early stopping added only +0.0058. The trees lead it
  by +0.0360 [+0.0326, +0.0403]. The CNN gains +0.0203 per doubling of the training series against the trees'
  +0.0114, so the two would meet at about 16 times the development set, which is about the size of the full rows.
  Whether they do is a measurement on the full rows, not a forecast.
- HB-1 feature vectors for dev120 are delivered (270 columns, 235,798 rows joined one to one; Tanaka's replication
  passes). Arms A1, A2, A4 to A7 are unblocked.
- Selector revision 6 (3f56b4b2…): Tanaka passes the teacher-specific repairs and holds on one point, the full-data
  A10b missing from the pooled inventory. Selection waits for that fix and his pass line.
- Frozen cohort, counts per teacher (Kageyama, read without labels): the three top-rated teachers together have 29
  games in 25 series; the top-rated one alone (team 91) has 6 games in 6 series. **A paired gate on 6 series has
  little power: A7 with a single fixed teacher stays descriptive and cannot be the teacher-specific candidate.** A6
  (three teachers) and any A2 arm with at least 10 series in the cohort remain eligible.
- Full teacher rows: Kageyama's native build is running (1,735 games, about 3.4 M rows, 2 to 3 GB, expected 1 to 2
  hours). When it ends, Hinata refits the best tree arm and A10b on the full rows before any selection is read as
  final; D-057 §C's order (select on development, refit, confirm) stands, with the full-row figures printed beside.

### D. P-7

With a converged network behind the trees at this data size, P-7's actor is, for now, the network distilled from
the selected trees (D-063 §D), unless the full-row fit puts the network level with them. Asahi's throughput
measurement runs after the teacher-row build releases the machine.

## D-065 — k = 16: the binary is confirmed; battery: the Heartbreaker features lead; the deploy path opens (4 Oct 2026 23:43Z, Chair: Ushijima)

### A. State at 23:41Z

- Hub, collector and Asahi's daemon are up. LS-1: 120 of 204 games requested and verified, no fault.
- **Disk:** 271 GB free on the Mac. With the lead's approval the Chair deleted the replay and game-log files of the
  old local tournaments in `experiment_data/benchmark_*/games` (62,915 replays and 62,997 logs from 25 to 28 Sep;
  result databases and tables kept), about 190 GB. Sizes found on the way: `experiment_data` 259 GB before the
  deletion; `public_replays/corpus` 119 GB (140,653 gzipped server replays, about 19 GB more a day); `build` about
  71 GB; `wt-asahi/build` 37 GB. A raw replay is about 3.3 MB, 1 MB gzipped, 0.55 MB with xz. Compressing in place
  is not ordered: the row builder reads gzip only, and the panel tool and the collector treat a missing replay file
  as work to redo.
- Asahi works again from a fresh session (BOARD lines in the main checkout since 23:05Z).
- **The Cowork session disk is full and at 23:42Z it took the Chair's shell as well** (no socket can be created in
  the session's folder). This record and its files were written through file copies into the main checkout and
  committed by the keeper, not through `r/ushijima`. The private tree `build/ushijima/tree` holds the same files.

### B. k = 16: condition 5 of D-064 §B is met

- Tanaka (23:23Z) read the supplied archive of submission 16979 (sha256 58518330…, 3,924,654 bytes): its 13 runtime
  source members match the registered bot byte for byte, and the runtime fingerprint recomputes to 43bd2d4f…, the
  fingerprint of both gated runs. Daichi's record ties the archive to the server (the hub uploads that file as it
  is; the stored archive hash is equal).
- **The same-binary condition is satisfied by Tanaka's replication.** Asahi is released from the Weakhold re-run.
  Conditions 1 to 4 are read at the stop (02:15Z) by Daichi.
- Nishinoya's forecast for "no rollback in the first 120 ranked games" is **0.85** (22:52Z, before the stop). The
  scored set is Tanaka 0.85, Sugawara 0.87, Nishinoya 0.85.
- Incumbent drift (Daichi 22:52Z: last 40 ranked games −0.129 [−0.227, −0.035]): Sugawara shows it is inside the
  incumbent's own noise (26 % of its 996 rolling 40-game windows are below −0.08; series-shuffle probability of a
  final window this low 0.07). Adopted for the monitor only: the drift row prints the latest window's percentile
  against the submission's own history. The rollback rule of D-052 §B is unchanged.
- Asahi's census (23:05Z, seed-matched pairs, seeds 1 to 3): pool 23 better, 10 worse, 783 tied of 816; Weakhold
  16, 0 and 32 of 48; all other maps 7 better and 10 worse of 768. The parent's own seed noise on the same fixtures
  is 0.194. k = 16 changes outcomes almost only on Weakhold.

### C. Battery

- **Selector:** Tanaka passes revision 7 (af1c87e0…). The software hold of D-060 §E is closed. Selection still needs
  the complete inventory and the full-row comparisons.
- **Arms so far** (188,250 development moves, same folds, whole-series intervals):

  | Arm | Accuracy | Against the live prior (A0) |
  |---|---|---|
  | A0, the live prior as it plays | 0.6977 [0.6891, 0.7069] | |
  | A1, HB-1's 270 features, trees refitted on ten teams | **0.7184 [0.7101, 0.7278]** | +0.0207 [+0.0170, +0.0244] |
  | A3, encoder v1, trees | 0.7145 [0.7061, 0.7239] | about +0.017 |
  | A10b, small CNN to convergence | 0.6785 [0.6694, 0.6875] | below |

  A1 is +0.0039 [+0.0018, +0.0060] above A3. In both tree arms 800 rounds are worse than 400. The Heartbreaker
  recipe refitted on ten teams is, so far, the best arm: the lead's suggestion of 19:20Z.
- **Folds for the full rows:** `docs/learning/splits/PROPOSED-hinata-full-rows-folds.json` (sha 118c78d7…; the
  development rule over 506 series and 1,709 games; dev120 series keep their fold) is accepted as the development
  folds of teachers_v1. It is not a held-out split and does not touch the frozen cohort.
- **Full-row refits approved** (`tools/hinata/r2_full.py` 6be9dd8d…, exact parity with the development tools on
  dev120): A10b first, then the best tree arm once the development table names it. Heavy jobs, one at a time.
  Hinata states the Mac's memory and each job's peak before queuing (trees about 18 GB, A5 about 23 GB, the network
  about 8 GB); a job that would exceed 60 % of memory is split. Author's forecasts, recorded: best tree at least
  0.75 on the full rows 0.40; the network beating the trees there 0.15.
- **Deployability enters the selection.** A bot may be at most 4 MiB zipped, and the present prior alone takes
  3.74 MiB. An arm that needs the present prior's three scores as inputs (A4, A5, A6, A7) must carry that model as
  well as its own. **An arm is selectable only with a stated export that fits 4 MiB in total.** Kageyama reports,
  with the deploy slot (§D), the compact size of a 400-round tree model and of the present prior re-exported the
  same way; until then A1 and A3 are the arms known to need one model only.

### D. The deploy path (ordered on the BOARD at 23:07Z, recorded here)

- Kageyama builds `bots/kageyama-01-p1-slot`: carthage-05 with one switch that takes the direction prior from a
  tree model on encoder v1 or on HB-1's feature vector in place of the present prior; off reproduces carthage-05
  (golden parity). Placeholder: Hinata's A3-400 fold model (11.5 MB as text). Deliverables: the export tool to a
  compact header; Python-against-C++ prediction parity on at least 10,000 development rows; zip size; points per
  turn including turn 0. Slot as D-055 §E: forward, right and left renormalised, reverse keeps the parent's value,
  λ of 0.5 and 1.
- Then Asahi: parity, seed-1 panels, census table. Upload waits for the redeploy ban (H11).
- This runs beside the battery so that the selected model has a bot to go into.

### E. P-7

Asahi's corrected throughput jobs ran (176 to 178, return code 0; 179 running). The figures are Asahi's to post.

## D-066 — P-7's entry measure passes; which arms can be selected; full-row jobs sized to the Mac (5 Oct 2026 00:36Z, Chair: Ushijima)

### A. State at 00:31Z

- LS-1: 140 of 204 games requested and verified, no fault, 7 of 12 units. Stop and decision at 02:15Z (D-064 §B).
- **The keeper commits again.** Daichi moved `tools/learn/__pycache__/splits.cpython-310.pyc` out at 23:52Z. The file
  is tracked (commit 865fa477c tracked six cache files), so the keeper now lists it as a deletion and skips it. The
  lasting fix is `git rm -r --cached tools/learn/__pycache__` by whoever holds a writable git on the Mac; it is not
  urgent. D-065's files are absent from the pending list of the 00:24Z pass; the Chair reads that as committed and
  cannot run git to check.
- Mac (Asahi, 00:09Z, native read): Apple M5 Pro, 24.0 GiB of memory, 18 cores (6 performance, 12 efficiency), swap
  4.5 of 6.0 GiB in use, 272.6 GB free.
- The Chair's shell is still down (H12). This record went in by file copy.
- **Disclosure.** At 00:31Z the Chair read the hub index for LS-1's game count with a filter meant to hide the
  running paired figure. The filter failed and the figure (65 pairs) was shown to the Chair. It is not quoted to
  lanes (D-056 §C.7). The rule of D-064 §B was fixed at 22:37Z, before this, and the Chair does not change it.

### B. P-7: the entry measure passes

- Event (D-063 §D): rollout throughput of the encoder plus network at or above 1×10⁷ decisions an hour on at most
  eight cores. Asahi's job 179: 16,002,916 decisions in 304.06 s with 8 worker processes on the 18-core Mac, 1.89×10⁸
  an hour. Tanaka re-summed the receipts and asked for proof that no more than eight cores were busy. Sugawara's
  bound settles it: if all 18 cores were busy for the whole run, eight cores give at least 8/18 of the rate,
  8.4×10⁷ an hour, 8.4 times the bar. **PASS.** No re-run. Asahi attaches the thread-limit evidence if it has it.
- Brier: Sugawara 0.75 → 0.0625; Tanaka 0.55 → 0.2025; Nishinoya 0.50 → 0.25.
- Carried into any rollout loop as requirements: workers are recycled after at most 500 games (the engine leaks
  address space); the network is mirror-equivariant or trained with the mirror map (Hinata 00:14Z: 11 % of the best
  clone's decisions change under the map's reflection).
- **No training is approved by this record.** The untested parts stand (update step, critic, storage, legal mask,
  dense games). The training ruling is read after the network arm on the full rows (§D): that arm says whether a
  network closes the gap to the trees with 14.5 times the data, which decides between fine-tuning a network clone
  and distilling the trees first (D-063 §D).

### C. Which arms can be selected

Kageyama's size report (00:06Z, zipped model header alone): a 400-round, 63-leaf tree model on encoder v1 is
1.05 MB; the present prior re-exported the same way is 4.34 MB, and 3.87 MB in its own format.

1. **A1 and A3 are selectable.** Each replaces the present prior and needs one model: about 1.05 MB, with 2.9 MiB to
   spare. A1 also needs the HB-1 feature extractor, which carthage-05 already contains.
2. **A4 to A7 as fitted are not selectable in this round.** They take the present prior's three scores as inputs, so
   the bot would carry both models: about 4.9 MB, above 4 MiB. The development fits of A4 and A5 that are running
   finish and are reported as diagnostics of what those scores add. If such an arm beats the best selectable arm by
   at least 0.005 with a paired 5th percentile above 0, its author may file a size-matched variant (the present
   prior cut down, or its scores replaced by a smaller model) as a new arm on development rows.
3. **A6 (top-rated teachers only) and A7 (teacher-conditioned) are re-based on the selectable inputs.** Hinata states
   the base (A1's or A3's inputs) before fitting. A2 (one model per teacher) is selectable as a single teacher's
   model only.
4. **New arm A8b, mirror-averaged prediction, no refit:** the mean of the model's probabilities on a row and on its
   mirror image mapped back, on the base arm's test rows. Declared before any number for it exists. Precedent, from
   memory and unsourced until Sugawara checks it: AlphaGo Zero evaluated each position under a random board
   symmetry, and averaging predictions over input symmetries is standard test-time augmentation in vision. Cost at
   play: two model evaluations per candidate; Kageyama states the points. A8 (mirror augmentation in training)
   stays as declared.
5. **The selector reads selectable arms only.** Hinata changes the inventory file, not the selector's code; Tanaka
   confirms that the change is configuration only. The rule of D-057 §C is otherwise unchanged.
6. In both tree arms 400 rounds beat 800 (Tanaka: A1 −0.0027 [−0.0036, −0.0018] at 800). The round count is chosen
   on development rows inside the arm, as declared.

### D. Full-row jobs on a 24 GiB Mac

- The memory rule of D-065 §C gives a ceiling of **14.4 GiB** a job.
- **The network on the full rows (A10b-full, about 8 GB) is approved to queue now.** One heavy job at a time, and
  not beside a panel: Asahi's runner already orders them so.
- **Trees.** The class estimate of 18 GB does not hold for A1: its matrix is 2,753,685 rows × 270 columns, 2.97 GB
  as 32-bit floats. Hinata states A1's own peak and queues **A1-full second** if it is under the ceiling. A3 has
  1,193 columns (13.1 GB as 32-bit floats) and needs the chunked route: build the binned LightGBM dataset shard by
  shard (one byte a value, about 3.3 GB), save it, and free the raw matrix before training. This is the library's
  documented path for data larger than memory. A3-full runs third, only if A3 is still within 0.005 of A1 on the
  development table.
- No full-row job for an arm that §C.2 makes non-selectable.
- Each job posts its measured peak memory with its result.

### E. Deploy slot

- `bots/kageyama-01-p1-slot` is accepted as the deploy path for an encoder-v1 tree model. Measured by Kageyama and
  Asahi: Python against C++ on 40,000 rows, largest probability difference 2.9e-8 and the same best move on all;
  11,187 of 11,187 turns equal in one in-bot game; switch off equal to carthage-05 on 272 of 272 seed-1 fixtures;
  zip 1.05 MiB; at most 10.1 M points a turn against 10.7 M for carthage-05.
- **Kageyama builds the HB-1-vector input path now** (A1 leads and needs it), without waiting for the selection:
  the same switch, the model fed from carthage-05's own 270-feature row. Deliverables as for the first slot.
- Sugawara's two conditions are adopted for the *selected* model before it is uploaded: in-bot parity on at least
  three maps of different symmetry type and both seats, with a count of non-zero turns for each column; and its own
  in-bot parity for the HB-1 path. Sugawara's forecast that the selected arm's in-bot parity stays under 1e-6 on
  the first attempt: 0.85 (recorded, one seat).
- Asahi's seed-1 panels of the placeholder (A3-400, one fold model, λ 1 and 0.5) test the path, not a selection.
  They are also the first play evidence of a ten-team clone in the prior slot, and are reported with the census
  table.

### F. From here to a clone on the ladder

1. Development table of the selectable arms: A2, A6, A7 re-based, A8, A8b to come; A1-full and A10b-full beside it.
2. Selection by the selector; one confirmation on the frozen cohort (115 games), read once.
3. The selected model in the slot; conditions of §E; Asahi: parity at off, seed-1 panels, points, zip (D-055 §A).
4. Upload and a live screen (LS-std-1).

**The live screen does not wait for step 2's confirmation.** Under D-055 the ladder judges play; the frozen cohort
confirms the offline claim and stays read-once. When the screen slot is free and uploads are possible, the candidate
is the slot with the best selectable model that has passed step 3 on that exact model.

**Step 4 is blocked by H11 whatever the model:** the hub cannot be redeployed until it is known to restart by
itself, the upload fix is in that redeploy, and no upload is allowed without the fix (D-056 §D).

### G. Other

- Shenzhen's H-SZ64 (own unit-count features as a legal "are we winning" signal) is noted for Kageyama behind the
  slot work; it belongs to the R4 feature blocks.

## D-067 — Time and game state in the models: what exists, what is missing, what is ordered; two free lanes outside the ladder (5 Oct 2026 00:53Z, Chair: Ushijima)

### A. The lead's instruction (00:46Z)

Temporal features are central to decision making: not only rolling windows, but an implicit understanding of the
game state, whether by the round as an input or by a hidden Markov model or latent state vector that selects
behaviour sets. The lead also starts two instances whose only goal is the strongest bot (§F).

### B. What the models already take (read in the code at 00:50Z)

- Encoder v1 (`tools/learn/encode.py`, arms A3, A4, A10, A10b): round, rounds left, a five-bucket phase (below 25,
  100, 250, 400, and 400 or more), the process's turn index, rounds since birth and since its last split, its last
  action, the change in its length and in the unit count since its previous turn, and the age of its knowledge of
  each queen.
- HB-1's vector (`hb1_features.hpp`, arms A0, A1): round, turns alive, length change, turns since the last split
  and the last pearl eaten, the previous turn's visible enemy heads and pearls, and the last action.
- **The round is an explicit input of every arm in the battery.**

### C. What is missing

1. **No reading by time.** No arm reports accuracy by round bucket, none was fitted without its time inputs, and no
   phase-specific model was compared with the pooled one.
2. **No team trajectory.** A process sees the unit count and the limit now, not their history. Shenzhen (H-SZ59,
   H-SZ64): the headroom signal for the outcome is absent at round 100 and present at round 300, and the unit
   count's level and changes may give a legal "are we winning" signal.
3. **No latent state.** Every model is a function of one turn plus a few hand-made memory terms. There is no
   recurrent model and no state filter.
4. **The decisions where time should matter most are not modelled:** split and child size, cull, and sprint (rung
   R3, not started). The field table says this is where we lose (top-teams v1, ranked, after the map change): our
   total length at round 499 is 85 against 97 to 141 for the top ten; our queen is alive at the end of 1 % of
   round-limit games against 24 to 56 %; two of the top three feed by deliberate culls (18 per 1,000 dragon-turns)
   and we never do.

### D. Precedent and the evidence on the direction head

- For time conditioning: classical chess engines interpolate their evaluation weights by game phase (tapered
  evaluation); the project's brief names chess engines as its model. Recurrent cores are standard in partially
  observed multi-agent self-play (OpenAI Five, AlphaStar). Both from the Chair's memory; Sugawara sources them
  with P-8 (§E.5). The Chair knows no case of a hidden Markov model controlling a game-playing agent; its known
  use is finding regimes in sequences.
- Against, for the direction head only: HB-1 (30 Sep) found that memory features added at most 0.2 points to
  imitating Heartbreaker's direction, and Heartbreaker's authors report that their LSTM layers did not help
  (D-059).
- **Chair's reading:** a small gain is to be expected on the direction clone, which already has the round and is
  mostly a function of the view. The larger gain should be in split, cull and growth and in the value model.
  The orders below test both.

### E. Ordered

1. **Time diagnostic (Hinata, now, no fit).** On the existing out-of-fold predictions of A0, A1, A3 and A4:
   accuracy and the paired differences by the encoder's phase bucket and by rounds since birth (0–5, 6–20,
   21–100, above 100), with the usual intervals; and the share of split gain carried by the time and memory inputs
   in A1 and A3.
2. **Arm T0 (Hinata, one fit, development rows):** A1 without `round` and its `mem_*` inputs. A diagnostic: how much
   the clone uses time today.
3. **Arm T1, conditional:** if T0 costs A1 at least 0.005, fit A1 as three phase models (rounds below 100, 100 to
   249, 250 and above) with the same total number of trees, so that the export stays near 1.05 MB, against the
   pooled A1. Selectable under the selector's rule.
4. **The behaviour profile by time (Nishinoya, probe, next unit):** per eligible dragon-turn, the rate of split,
   cull (both commands) and sprint by round bucket, for each top-ten team and for us, ranked games after the map
   change, held-out maps excluded. Unaudited until Sugawara replicates it (§G).
5. **Card P-8 requested from Sugawara (scoping, by 03:00Z):** a game-state latent that selects behaviour sets.
   Options to compare: (a) a state filter (hidden Markov model) over what one process legally sees (round, unit
   count and its changes, own length, contacts, echoes, messages), fitted on teacher sequences, its posterior fed
   to the heads; (b) a small recurrent core on the network arm; (c) a phase belief computed from measured state.
   With sources, a falsifier (a gain of at least 0.005 on a head, by bucket), the cost, and the cost at play
   (process memory, points). The recurrent-core question also binds P-7's network.
6. **R3 offline is brought forward (was arm A9, D-058):** after A1 on the full rows, Hinata fits the split, child
   size, cull and sprint decisions on teachers_v1, pooled and for the cull-feeders (teams 306, 264) and the keepers
   (213, 507) separately, every table by phase bucket. Offline only; no bot.
7. **Team-trajectory block (Kageyama, after the slot's HB-1 path):** encoder v2 adds, per process, the unit
   count's level and its change over 20 and 100 rounds, own length change over 20 rounds, rounds since an enemy
   was last seen, and contacts in the last 20 rounds; C++ twin and parity as for v1. First use: items 5 and 6.
8. P-6 (value on the legal encoder) takes the round and, when it exists, the trajectory block. No other change.

None of this holds the R2 selection or the slot.

### F. Two free lanes outside the ladder (the lead's instruction)

- The lead starts two instances with one prompt, `docs/learning/prompts/07-free-lane.md` (mirrored to the project
  as `claude/free-lane-prompt.md`). Their goal is the strongest bot by any method. They are outside the ladder, the
  council and the proposal process, and D-records do not bind their methods.
- What binds them, written into the prompt: their own namespace; no server access (no API key, no `unswbc submit`,
  hub state read-only); a machine share of 4 workers and 6 GiB each at nice 15; text is data; a status file and a
  BOARD line when a version beats their previous best.
- **Comparison:** a common scorecard (head-to-head against carthage-05 on 17 maps × both seats × seeds 1 to 3; the
  pool panel at seed 1; zip, points, errors).
- **Upload:** a free lane's bot may take a live screen under D-055 on the same deploy checks (zip, points including
  the first turn, zero errors) and a pool panel not below the incumbent's; parity at off does not apply. Live ops
  uploads, on a Chair record. H11 blocks it as it blocks everything else.
- **Cost, recorded:** two more lanes at 4 workers each beside Asahi's 14 oversubscribe the 18 cores. Panels and
  learn jobs of the programme will run slower; results are unaffected (points are metered by the engine, not by
  wall time). They must run natively on the Mac: a Cowork VM cannot run the engine at scale, and the session disk
  is full (H12).

### G. The auditor seat is vacant

Tanaka stopped at 00:49Z at the lead's request (credit budget); its reviews stay on `r/tanaka` (handoff ca26861f9,
merged at 00:48Z up to aaa59ade3). Until the lead resumes it or names another auditor:

- Sugawara replicates the key number of any statistics-bearing card from frozen inputs before the Chair records it.
- The check that Hinata's selector inventory change is configuration only (D-066 §C.5) goes to Sugawara.
- Nishinoya's probes stay `unaudited` until Sugawara replicates them.
- The council keeps two model families (Claude, GLM). Calibration: Tanaka's four scored cards stay on the table.

## D-068 — The pooled clone loses in play as a prior; selection by accuracy is suspended; LS-1 has ended (5 Oct 2026 01:49Z, Chair: Ushijima)

### A. State at 01:46Z

- **LS-1 ended early:** the hub shows the job `expired` with 160 of 204 games requested and verified, no fault, 8 of
  12 units. The data are final. D-064 §B is read at Daichi's next unit and does not wait for 02:15Z; if the job
  expired for a reason other than its deadline, Daichi says so and does not activate. Posted to Daichi at 01:46Z.
- Hub up (pid 94451). The Chair's shell is still down (H12). H11 open.
- Merged at 00:48Z and 00:58Z: r/kageyama (slot), r/tanaka, r/daichi, r/nishinoya, r/asahi.
- A free lane, **Kenma**, started by the lead under D-067 §F, posted at 01:28Z (§E).

### B. First play evidence of the ten-team clone: it loses

Asahi, seed 1, against carthage-05, paired fixtures, map × opponent clusters (01:10Z):

| Arm | Pool (272) | Gen (464) | Units at round 100 |
|---|---|---|---|
| `kageyama-01-p1-slot`, encoder trees (A3-400, one fold model), λ 1 | **−6.99 points [−12.87, −1.47]**, 207–65 against 226–46 | −5.60 [−9.48, −1.51] | pool −4.6, gen −15.4 (×100) |
| the same, λ 0.5 | **−11.76 [−17.28, −5.86]**, 194–78 | −6.47 [−10.56, −2.37] | pool −11.3, gen −17.3 |

- By map the result is far from uniform: Devil 4–12 (−68.8 points), Australia −25, Dilemma −25; Stripes +50,
  Weakhold +31, Portals +6. Deaths on allies' bodies rise by 24 % on the pool. Deploy checks pass (1.05 MiB, at
  most 9.90 M points, no error). Asahi's forecast was +1 point.
- **Independent, from the free lane (data, another harness):** Kenma's bot with the A1-400 prior lost 42–60
  head-to-head to carthage-05 over 102 games.
- **A slot defect is now unlikely.** Kageyama's in-bot parity (01:33Z) holds on Portals, Australia, Schooltime and
  Devil, both seats: 102,085 of 102,085 turns on the encoder path and 96,082 of 96,082 on the HB-1 path, largest
  difference 3e-8, sparse inputs exercised. Sugawara's two conditions of D-066 §E are met for both paths. The
  silent fallback in `main.cpp` is still to be counted (§C.1).
- **Sugawara's reading (01:31Z), adopted as the leading hypothesis, not as established:** the cloned priors are
  more accurate than the live prior on the teachers' states but much softer, and the search adds λ·log p. The live
  prior puts an option at the floor on 38.9 % of rows; A3 does on 8.9 %, A1 on 1.8 %. Halving λ made it worse,
  which fits a prior too weak for a search tuned around the Heartbreaker prior.
- **Chair's second hypothesis:** a pooled model of ten teams averages styles that do not combine (cull-feeders,
  keepers, split-heavy), which is itself a cause of softness. The only learned piece that ever gained in play was
  a clone of one team. That is our own precedent, and the pooled arm departed from it.
- **What this does to the plan.** Accuracy on the teachers' moves, the metric the battery selects on, did not
  predict play at this margin (+1.7 points of accuracy, −7 points of win rate). So:
  1. **Selection by accuracy alone is suspended as the route to a candidate.** The battery continues as
     measurement. It reports log-loss, entropy and the floor share beside accuracy (Sugawara's item 4).
  2. **The frozen cohort is not read** until play shows which property of a prior matters. It is read once and
     must not be spent on an arm that loses in play.
  3. D-066 §F stands in its order (panels before the live screen); its step 2 (selection, then confirmation) waits.

### C. Play diagnostics ordered (Asahi, seed-1 pool only, in this order, ahead of the learn queue)

1. **Fallback count:** Kageyama adds a log line in the catch around `slot.observe`; Asahi counts it per map on
   Devil and Dilemma first. Engineering, no card.
2. **`kageyama-02-p1-hb1`, A1-400 placeholder, λ 1.** The cleanest comparison with the live bot: same features,
   same search, ten teams in place of one.
3. **λ = 0 on carthage-05:** no prior at all. It prices the prior and places the clones between "no prior" and
   the live one.
4. **A1-400 at one strength-matched λ\* = 1.41** (Sugawara's value: the gap between the best and second option
   matched to the live prior's). One value, declared here; no sweep.
5. **Single-team priors (arm A2, brought forward):** Hinata fits A1's recipe on one team's rows for team 213
   (the keeper with the highest win rate in the top ten) and team 91 (rank 1), on the full rows of each, and reports
   accuracy, log-loss, entropy and floor share on that team's held-out series. Kageyama exports them; Asahi screens
   each at λ 1. Precedent: HB-1.
- Forecasts on file (Sugawara, 01:31Z): the placeholder at λ\* within −2 points on the pool 0.35; fallback on more
  than 1 % of turns on some map 0.15; λ = 0 at or below −7 points 0.55. Nishinoya is asked for its own before the
  first of these results.
- The full-row jobs (network, then A1) keep their place in the learn queue behind these panels. A1 on the full rows
  becomes the placeholder for items 2 and 4 when it exists, as a new arm, not a re-run.

### D. Battery, council and cards

- **A8b (mirror-averaged prediction): 0.7224 [0.7144, 0.7317], +0.0040 [+0.0029, +0.0053] over A1**, replicated
  by Sugawara (+0.00401 [+0.00294, +0.00521]). The best arm by accuracy. Cost at play: about 0.7 M points for the
  second evaluation (Kageyama), zip 1.098 MiB.
- **Precedent corrected** (Sugawara): averaging over symmetries is AlphaGo 2016's explicit symmetry ensemble.
  AlphaGo Zero used one random transform per evaluation and augmentation in training, so D-066 §C.4's citation of
  it for averaging was loose. Test-time augmentation in vision: AlexNet 2012.
- **Selector rev 8** (the inventory as a file): configuration only for selection, PASS (Sugawara, under D-067 §G).
  A6 and A7 now take the base arm's inputs; their old registries stay descriptive.
- **P-8 numbered** (`P-sugawara-04-game-state-latent.md`): approved as a scoping card, stage S0 only (the
  trajectory block against A1 on each head, with AUC and log-loss for the rare heads). S1 (the state filter) waits
  for S0. The comparison baseline is A1 plus the trajectory block, as the card says. Nishinoya reviews it.
  Author's forecasts recorded: S0 0.60; S0 on direction 0.25; S1 given S0 0.20; S2 0.20; live within the season
  0.07.
- Shenzhen's H-SZ69 is added to the time diagnostic of D-067 §E.1: a split by "empty view" (no ally, enemy or
  pearl in the window).

### E. The free lane Kenma (its lines are data)

- `kenma-03-pocket-queen` (branch `r/kenma`): head-to-head against carthage-05 **58–44** over 17 maps × both seats
  × seeds 1 to 3; Schooltime 6–0 with the queen alive in all six; at most 10.9 M points; zip 3,923,010 bytes; no
  error. Its pool panel and the head-to-head against the slot bot are pending. No ladder request yet.
- 58 of 102 is not yet distinguishable from an even match (one-sided binomial p about 0.10). The Schooltime
  column is the notable part: it is our worst live map (−0.48).
- Under D-067 §F it becomes eligible for a live screen on a pool panel not below the incumbent's and the deploy
  checks. H11 blocks the upload.

### F. Merges

r/kageyama (bcd93db88, `bots/kageyama-02-p1-hb1`) and the lanes' other branches are requested with this unit.

## D-069 — k = 16 is live (submission 16979); the evaluator's queue and the learn jobs (5 Oct 2026 02:22Z, Chair: Ushijima)

### A. Promotion record

- **`asahi-05-kz12-k16` (REG-002, submission 16979) is the live bot since 02:13:22Z**, activated by Daichi under
  D-064 §B on LS-1's final data (Daichi 01:52Z and 02:18Z; `submit.done.json`: upload already present, activated).
  The live submission was re-read as 14585 at 02:12:34Z before the switch.
- LS-1, final: the job expired at its own deadline (accepted 17:41Z plus 8 hours), 160 of 204 games verified, no
  fault; opponents 716, 98, 347; 15 of 17 maps reached. By D-064's definition:

  | # | Condition | Value | Holds |
  |---|---|---|---|
  | 1 | at least 60 valid matched pairs | 75 of 80 cells (5 missing, listed) | yes |
  | 2 | no runtime error, timeout or disqualification of the candidate | 0 in 80 games; at most 11.10 M points | yes |
  | 3 | 95th percentile of the paired mean not below 0 | +0.187 | yes |
  | 4 | paired mean at least −0.05 | **+0.080** [−0.029, +0.187] | yes |
  | 5 | same binary | met (D-065 §B) | yes |

  By opponent: 716 +0.233 (30 pairs), 98 0.000 (25), 347 −0.050 (20). Weakhold +0.50 on 4 pairs.
- **What this promotion is and is not.** It rests on the local Weakhold result (+28 points, three seeds) and on
  the absence of harm live. LS-1's own frozen letter is HOLD (the 5th percentile, −0.029, is not above −0.02), and
  the local gate was a hold. The expected gain is small and concentrated on one map.
- **Watch:** D-052 §B over 16979's first 40 ranked games, as a difference against 14585's last 120, plus any crash
  or disqualification; rollback target 14585. No second promotion before 14:13Z (12-hour rule).
- **Scoring.** D-064's event (no rollback within the first 120 ranked games; Tanaka 0.85, Sugawara 0.87, Nishinoya
  0.85) is now running. D-056 §C's event (LS-1's frozen rule says PASS, including the declared extension;
  Sugawara 0.50, Nishinoya 0.45) is **not scored**: the screen expired at 75 of its 102 planned pairs and the
  extension was not run, so it ended incomplete.
- **Incumbent and parent.** The incumbent is 16979 (`asahi-05-kz12-k16`); the fallback is 14585 (carthage-05).
  New candidate bots are built on `asahi-05-kz12-k16`. The diagnostics of D-068 §C stay on carthage-05, so that
  they compare with the placeholder screens already run.

### B. The evaluator's queue and long learn jobs

- Asahi queued D-068 §C's items 2 to 4 with a pre-registration (02:15Z; its forecasts: A1 at λ 1 −4 points, no
  prior −8, λ 1.41 −3). The daemon runs one job at a time and Hinata's network job on the full rows has held it
  since 01:03Z (about 33 minutes a fold, five folds, peak 7.38 GiB). The daemon cannot pre-empt it.
- **Ruling.** The play diagnostics come first. Hinata: if `r2_full.py` keeps finished folds and can resume, cancel
  `hinata-01-a10b-full` now (`build/learn/queue/cancel-hinata-01-a10b-full`) and re-queue it behind Asahi's
  panels; if a cancel loses the finished folds, let it finish.
- **From now on a learn job is at most one fold, or about 45 minutes,** so that panels can run between jobs.
  `hinata-02-a1-full` is re-queued as five fold jobs.
- Kageyama's `bots/kageyama-02-p1-hb1` is on main (merged 01:52Z with r/asahi, r/daichi and r/nishinoya).

### C. Battery

- A5 (encoder, HB-1 vector and the live prior's scores): 0.7267 [0.7179, 0.7361], the highest arm; not selectable
  (two models). It is +0.0043 [+0.0017, +0.0067] over A8b-A1, below the 0.005 bar of D-066 §C.2, so no size-matched
  variant is filed.
- **A11 (encoder plus HB-1 vector, without the live prior's scores, one model) may join the inventory as a
  measurement arm** (Hinata's question, 02:21Z): declared in the inventory file before fitting, fitted in the cloud,
  reported with log-loss, entropy and floor share. No slot work for it until the play diagnostics of D-068 §C are
  in: selection by accuracy is suspended and the slot would need both input paths at once.

## D-070 — 16979's first ranked games; LS-1's pairing range; the time diagnostic; Kenma's scorecard (5 Oct 2026 03:02Z, Chair: Ushijima)

### A. 16979 live: a bad first ten games, no rollback yet

- Daichi (02:55Z): 10 of 40 ranked games, 2 series, 3 wins and 7 losses against teams 303 (Elo 1559, 1–4) and 420
  (Elo 1533, 2–3); score minus expectation −0.439; **Elo 1725 → 1643, rank 90 → 110**. No timeout, no error, at
  most 10.81 M points in all 10 games.
- **Chair's reading: this is two series, and it is not evidence against k = 16.**
  1. In the local census the two bots give the same result on 783 of 816 seed-matched fixtures; they differ
     almost only on Weakhold. A bot that close to its parent is very unlikely to lose 0.4 a game by its own
     change. The local panels do not cover the server's hidden bed layouts, so this is not proof.
  2. In LS-1 the same binary scored 46 wins in 80 games against the parent's 41, same opponents and hours.
  3. The parent's own recent ranked series include 1–4, 1–4 and 2–3 results.
- **Daichi's "contradiction" is the queen rule, not a decoder question.** Since the rules change of 1 Oct (D-040)
  the round-limit order is the longer queen first, then the longest dragon, then total length. A side with the
  longer longest dragon loses at round 500 whenever its queen is dead and the opponent's is alive. Our queen is
  alive at the end of about 1 % of round-limit games. Four of the seven losses are of this kind. It is the
  programme's largest known weakness and no rung of the ladder addresses it at present (cage parked, reach veto
  refuted); the free lane's bot does (§D).
- **Orders to Daichi:** add each side's queen state at the last round (from the replay header) to the scan, and
  14585's ranked record against teams 303 and 420 since the map change. **The rollback rule of D-052 §B is not
  changed:** it is read at 40 ranked games, and at once on any crash or disqualification. Sugawara's forecast that
  it fires within the first 40: 0.08 (02:28Z, before these games were posted).
- The lead may order an immediate rollback at any time; 14585 is one activation away.

### B. LS-1: the pairing range (amends D-069 §A)

Sugawara replicated LS-1 from the job rows. Five cells of opponent 98 hold two candidate games each; the paired mean
is +0.080 with the later game (Daichi's figure), +0.073 with the average, +0.067 with the earlier, and +0.0625 on 80
pairs if the second unit is moved to the five cells it was meant for. Conditions 1 to 4 of D-064 §B hold under
every pairing and LS-1's own letter is HOLD under every pairing. D-069's record stands with the range
**+0.0625 to +0.080**. Adopted for the next screen: the rule for duplicate and colliding cells is frozen in the
gate specification before any outcome is read.

### C. Time and the shape of the prior (Hinata 02:30Z)

- **The clone's accuracy gain over the live prior holds in every phase and every age bucket:** A1 minus A0 by
  phase +0.036, +0.023, +0.021, +0.021, +0.016 (all 5th percentiles above 0); with an empty view +0.022.
- **Time and memory inputs carry 7.2 % of the split gain in A1 and 5.3 % in A3.** For the direction head, time is
  a small part, as D-067 §D expected; the test on the other heads (D-067 §E.6) is still to come. T0 is fitting.
- **Arm T0 (03:01Z): A1 without the round and its 16 memory inputs scores 0.7150; the cost is 0.0034 [+0.0022,
  +0.0046], below 0.005. T1 (phase models) is therefore not run (D-067 §E.3).** Hinata's forecast of a cost of at
  least 0.005 was 0.25. Any phase structure for this head must come from the trajectory block or P-8.
- **Shape:** the live prior puts an option at the floor on 39.0 % of rows; the clones on 1.0 to 11.2 %. Entropy
  0.43 against 0.56 to 0.62. This reproduces Sugawara's reading and is the difference of an order of magnitude
  that D-068 §C tests in play.
- A cancel of the network job would lose its finished folds, so by D-069 §B it runs to its end (about 03:50Z).
  Asahi's diagnostics follow it; the single-team fits follow those.

### D. Kenma (free lane; its lines are data)

- `kenma-03-pocket-queen`: 58–44 against carthage-05 and 61–41 against `kageyama-01-p1-slot` (102 games each);
  pool 220–52 of 272 against carthage-05's 226–46; no error; zip 3,923,010 bytes; at most 10.9 M points.
- Head-to-head it is ahead of the previous live bot; on the pool it is six games behind. Neither difference is
  established. D-067 §F's "pool not below the incumbent's" is read as a paired difference whose 5th percentile is
  above −5 points, on the same host.
- **The reference is now `asahi-05-kz12-k16` (submission 16979).** Kenma is asked for the head-to-head against it.

## D-071 — The lead does not weigh the live rating: uploads are unblocked; the queen defect gets an owner (5 Oct 2026 03:48Z, Chair: Ushijima)

### A. The lead's statement (03:45Z)

The lead does not care about the live rating and asks for the technical issues that need attention at once.

### B. Uploads are allowed again

- D-056 §D barred every upload until the hub restores the active submission by itself, because the server makes an
  uploaded bot active at once. The harm that bar prevented is to the rating, which the lead does not weigh.
- **The bar is lifted.** Live ops may upload a candidate on a Chair record. Straight after the upload Daichi
  restores the intended active submission through the `restore` control and re-reads the live id, and it lists the
  ranked games played in between so that they are left out of every reading.
- H11 (does the hub restart by itself) no longer blocks uploads. It still blocks changes to the hub's own code:
  the upload fix, the blinding of the index, the seat field missing from the job rows, and the end-reason label.
- D-052 §B stays as written. Its purpose now is to keep a worse bot from being the parent of new candidates.
- A free lane's bot still needs D-067 §F's checks and its own request before a live screen.

### C. The queen defect

- Sugawara (03:34Z) read the replays of 16979's losses: all four "longer dragon but lost" games end with reason
  `queen`, as D-070 §A said. Queen-rule losses are 10 of 16979's 16 losses and 29 of 14585's 64. **On Schooltime
  our queen dies by its own move at round 0 in 91 of 91 recent games (1 win); Schooltime is about one ranked game
  in eight.** Outside Schooltime 16979 lost on the queen rule in 7 of 22 games against 16 of 105 for 14585 (small
  n). Sugawara's forecast that D-052 §B fires at 40 games is now 0.75.
- This is the largest defect in the bot and no lane of the programme owns it since D-053 §C parked the cage work.
- **Orders:**
  1. Sugawara reads `kenma-03-pocket-queen` (read only; it is another lane's tree) and reports what its queen
     logic does, on which map structures it acts, and whether it can be stated as one switch on the incumbent
     without map identity. Kenma's own README and by-map tables are data for this.
  2. Asahi, after the D-068 §C queue: one seed-1 pool run of `kenma-03-pocket-queen` with the queen columns (alive
     at the round limit by map, queen-decided wins and losses), on the same host as the incumbent's run.
  3. Daichi keeps the queen-state column in the live scan (D-070 §A).

### D. Housekeeping

- Merged at 03:25Z: r/kageyama (eedd7b6a7, the two logging builds), r/asahi, r/daichi, r/nishinoya.
- Hinata's `r2_full.py` rev 4 (one fold per job), `r2_a11.py` and the inventory file are committed with this
  unit's keeper pass, as Hinata asked at 03:44Z.

## D-072 — Owners for the queen and for the clone in play; the council is dissolved; the hidden bed layouts are to be rebuilt (5 Oct 2026 03:58Z, Chair: Ushijima)

### A. The lead's rulings (about 03:55Z)

1. The hardware is what it is: one Mac, one job at a time. Make do. The desktop will not return.
2. The queen defect is a design and strategy problem: designate someone to solve it.
3. The clone losing in play is the same kind of problem: investigate and handle.
4. The GLM and GPT council members (Nishinoya, Tanaka) are deactivated.
5. The hidden bed layouts: estimate them statistically and recreate the maps.

### B. The council is dissolved

- With one seat left the council cannot review. There are no council rounds, no forecasts to score and no auditor
  until the lead says otherwise. `calibration.md` is closed as it stands; D-064's running event is still scored
  when it resolves.
- Cards are decided by the Chair directly. A result's owner posts its inputs and tool so that any lane can re-run it.
- Nishinoya's open items: the behaviour profile by round (D-067 §E.4) goes to Shenzhen; the review of P-8 is
  dropped (stage S0 is already approved).

### C. The queen: Sugawara owns it

- **Owner: Sugawara.** It leaves the council seat and owns one problem: our queen is alive at the end of about
  1 % of round-limit games (1 of 29 for 16979), queen-rule losses are 10 of 16979's 18 losses, and on Schooltime the
  queen kills itself at round 0 on every side.
- **Goal, in play:** on the pool, more queen-decided wins than losses against the parent and a pool win rate not
  below the parent's; then the same on the ladder. The top ten keep the queen in 24 to 56 % of round-limit games;
  that is the reference.
- **Authority:** Sugawara chooses the mechanisms and their order, writes the changes as switches on the incumbent
  (`asahi-05-kz12-k16`, or carthage-05 if 16979 is rolled back), and queues builds and seed-1 screens with Asahi.
  No card or review is needed for a screen. A candidate that passes D-055 §A's checks goes to a live screen on a
  one-line request to the Chair. Map identity stays excluded.
- **Material in hand:** Shenzhen's result of 03:50Z (C+D gets the Schooltime queen past round 0 on 6 of 6 and wins
  5 of 6; C+D with the reserve wins 6 of 6 but costs on open maps); `asahi-01-cage-cd-e0` (C+D, screened on
  carthage-05: pool +2.2 points [−0.4, +5.2], Portals −12.5); the free lane's `kenma-03-pocket-queen` (6–0 on
  Schooltime; D-071 §C); Daichi's queen column in the live scan; the top-team table (keepers: teams 213 and 507).
  D-053 §C's parking of the cage work is lifted.
- **Support:** Shenzhen is Sugawara's analyst (replay and simulator evidence); Asahi builds and screens.
- Sugawara reports each result in one BOARD line and keeps `claude/sugawara-status.md` as the queen log.

### D. The clone in play: Hinata owns it

- **Owner: Hinata.** The goal changes from accuracy on the teachers' moves to play: a learned prior in the slot
  that is not below the incumbent on the seed-1 pool, then above it.
- **Authority:** after D-068 §C's five tests Hinata chooses the route without a card: temperature or calibration
  of the prior, the weight λ, single-team models, mirror averaging, more data. One declared value per test, no
  sweeps on the panel. Kageyama exports; Asahi screens.
- The battery stays as measurement. The frozen cohort stays unread until a prior wins in play.

### E. The hidden bed layouts: Kageyama rebuilds them (withdraws the limit in D-053 §A item 9)

- The Chair accepted too early that these layouts cannot be rebuilt. The replays show where and when every pearl
  appears; a bed is two integers (first countdown, period); and the oracle is an exact test: a rebuilt map is
  right when the engine re-run reproduces the server's games turn for turn.
- **Order to Kageyama, ahead of the trajectory block:** for each map and variant on which the oracle fails
  (Schooltime open-4, Prisoners Dilemma with 10 dragons, and the timer variants of Slithery Fight, Queen of Spades
  and Devil), estimate each bed's cells and timers from the pearl appearances across that variant's games (an
  older tool, `tools/infer_beds.py`, did this from countdown events the server no longer writes), write the map
  under `maps/live_var/`, and accept it when the oracle reproduces at least 95 % of that variant's games.
- **Uses:** Asahi adds the accepted variants to the pool, so the panels cover the roughly 15 % of ranked games they
  miss today; the 548,724 teacher rows without timers can be rebuilt as oracle rows.

### F. One machine

- Queue order on the Mac: Asahi alternates the clone's and the queen's jobs, starting with D-068 §C's three runs;
  training folds run between panels (D-069 §B). No job longer than about 45 minutes.
- The second runner is dropped.

## D-073 — The hub restarts by itself and is redeployed; the session disk is reset (5 Oct 2026 04:08Z, Chair: Ushijima)

### A. H11 is closed

- The lead closed the hub's Terminal window and started the hub inside the restart loop (new process 04:03:17Z).
- The Chair requested the redeploy at 04:05Z through `hub-state/control/redeploy.json` (51 files hashed, the same list
  as the last accepted request), so that the loop was tested while the lead was at the machine. The hub accepted it:
  gate tests ok, snapshot `67384f265-20261005T040635Z`, exit, and a new process on the new snapshot at 04:06:45Z
  (pid 40226, mode shadow, active 16979). **The loop works. The redeploy ban of D-057 §A is lifted.**
- **Deployed:** the upload fix (`submit_check` restores the active submission), the field reserve of 5 (D-057), and
  the blinding of the index. With the upload fix live, D-071 §B's restore by hand becomes a check: after an upload
  Daichi re-reads the live id and restores only if it is wrong.
- **Still to write and deploy (Daichi, no ban):** the seat in the live-screen job rows, the end reason `queen` in
  `executor.analyse_replay`, and the frozen pairing rule for duplicate cells (D-070 §B).
- Daichi verifies at its next unit that the blinding and the reserve behave as built.

### B. H12: the session disk was reset

- The lead quit the app and moved the session disk image aside at about 04:00Z; the app recreated it.
- The Chair's own shell still fails, now with a permission error on its session folder (the folder did not survive
  the reset). The Chair keeps working by file copy; a fresh Chair session would have a shell.
- Every lane reports in its next line whether its shell works. The backup image is deleted once they do.
- The disk will fill again: each scheduled run leaves a session folder behind. Expect one to three days.

## D-074 — The clone's play tests are in; a ladder trial for the free lane's queen bot; after the disk reset (5 Oct 2026 04:33Z, Chair: Ushijima)

### A. D-068 §C, items 1 to 4: results (Asahi, seed-1 pool, 272 paired fixtures against carthage-05)

| Arm | Pool difference |
|---|---|
| carthage-05 with no direction prior (λ 0) | −13.05 points [−18.38, −7.35] |
| A1-400 (HB-1 features, ten teams) at λ 1 | −13.60 [−19.49, −8.09] |
| A1-400 at λ 1.41 | −5.88 [−11.03, −0.74] |
| A3-400 (encoder trees) at λ 1, from D-068 §B | −6.99 [−12.87, −1.47] |

- Between arms, paired: A1 at λ 1 against no prior −0.55 [−5.88, +4.60]; A1 at λ 1.41 against A1 at λ 1 +7.72
  [+2.94, +12.52]; A3 at λ 1 against A1 at λ 1 +6.62 [+1.47, +12.13].
- Fallback count: 0 in 728,046 dragon-turns on the server-like build (no positive control was run).
- **Reading.** The live prior is worth about 13 points. At its weight the more accurate clone (A1) is worth nothing;
  sharpened it recovers a little over half. The arms order by the sharpness of the prior, not by accuracy on the
  teachers' moves. D-068's leading hypothesis holds. No arm reaches the incumbent.
- The route from here is Hinata's (D-072 §D); its 04:29Z plan (single-team priors next, a blend with the parent's
  prior otherwise, the full-row models when scored) stands without a card.
- **The network on the full rows:** 0.7280 [0.7254, 0.7312] on 2,753,685 moves; on the development games' rows 0.7284,
  +0.0100 [+0.0065, +0.0138] over A1 trained on those games alone (not like for like: 14.6 times the data). Its
  floor share is 26.2 %, far nearer the live prior's 39.0 % than the trees' 1.8 %. A network of 0.5 MB is therefore
  a candidate prior in play and the starting point P-7 needs. Kageyama gives a cost estimate for a network
  inference path in the slot; no build yet. No training by self-play is approved by this record.

### B. A ladder trial for `kenma-03-pocket-queen` (Kenma's request, 04:30Z)

- Its local record: 58–44 against carthage-05, 61–41 against the slot bot, pool 220–52 against 226–46, deploy checks
  pass. The pool is below the incumbent's; Asahi's same-host pool run with queen columns is in progress.
- **Approved as a trial, not a promotion.** The lead does not weigh the rating, and the queen is where we lose.
- **Design, fixed now:** Daichi registers and uploads the bot from Kenma's deploy folder and makes it the active
  submission until the first series boundary at or after **60 ranked games**. Statistic: score minus Elo expectation
  with our rating fixed at activation, series bootstrap, 5th and 95th percentiles, against two references: 14585's
  last 120 ranked games and 16979's window. Also reported: our queen alive at the last round, wins and losses
  decided by the queen rule, and the table by map. Any crash, timeout or disqualification ends the trial at once.
  At the end Daichi restores the incumbent and the Chair rules on the table.
- **Order of events:** Daichi first reads D-052 §B on 16979 (39 games at 04:27Z); the incumbent to restore after the
  trial is whichever that reading leaves (14585 on a rollback). The 12-hour rule of D-069 does not apply to a trial.
- Bokuto's best (`bokuto-07-dodge`, 60–42 against carthage-05 by its own run) gets the same trial after Kenma's,
  once it posts points per turn and its pool panel.

### C. After the disk reset

- Fresh sessions work: Kageyama (pushed 04:27Z) and Asahi. Sessions that were open at the reset lost their shells
  (permission error): the Chair, Hinata's running unit and Bokuto. Hinata's next scheduled run starts fresh. Bokuto's
  tree in `../wt-bokuto` is uncommitted until it has a shell.
- Shenzhen is stopped at the lead's request. Its analyst role under D-072 §C lapses; its findings stand as material
  for Sugawara. Kageyama is asked to run Shenzhen's commit command for its units 36 to 39.
- **The keeper is blocked again** (04:31Z) on a tracked cache file, `tools/learn/__pycache__/rebuild.cpython-310.pyc`.
  The lead is asked to untrack the folder; lanes with a shell move modified cache files aside meanwhile; every
  lane runs main-checkout code with `PYTHONDONTWRITEBYTECODE=1`.

## D-075 — k = 16 is rolled back; the Kenma trial is running; Bokuto's queen bot is next; the bed schedule is solved (5 Oct 2026 05:18Z, Chair: Ushijima)

### A. Submission 16979 (`asahi-05-kz12-k16`) is rolled back (Daichi, 04:53:55Z, under D-052 §B)

- The look: 45 ranked games, 9 complete series since 02:13Z (44 with an expectation). Mean of score minus Elo
  expectation against 14585's last 120 ranked games: difference **−0.263, series-bootstrap 95th percentile −0.126**
  (both conditions of the rule hold: below 0 and below −0.08). Our rating fixed at 1725.
- 16979 alone: 16–28, −0.211 [−0.327, −0.082]; Elo 1725 → 1605, rank 120. No timeout, no caught error.
- Queen column (44 decoded): decided by the queen rule 1 W – 14 L; our queen alive at the end in 4 of 44.
- **The live incumbent is 14585 again** (`carthage-05-free-sprint`). REG-002 is `uploaded`, not live.
- **The cause is not established.** The bot differs from its parent on 33 of 816 local fixtures and scored
  +0.080 [−0.029, +0.187] over 75 live pairs, so a true effect of −0.26 (about 180 Elo) from the switch alone is
  unlikely. Three explanations stay open: noise over nine series; a change in the field during the window; and the
  switch itself exposing the queen (queen-rule losses 14 of 28 by Daichi's scan and 19 of 29 by Sugawara's wider
  count, against 29 of 64 for 14585; outside Schooltime 7 of 22 games against 16 of 105 at 25 games, Sugawara
  03:34Z). §C adds the control that separates the second from the others.
- The rule is not changed and the rollback is not reversed. k = 16 remains a local parent (pool 233–39 against
  226–46) until §D's panel says otherwise.
- **Calibration, D-064 §B's event** (no rollback within the first 120 ranked games): outcome 0. Brier: Tanaka
  0.7225 (0.85), Sugawara 0.7569 (0.87), Nishinoya 0.7225 (0.85). All three seats were confident and wrong, and
  the Chair promoted on the same expectation. Sugawara's later numbers are on record and not scored: 0.08 that the rule fires within 40 games (02:28Z),
  revised to 0.75 at 29 games (03:34Z). The council is dissolved; the calibration file is closed with this entry.

### B. The trial of `kenma-03-pocket-queen` is running (D-074 §B)

- Submission **17388** (`LV-kenma-03-pocket-queen-c5d2ff46-ai`), registered from Kenma's deploy zip, code byte-equal to
  Kenma's tree, runtime e60733a9…. The server activated it when it finished compiling: first ranked series 05:02Z.
  No ranked game of 14585 fell between the restore and the trial. End: the first series boundary at or after 60
  ranked games, about 08:00Z.
- **Amendment to the statistic (made at 05:18Z; the Chair had seen one trial series, 2 wins and 2 losses of 5, in
  the hub's state file, and nothing else).** Daichi anchored the trial at our rating at activation, about 1605.
  That rating is the product of 16979's 45 games. If the trial bot is nearer 1725 in strength, an anchor of 1605
  credits it about +0.16 a game for nothing, and the comparison with 14585's window (anchor 1725) is biased
  upward. **Primary statistic for every window in §B and §C: mean of score minus expectation with our rating fixed
  at 1725, series bootstrap, 5th and 95th percentiles.** Also reported for each window: the performance rating
  (the rating at which the window's score equals its expectation) with the same bootstrap, and the figure at the
  activation anchor.
- Unchanged: queen alive at the last round, queen-rule wins and losses, the table by map; a crash, timeout or
  disqualification ends the trial at once.

### C. Second trial, the control, and the rule at the end

- **`bokuto-04-queen` gets the same trial directly after Kenma's**, without a return to 14585 in between. It is
  chosen over `bokuto-07-dodge` because it has the same-host pool with queen columns (§D); if Bokuto posts a
  same-host pool for a later version before the first trial ends, the Chair may swap it.
- Conditions before the upload: Asahi runs the deploy probe on the tree it used for the pool (runtime ff68a709…): zip
  at most 4 MiB, at most 30 M points a turn with the first turn included, four heavy-map games, no error. Daichi
  registers from a byte-exact copy of `../wt-bokuto/bots/bokuto-04-queen` and checks the runtime fingerprint.
  Bokuto's tree is not edited. If the probe is not in when the first trial ends, the control below runs first.
- **Control:** after the trials Daichi restores 14585. Its next 60 ranked games are read with the same statistic
  against its own last 120 games before 02:13Z. A difference near zero says the field did not move and 16979's
  window was the bot or noise; a difference near 16979's says the field moved.
- **Rule at the end, fixed now.** The lead does not weigh the rating, so a switch costs nothing and no significance
  test is needed. Of the three windows (17388, Bokuto's, 14585's control) the bot with the highest primary
  statistic becomes the incumbent, provided it had no fault; a lead under 0.03 over 14585's control keeps 14585.
  The windows are about 60 games each and three hours apart, so the choice is noisy; it is the best available
  estimate and can be revised by a later window. D-052 §B then applies to the chosen bot as to any incumbent.

### D. The free lanes' bots, measured on our harness (Asahi, seed-1 pool, 272 paired fixtures)

| Bot | Pool | Against carthage-05 | Against k = 16 | Queen-decided W–L | Queen alive at the round limit |
|---|---|---|---|---|---|
| `carthage-05-free-sprint` | 226–46 | | | 0–5 | 0 of 146 |
| `asahi-05-kz12-k16` | 233–39 | +2.6 points | | 0–5 | 0 of 146 |
| `kenma-03-pocket-queen` | 220–52 | −2.21 [−4.41, −0.37] | −4.78 [−7.72, −1.84] | 13–4 | 15 of 147 (14 on Schooltime) |
| `bokuto-04-queen` | 226–46 | 0.00 [−5.15, +4.78] | −2.57 [−7.35, +2.21] | 42–4 | 44 of 189, on 11 of 17 maps |

- Head to head, 102 games each, the lanes' own runs: kenma-03 against carthage-05 58–44, against k = 16 57–45,
  against bokuto-04 54–48; bokuto-04 against carthage-05 58–44; `kenma-21` 60–42 and `bokuto-07-dodge` 60–42 against
  carthage-05 (no same-host pool yet).
- Costs: Kenma loses on Australia and UNSW (every non-queen plans with one unit slot reserved, all game); Bokuto
  loses economy (−6.3 [−9.5, −2.7]) and Queen of Spades, UNSW, Autarky, Default, Dilemma.
- **Reading.** Bokuto keeps its queen at the top ten's rate (23 % of round-limit games; theirs 24–56 %) across
  maps and holds the pool level. Kenma's logic acts on Schooltime. The pool's opponents rarely keep a queen, so a
  queen kept there wins by default; the ladder trials measure the same thing against teams that do keep theirs.
- **For the queen owner (Sugawara decides; D-072 §C).** The build order of 04:38Z (Kenma's pocket first, then the
  grow rule, Bokuto's block last) was written before Bokuto's pool result. The broad mechanism is now the one
  with evidence at pool parity. The Chair asks Sugawara to move Bokuto's caution and crown block beside or ahead of
  the grow rule, or to say why not. Ordered in any case: the 68-game queen-keeper panel (against `bokuto-04-queen`
  and `kenma-03-pocket-queen`) is run for **both parents**, carthage-05 and k = 16, before the builds are read. It
  shows whether the k = 16 veto costs the queen against opponents that keep theirs (§A's third explanation).

### E. The clone in play (Hinata's route, D-072 §D)

- All ten of Hinata's learn jobs failed at 04:37–04:39Z on a missing library (`libomp` for LightGBM on the Mac).
  Asahi fixed the runner and re-queued them unchanged; the first two have finished.
- **Single-team priors (D-068 §C.5), fitted on the full rows:** team 213 **0.7541** [0.7476, 0.7603] on its own
  268,722 moves (63 series), team 91 0.7133 [0.7092, 0.7175] on 222,647 (40 series). The pooled network scores 0.6962
  and 0.6841 on the same rows: a pooled clone gives up 3 to 6 points on any one teacher. Shape of the 213 model:
  entropy 0.561, floor share 2.4 % (the pooled A1 on 213's development rows 0.635; the live prior 0.43 and 39.0 %).
- Hinata's first route candidate is the 213 prior at λ 1. Kageyama exports it first (same path as
  `kageyama-02-p1-hb1`), ahead of the remaining bed variants: it is short and it unblocks a Mac job.
- **The Chair's forecast for the 213 prior at λ 1 on the seed-1 pool:** about −8 points; 0.12 that it is not below
  the incumbent (paired 5th percentile above −5). It is sharper than the ten-team clone and still softer than the
  live prior, and §A of D-074 says the arms order by sharpness. The Chair asks Hinata to queue beside it one arm at
  the weight λ at which the tempered prior's mean entropy on the development rows equals the live prior's (one
  value, computed before the run),
  so that team style and sharpness are separated in one pass. Both runs report the queen columns: 213 keeps its
  queen, and a prior cloned from it may carry some of that.

### F. The hidden bed layouts (Kageyama, D-072 §E)

- **The schedule is solved exactly.** The engine draws every bed countdown from `mt19937_64(seed)`: countdown =
  lo + (u mod (hi − lo + 1)); the symmetric pairs draw in row-major order of the first cell at round −1 and again at
  each expiry. A Python emulator matches the engine on 11 maps × 2 seeds, every pair, 500 rounds. A candidate bed
  list is checked against a server game in milliseconds.
- **Devil, second layout:** 380 of 777 post-m2 Devil games (49 %) are on it; a list of 38 pairs fitted on 150 games
  explains every pearl appearance in all 380; the oracle reproduces 20 of 20 Devil games that failed before, turn
  for turn. This meets D-072 §E's acceptance (at least 95 %).
- Queen of Spades, Slithery Fight, Schooltime (open-4) and Prisoners Dilemma (10 dragons) follow by the same method.
- The withdrawal in D-053 ("cannot be rebuilt") was wrong, and the lead's objection to it was right.
- **Ordered for when `maps/live_var/` is merged:** Asahi adds each variant as pool fixtures (same opponents, seats
  and seed), re-zeros carthage-05, k = 16, `kenma-03-pocket-queen` and `bokuto-04-queen` on them, and from then on
  every pool card shows two totals: templates only (comparable with the past) and weighted by each layout's share
  of live games. R0 item 9 is reopened until then.

### G. Housekeeping

- The keeper's passes at 04:54Z and 05:12Z show no error; the cache-file block of 04:31Z is gone.
- Shells after the reset: Sugawara, Daichi, Kageyama and Asahi work in fresh sessions. The Chair's device shell
  still fails; it works by file copy. Bokuto's shell is down; its tree in `../wt-bokuto` is uncommitted.
- Daichi's remaining hub items: the seat field in job rows, the end reason `queen`, the frozen pairing rule.
- Not yet reported: whether Shenzhen's units 36–39 were committed on its behalf.

## D-076 — Ratings belong to submissions, so trials are free; trial 2 may be Bokuto's newer bot; the queen order is amended (5 Oct 2026 06:19Z, Chair: Ushijima)

### A. A fact about the ladder: each submission has its own rating

- Source: the organisers' rating page (`game.battlecode.au/docs/elo`, read 06:18Z): "Each submission (bot) has its
  own rating". The team's rating is the active submission's, averaged over the ranked maps, with an offset per map.
  Re-activating an older submission brings back its rating. A new submission starts from the rating of the one it
  replaces, with more uncertainty, so it moves fast at first.
- Daichi's snapshots agree: 1605 at 04:47Z (16979), **1721 at 04:58Z** (14585 restored), then 17388's own path
  (1702, 1778, 1767 at 05:50Z, rank 78).
- **Consequences.**
  1. A trial costs the incumbent nothing: 14585 keeps its rating while another submission plays. The only cost is
     time on the live slot, about 20 ranked games an hour.
  2. 16979's fall of 120 points in 45 games is partly the speed of a new submission's rating. The rollback rested
     on score minus expectation, which does not depend on that; D-075 §A stands.
  3. Daichi's correction (05:53Z): the rating at the trial's start was 1721, not 1605. The bias D-075 §B guarded
     against did not occur. The statistic stays anchored at 1725 for every window.
  4. For the lead: the rating shown at any moment, the deadline included, is that of whichever submission is
     active then.
- **Trials from now on.** A candidate may be queued for a 60-game ladder trial when it has a passing deploy probe
  and a same-host seed-1 pool whose paired 5th percentile against carthage-05 is above −5 points. The Chair orders
  the queue. The end rule of D-075 §C applies to every window: highest primary statistic, lead under 0.03 keeps the
  incumbent.
- Disclosure: Daichi's 05:53Z line carries an interim reading of trial 1 at 25 games, and the Chair has read it.
  The end rule was fixed at 05:18Z and is unchanged; the look is at the first series boundary at or after 60 games.

### B. Trial 2: `bokuto-13-cull` if it holds on our harness, otherwise `bokuto-04-queen`

- `bokuto-04-queen` passed its deploy probe (Asahi, 05:53Z): zip 3.75 MiB, at most 12.86 M points a turn, first turn
  at most 12.47 M, no error in 10 games. Daichi holds a byte-exact copy.
- Bokuto reports `bokuto-13-cull` at **70–31–1** against carthage-05 (102 games; `bokuto-08-yield` 65–37,
  `bokuto-04-queen` 58–44). The figure comes from the scorecard Bokuto iterates on, the same fixtures against the
  same opponent, so it overstates; the pool is the check.
- **Rule, fixed now.** Asahi runs the same-host seed-1 pool with queen columns and the deploy probe on
  `bokuto-13-cull`, ahead of the other jobs, and posts both by 07:45Z. If its pool wins are at least 226 (bokuto-04's
  count) and the probe passes, trial 2 is `bokuto-13-cull`. Otherwise, or if the results are late, trial 2 is
  `bokuto-04-queen` as ordered. The trial is run for the outcome, not to isolate a mechanism; Sugawara's builds do
  the isolating.

### C. The queen (Sugawara's answer to D-075 §D, accepted)

- **Correction to D-075 §D's reading.** Sugawara's paired read of the pool: of `bokuto-04-queen`'s 42 queen-decided
  wins, 38 are fixtures carthage-05 also won; 4 are rescues. Its pool parity is 31 gains against 31 losses (62 of
  272 fixtures differ; k = 16 differed from its parent on 4 %). The bot stacks three layers (a guard and cage
  split, a branch gate, the queen block). So the pool shows how Bokuto wins, not that queen keeping wins; neither
  its economy cost nor its gains can be put on the queen block. Asahi's "pays for itself" and the Chair's
  repetition of it are withdrawn.
- **Amended build order (Sugawara's, on carthage-05, not k = 16):** `sugawara-q1-cage` (Kenma's pocket without the
  reserved slot; Asahi's `asahi-21-q1cage-c05`); then `sugawara-q2b-crown` (carthage-05 plus only Bokuto's queen
  lines: no queen split after round 60, more caution, a crown rule; `asahi-25-q2bcrown-c05`, 32 changed lines); the
  grow rule q2a is parked. Optional: the pool of `bokuto-02-vac` to separate Bokuto's layers.
- **Queen-keeper panel (68 fixtures against `bokuto-04-queen` and `kenma-03-pocket-queen`, seed 1):** carthage-05
  32–36, k = 16 35–33; queen-decided 0–6 and 0–7; our queen alive at the round limit 0 of 47 and 0 of 48. k = 16
  minus carthage-05 +4.41 points [−1.47, +10.29]. **D-075 §A's third explanation (the veto exposing the queen) gets
  no support locally.** Neither parent ever keeps a queen against opponents that do; both lose Schooltime 0–4.
- Owner's forecasts on file: q2b's pool 5th percentile above −5 points 0.55; q2b at least +5 points over carthage-05
  on the keeper panel 0.40.
- **First results of the isolating builds (Asahi, 06:19Z, arrived while this record was written; seed 1).**
  - q1-cage on carthage-05: 270 of 272 pool fixtures identical to the parent, both differences on Schooltime; pool
    226–46, equal to the parent; queen-decided 3–5 (parent 0–5); Schooltime queen alive 3 of 14 (Kenma's bot with
    its reserved slot: 14 of 14). Keeper panel 34–34 against 32–36, +2.94 points [0.00, +5.88].
  - q2b-crown on carthage-05: pool 219–52–1, **−2.39 points [−5.89, +0.92]**; queen-decided 16–5; queen alive 17 of
    149 (15 on Trauma); Maze −37.5. Keeper panel 27–41 against 32–36, **−7.35 [−16.18, +2.94]**; against
    `bokuto-04-queen` itself 12 of 34 (carthage-05: 16 of 34).
  - Both of the owner's forecast events failed (0.55 and 0.40; Brier 0.3025 and 0.16, not council-scored).
- **Chair's reading.** Neither queen mechanism transfers as one switch onto carthage-05. The cage needs the
  reserved slot to hold the Schooltime queen; Bokuto's queen lines alone cost wins and lose to their source. Queen
  keeping in the free lanes' bots depends on the rest of each bot. Adding layers to carthage-05 one at a time has
  now failed twice at the first step. The Chair suggests the opposite direction to the owner: take the stronger
  free-lane bot as the base and remove one layer at a time (leave-one-out), so that each layer is measured in
  the context where it works. The ladder trials say whether such a base is worth adopting. Sugawara decides.

### D. The clone (Hinata)

- **On equal rows the trees beat the network.** A1 on the full rows: 0.7379 [0.7352, 0.7409]; against the network
  +0.0099 [+0.0089, +0.0107], positive on all 14 maps, +0.042 on queen rows. The network is the sharper of the two
  (floor share 26.5 % against 9.6 %). D-074 §A's sentence that a small network is the candidate prior is amended:
  the pooled slot candidate is A1 on the full rows (refit queued); the network stays P-7's route only by
  distillation (D-063 §D). Kageyama's estimate for a network inference path moves behind the bed layouts.
- A11 (encoder and HB-1 vector in one model) 0.7264, equal to A5: the parent's prior adds nothing as an input.
- **Entropy-matched weights, computed before any game:** 1.45 for the team-213 model, 1.72 for A1-400. So the
  λ 1.41 arm of D-074 was still softer than the live prior (0.483 against 0.423 nats).
- Arms, in Hinata's order: the 213 prior at λ 1 and λ 1.45 once Kageyama's export lands; A1-400 at λ 1.72 (no
  export needed). The Chair asks Asahi to run the λ 1.72 arm as the next clone job now, since nothing blocks it and
  it tests sharpness with content fixed.
- **Chair's forecasts (pool difference against carthage-05; P that the paired 5th percentile is above −5):**
  A1-400 at λ 1.72: −2 points, 0.35. The 213 prior at λ 1.45: −4 points, 0.25. (At λ 1: −8, 0.12, D-075 §E.)
- Hinata's caution is recorded: on other teams' moves the 213 model predicts no better than the live prior
  (0.6954 against 0.6977).

### E. Housekeeping

- The unit-25 merges went through (05:23Z). Kageyama has not posted since 05:00Z; its export of the 213 model gates
  two arms. Bokuto's shell is still down; its trees reach other lanes by file copy only.

## D-077 — Trial 2 is `bokuto-13-cull`, the best bot we have locally; the control is dropped; a stop rule for the clone prior (5 Oct 2026 07:23Z, Chair: Ushijima)

### A. Trial 2 is `bokuto-13-cull` (D-076 §B's rule, both inputs in at 07:20Z)

- Same-host seed-1 pool (Asahi): **241–31**. Against carthage-05 (226–46) **+5.51 points [+2.19, +9.19]**; against
  `bokuto-04-queen` +5.51 [+1.47, +9.56]; against k = 16 (233–39) +2.94 [−0.74, +6.99].
- Queen columns: decided by the queen rule 92 W – 2 L; **queen alive at the round limit in 94 of 163 games, 58 %**
  (the top ten: 24–56 %); on Schooltime 16 of 16, Trauma 15 of 15, UNSW 13 of 16. Economy level with the parent
  (−0.60 [−3.62, +1.97]).
- Costs and flags: Stripes 4–12, Autarky and Portals −12.5; deaths by head-on with an ally +14.5 %.
- Deploy probe: zip 3.75 MiB; at most 12.38 M points a turn, first turn included; no error in 10 games.
- 241 ≥ 226 and the probe passes, so the rule selects it. Daichi registers from a byte-exact copy of
  `../wt-bokuto/bots/bokuto-13-cull` and checks the runtime fingerprint d192d721…. Registry: REG-007.
- It is the largest gain over carthage-05 measured on our pool (k = 16 gave +2.6 at seed 1) and the first of our
  bots whose queen survives across maps. Two cautions: Bokuto has run this pool during development, so some of the
  gain may be fitted to it; and the pool's opponents rarely keep a queen. The ladder trial is the out-of-sample
  test.
- **Chair's forecasts for trial 2** (primary statistic at rating 1725): point +0.10; 0.75 that it exceeds 14585's
  reference by more than 0.03; 0.60 that it is the highest of the three windows.

### B. The control window is dropped; the end rule is applied at trial 2's look

- D-075 §C ordered a 60-game control on 14585 after the trials, to see whether the field moved during 16979's window.
  It would hold the live slot for three hours. Two things have changed since: the slot's time is the only cost of a
  trial (D-076 §A), and there is now a candidate worth more exposure than the control is worth.
- **Amendment.** 14585's window for the end rule is its last 120 ranked games before 02:13Z (−0.043 [−0.109, +0.028]
  at rating 1725, performance rating 1694; Daichi 05:53Z). The control runs only if both trial windows come in below
  −0.15, which would point to a change in the field. Otherwise, at trial 2's look, the bot with the highest primary
  statistic among 17388's window, trial 2's window and 14585's reference becomes the incumbent at once and stays
  live; a lead under 0.03 over 14585's reference keeps 14585.
- Disclosure: this is made after the Chair read trial 1's interim at 25 games (D-076 §A). The change does not
  favour either trial bot against the other; it compares both with 14585's earlier window instead of a later one.
- The incumbent's further ranked games are diagnostic material: Daichi's scan with queen columns and the table by
  map runs on them at every unit, and the free lanes and Sugawara read the losses.

### C. `bokuto-13-cull` is the local reference from now on

- New candidates' pool cards are paired against `bokuto-13-cull` as well as carthage-05. Sugawara's leave-one-out
  uses it as the base, as its plan says. `bokuto-02-vac` alone is 195–77 (−11.40 points [−16.91, −5.51]): the
  first layer costs 31 wins and the later layers win them back and more.
- **The bot exists only as uncommitted files in `../wt-bokuto` and as byte copies.** Asahi commits its byte copies
  of `bokuto-04-queen` and `bokuto-13-cull` (with the source fingerprint files) on `r/asahi` and asks for a push, so
  that both are in git. Bokuto's tree is not touched.

### D. Compute goes first to the line that produces wins

- In about six hours a free lane has produced the largest local gain of Phase 3 (+5.5 points). The ladder's own
  lines have given +2.6 from the hand rule, which then failed live, and nothing from the clone prior or the
  isolated queen builds. Bokuto did it on two cloud cores with no shell. This is evidence, and by the lead's rule evidence follows precedent: the allocation changes, the
  strategy text is not rewritten on one pool result.
- **Mac queue order from now:** (1) one same-host pool and one deploy probe an hour for each free lane, on request
  by a BOARD line naming the bot; (2) the bed-variant fixture block and its re-zero (D-075 §F), with
  `bokuto-13-cull` among the bots; (3) Sugawara's leave-one-out builds; (4) the three clone arms of §E; Hinata's
  one-fold learn jobs between them as before.

### E. The clone prior: sharpness explains about half the gap; a stop rule

- A1-400 at its entropy-matched weight (λ 1.72): pool 206–66, **−7.35 points [−12.15, −2.21]**. The curve for this
  model is −13.60 at λ 1, −5.88 at λ 1.41, −7.35 at λ 1.72. Past λ of about 1.4 nothing more is recovered: at equal
  sharpness the ten-team clone is still 6–7 points below the one-team Heartbreaker prior. D-074 §A's reading
  ("arms order by sharpness") holds up to that point only; the rest of the gap is content.
- The Chair's forecast (−2 points; 0.35 that the 5th percentile is above −5) failed. Brier 0.1225.
- **Remaining arms:** the team-213 prior at λ 1 and λ 1.45 (Kageyama's export is in: parity on 111,592 of 111,592
  turns, zip 1.075 MiB), and A1 on the full rows at λ 1.76 once exported. Forecasts on file: −8 and −4 points for
  the 213 arms; the Chair adds −6 points and 0.15 for A1-full.
- **Stop rule, fixed now.** If none of the three reaches a paired 5th percentile above −5 points against
  carthage-05, the line "a cloned direction prior in the carthage-05 search" is paused: no further arms of the
  same family on the Mac. Hinata then proposes one next route with a forecast. The Chair's candidates, for Hinata
  to weigh: clones of the decisions the free lanes now hand-code (cull, split, corridor targeting; R3), fitted
  and tested on the new base; or a value model trained on that base's self-play.
- The network inference estimate asked of Kageyama in D-074 §A is cancelled (the trees lead on equal rows, D-076 §D).

### F. Data (Kageyama)

- **R0 item 9 is closed; D-072 §E is done.** All five hidden layouts are rebuilt: 828 of 828 variant games
  reproduce turn for turn; the variants carry 14.46 % of ranked post-m2 games (4,598), about 3 % each. Maps in
  `maps/live_var/`, labels in `docs/learning/datasets/kageyama-bed-variants-v1.json`. Merged at 06:43Z.
- The team-213 and team-91 slot bots are accepted for screening (`bots/kageyama-02-p1-hb1-t213`, `…-t91`).
- **The trajectory block of D-067 §E.7 is built:** seven columns per process from its own turns (unit-count change
  over 20 and 100 rounds, length change, rounds since an enemy was seen, contact counts), with a C++ twin at parity
  on 255,152 turns. First users: P-8 stage S0 and the R3 offline fits.
- Next for Kageyama: the A1-full export (one model file), then the teacher rows on the variant maps rebuilt as
  oracle rows.

## D-078 — Trial 1's table; trial 2 is uploaded; the single-team clone fails; a tie rule between the trial bots (5 Oct 2026 08:17Z, Chair: Ushijima)

### A. Trial 1: `kenma-03-pocket-queen` (submission 17388), Daichi's look at 60 ranked games

- Window 05:02–07:13Z, 60 games, 12 series, 31–29. **Score minus expectation at rating 1725: +0.074
  [−0.048, +0.197]**; performance rating 1781 [1686, 1876]. Against 14585's reference (−0.043 [−0.109, +0.028]):
  +0.117 [−0.018, +0.269]. No fault. Lost by the queen rule: 7 of 60.
- By map: Trophy 1 of 6, Prisoners Dilemma 0 of 2, UNSW 0 of 2, Weakhold 0 of 1; Portals 5 of 8, Islands 4 of 6,
  Stripes 3 of 4, Maze 3 of 4. **No Schooltime game fell in the window**, and Schooltime is where this bot's change
  acts. The window therefore measures a carthage-05 with one unit slot reserved, not the pocket logic.
- **Reading.** The bot played at about the incumbent's level or a little above; the interval includes zero and
  the mechanism was not exercised. Nothing is concluded yet; the end rule is applied at trial 2's look.
- **Check ordered (Daichi):** no Schooltime in 12 series is a 1.5 % event if each series draws five different maps
  of 17 (0.4 % for the 16 series to 07:52Z). Count ranked Schooltime games of all teams in the corpus since 05:00Z
  and say whether the map is still in the ranked draw. If it is not, the weights of every local total change.

### B. Trial 2: `bokuto-13-cull` is uploaded as submission 17530

- Registered 08:01Z from a byte copy (16 files equal; runtime d192d721…, the fingerprint of Asahi's probe); uploaded
  08:14:33Z as `LV-bokuto-13-cull-877fa2c9-ai`. The activation call returned 409 while the server compiled, as for
  17388; the server activates on ready. Window: its first 60 ranked games; look at the first series boundary at or
  after 60.
- Sugawara's request is adopted: the look also reports Schooltime (both layouts) apart from the rest.
- **Out of sample, locally (Asahi's variant block, 80 fixtures Bokuto never saw):** `bokuto-13-cull` 72 of 80 against
  carthage-05's 63. Eight of the nine come from `schooltime_open4` (15 against 7); the other four layouts are 57 of
  64 against 56. Weighted by each layout's share of live games: **+5.75 points [+2.97, +8.62]** (k = 16 +2.21;
  `kenma-03-pocket-queen` −1.61). So the Schooltime-family gain transfers to unseen layouts; the rest of the pool
  gain is unconfirmed out of sample at this size (Sugawara's read).

### C. A tie rule between the two trial bots, fixed before any game of trial 2

- D-075 §C takes the highest window with no test. Between two 60-game windows the standard error of the difference
  is about 0.10. As written, the rule would crown `kenma-03-pocket-queen` on a difference that is noise, against a
  local pool that puts `bokuto-13-cull` 21 wins ahead of it (241 against 220 of 272).
- **Amendment.** Between the two trial bots the live windows decide only if they differ by more than 0.10; within
  0.10 the same-host pool decides, which means `bokuto-13-cull`. The comparison with 14585's reference is unchanged
  (a lead under 0.03 keeps 14585). The control still runs only if both windows are below −0.15.
- Disclosure: made after trial 1's table and before trial 2's first game. It favours the bot the local evidence
  favours; the Chair judges that correct and says so here, not afterwards.

### D. The clone prior: five arms in, one to come

| Arm (seed-1 pool against carthage-05) | Difference | Chair's forecast |
|---|---|---|
| Team-213 prior at λ 1 | −12.50 points [−17.28, −7.35] | −8; 0.12 above the bar |
| Team-213 prior at λ 1.45 | −12.68 [−17.83, −7.54] | −4; 0.25 |
| Ten-team A1-400 at λ 1.72 (D-077) | −7.35 [−12.15, −2.21] | −2; 0.35 |

- Sharpening the single-team model buys nothing (λ 1.45 minus λ 1: −0.18 [−5.51, +4.42]); at matched sharpness it
  is worse than the ten-team clone (−6.80 [−12.32, −1.83]). Neither of D-068's two hypotheses, softness and style
  mixing, rescues a cloned direction prior in this search. The 213 model's accuracy on its own team's moves
  (0.754) did not carry into play, as with the pooled arms.
- All three of the Chair's forecasts were too optimistic (Brier 0.0144, 0.0625, 0.1225). Hinata's were closer.
- One arm remains under D-077 §E: A1 on the full rows at λ 1.76, after Kageyama's export. It runs at the back of
  the queue. If it fails the bar the line is paused without a further record.
- **P-9 (`P-hinata-05`): a learned cull gate for `bokuto-13-cull`, fitted from the bot's own randomisation.** The
  bot culls on a state-independent 1-in-8 draw, so every pool game already holds bandit data with known propensity.
  **Stage S0 is approved to start now**: a diagnostic on existing replays, no Mac time, no bot change, held-out
  maps excluded. Stage S1 (one gate export, one seed-2 pool paired against the base) needs the Chair. Author's
  forecast for S1: +1 point; 0.30 that the point is positive and the 5th percentile above −3. The base bot's hash
  gate stays unchanged in every copy used for pools, as Hinata asks.

### E. A lead for whoever builds on `bokuto-13-cull` (Sugawara's note)

- The inherited map atlas seeds pearl-bed beliefs from the template when the terrain matches. Four of the five
  hidden layouts share their template's terrain, so on about 11 % of ranked games the bot believes the wrong beds
  until it sees them, and Bokuto's branch gate reads those beliefs. Kageyama's bed lists make a fix possible: hold
  both layouts as hypotheses and drop one at the first pearl that contradicts it. No harm is measured locally; this
  is offered to the free lanes and the queen owner, not ordered.

### F. Housekeeping

- The unit-27 commit and merges went through. Asahi committed the byte copies of `bokuto-04-queen` and
  `bokuto-13-cull` on `r/asahi` (17d7574d5), so the trial-2 bot is in git.
- Bokuto has not posted since 05:50Z; no sign of a fresh session.
- **The BOARD was overwritten at 08:17:14Z with its 05:50Z state** (100 lines gone). The Chair restored it at
  08:19Z byte for byte, from its 07:25Z copy and the 19 later lines held in its session log (1,323 lines, the size
  it had at 08:16Z). The cause is a stale file sent through the file bridge, almost certainly by the old Bokuto
  session, which has no shell: the state written back is the one right after its own last write. Rules posted:
  stage immediately before appending, a new output directory for every write, the modification-time guard always,
  never force; the old Bokuto session does not write to the BOARD again. A line appended between 08:16Z and
  08:17Z, if any, is lost.

## D-079 — Kenma is retired; the BOARD was overwritten twice; the cull-gate route is closed; what the planned lines have produced (5 Oct 2026 09:17Z, Chair: Ushijima)

### A. Kenma (the GPT free lane) is retired

- The lead reports it out of credits. Its files stay as material; nobody owns them and anyone may copy.
- What its last runs left in `build/kenma/` (its own harness, 102 games each, no error; read by the Chair from the
  progress logs):

| Run | Result |
|---|---|
| `kenma-28-harvest-reserve` against carthage-05 | 72–30 |
| `bokuto-13-cull` against carthage-05 (Kenma's control) | 73–29 |
| `kenma-21` against `bokuto-13-cull` | 34–68 |
| `kenma-21` against `kageyama-01-p1-slot` | 55–47 |
| `kenma-21`, pool of 272 | 228–44 |

- `kenma-28-harvest-reserve` names `bokuto-13-cull` (d192d721…) as its parent and adds Kenma's pocket and
  reserved-slot components. It shows no gain over that parent on the same harness. Kenma had moved onto Bokuto's
  base before it stopped.
- A second, independent harness therefore agrees that `bokuto-13-cull` is the strongest bot locally (73–29 against
  carthage-05; Bokuto's own run 70–31–1).
- Ordered of Asahi (08:59Z): byte copies of `kenma-03-pocket-queen`, `kenma-21` and `kenma-28-harvest-reserve` on
  `r/asahi`; a report on uncommitted work in `../wt-kenma` and on any Kenma process still running; the same-host
  pool, variant block and probe for `kenma-28-harvest-reserve`. Registry: REG-008.

### B. The BOARD was overwritten twice by the old Bokuto session

- 08:17:14Z: replaced by its 05:50Z state (100 lines gone); restored 08:19Z (D-078 §F).
- 09:05:05Z: replaced by the file that session had built at 08:17Z (lines 1 to 1,323 plus its own request for a
  ladder screen); the 12 lines from 08:19Z to 08:59Z were gone. Restored 09:06Z from the Chair's 08:59Z copy, byte
  for byte, with Bokuto's line kept below the notice. Git holds the restored file (af5154501).
- Lines appended by others between 08:59Z and 09:05Z, if any, are lost; lanes were asked to post again.
- Cause: a session without a shell writing whole-file copies through the file bridge from stale stages. The lead
  is closing that session and starting a fresh one. The Chair keeps a copy of the BOARD at every unit and asks for
  a keeper pass after every restore.

### C. The cull-gate route (P-9) is closed at its first stage

- Sugawara found before any number was read that the bot's cull draw is not a per-turn coin: each dragon is hit on
  one fixed round in every eight. The unit became the eligibility spell and the instrument the delay to the hit.
  Hinata accepted the amendment and froze it at 08:37Z.
- Result: P(cull | shortest delay) minus P(cull | longest delay) = 0.0179 [0.0129, 0.0228], against a bar of 0.25.
  When the hit round is reached inside a spell the bot culls 2 % of the time; other gates block the rest. The logs
  cannot teach a cull decision. No effect was computed. The route stops, as its own rule says.
- Forecast on file: Sugawara, usable first stage 0.45 (outcome 0; Brier 0.2025, not council-scored).
- Hinata intends to file a self-play value-model card next. **It may be filed; no compute is approved for it
  before the trial-2 look, and the Chair's present intention is not to fund it** (the author's own forecast for
  that route was 0.08).

### D. What the planned lines have produced (the lead's question, 09:05Z)

- **In playing strength: nothing that survived.** The clone prior: six priors tested in the search, all 6 to 14
  points below the live one. The hand rule: +2.6 points locally, −0.26 a game live, rolled back. The isolated queen
  builds: no gain and a loss. The value model failed; the cull gate stopped at its first stage.
- **As services: three lanes carry everything else.** Asahi's harness (pools, probes, the variant block), Daichi's
  live operations (two clean trials, the rollback, the rating finding), and Kageyama's data work (the bed
  schedule and five hidden layouts, which gave the first out-of-sample check of a candidate).
- **Nothing from any lane is confirmed on the ladder yet.** Trial 2's interim (Daichi, 08:51Z; 25 games, not the
  look): `bokuto-13-cull` 10–15, −0.193 a game at rating 1725. If that holds at 60 games, two local gains in a row
  (k = 16, and this one, which two harnesses agree on) will have failed to carry, and the bottleneck is the local
  pool's power to predict the ladder, not the supply of candidates.
- **Chair's intentions, told to the lead:** no change before the look (about 11:15Z); the clone-prior line pauses
  when its last arm reports; Asahi, Daichi and Sugawara continue as they are; whether Hinata's and Kageyama's lanes
  are stood down or become a builder lane is the lead's decision after the look.
- **Prepared now, dispatched only by a later record:** Daichi drafts a paired live screen through the battles
  control (candidate and reference against the same chosen opponents, in the same hour, without the live slot):
  `bokuto-13-cull` and `kenma-03-pocket-queen` against 14585 on six opponents, two near our rating, two near 1900
  and two of the top ten, sized from the field quota. At the look Daichi also splits both trial windows by
  opponent rating (above and below 1725).

## D-080 — Why the local gain is not carrying: the queen race after round 100; the clone-prior line is paused; a ruling on map atlases (5 Oct 2026 10:18Z, Chair: Ushijima)

### A. Two independent reads of submission 17530's ladder games agree

- **Bokuto (fresh session, 30 ranked games, 09:32Z).** On the ladder the queen is alive at round 100 in 67 % of
  games, at round 200 in 50 %, at the end in 17 % (the pool: 58 %). When both queens live we lose the length race
  (Australia 11 against 38). Census of 6,479 ranked games between sides rated at least 1650: at the round limit,
  with the enemy queen alive, a queen 1–3 long wins 45 % and a queen 26 or longer wins 75 %. The top teams hide
  the queen at length 2–3 until round 250–300 and then feed her to 30–60 and more. `bokuto-13-cull` starts feeding
  at round 400–430 and ends with a queen of 3–13.
- **Hinata (P-hinata-06, card frozen before reading; 40 games).** In its losses 17530 is ahead at round 100 (27.8
  units against 21.0); the losses end late (mean round 460); 52 % of them are by the queen rule, against 34 % for
  14585; 9 of its 12 losses to teams below 1725 are by the queen rule. Against teams at 1725 or above it lost 9 of
  10 (two teams); below 1725 it loses no more often than 14585.
- **Reading.** The local pool rewards the economy at round 100, which this bot has, and has no opponent that keeps
  and feeds a queen. The ladder is decided between round 100 and the end by the queen's survival and her length.
  This is the lead's point of D-067 in concrete form: behaviour has to change with the phase of the game, and the
  phase that matters is the last 200 rounds.
- The matched comparison of P-hinata-06 (the reference re-weighted to the trial bot's opponents, series bootstrap)
  becomes a standing column of every trial look; Hinata computes it with the method as frozen.

### B. Consequences for building and measuring

- **Target for the next candidates:** the queen alive and long at the round limit: hidden early, fed from about
  round 250–300. Bokuto is building `bokuto-18` on this (no blind dives, no single-exit cells, no reliance on a
  rescue split, feeding from about round 280).
- **Asahi adds to every card:** our queen alive at rounds 100, 200, 300 and at the end; both queens' length at
  the end; results of games in which both queens are alive at the limit. And a second keeper panel, `qk2`: the 17
  maps × both seats against `bokuto-13-cull` and `kenma-28-harvest-reserve`, the two local bots whose queens survive.
- **Kageyama builds the curve table** from the ranked corpus: by round (every 25 rounds) units, total length,
  queen alive and queen length, for our submissions 14585, 17388 and 17530 and for their opponents, split by
  opponent rating (below 1725, 1725–1900, above 1900) and for the top ten among themselves. It is the lead's
  earlier proposal (summary curves, find where and when we fall behind), which the Chair had left open; it is
  ordered now as a data product because today's clearest diagnosis came from exactly this kind of reading. The
  cards' format is otherwise unchanged. The lead may strike this.
- **Sugawara:** the layer removal on `bokuto-13-cull` is read on the keeper panels, not the pool, for the reason in
  §A. The Chair asks the queen owner to support Bokuto's build with the feeding analysis (when the top teams
  start, how many feeders, where the queen sits), not to build a competing bot. Sugawara decides.

### C. The clone-prior line is paused now

- Five arms are in, all 6 to 14 points below the live prior. The sixth (A1 on the full rows at λ 1.76) is
  cancelled: its export has not arrived, and both forecasts put it below the bar (0.12 and 0.15). D-077 §E's
  pause takes effect with this record. Hinata is not filing the self-play value card.
- Kept for a later restart: the encoder with its C++ twin, the teacher rows, the slot bots, the trajectory block.
  Hinata's own lesson is recorded: to learn a decision from logs, randomise at the last gate before the action
  or log that gate's inputs.

### D. Ruling: map atlases in free-lane bots

- Sugawara flags that `bokuto-17-atlas` carries the terrain and bed classes of all 17 live maps and selects one by
  matching observed edges: map identity. carthage-05 and `bokuto-13-cull` already carry such an atlas for 10 maps.
- **Ruling.** The rule against map identity binds learned features and artifacts on the ladder of rungs. It does
  not bind free-lane bots: their prompt allows map-specific work at their own risk, and the measure is the contest
  ladder, which plays these maps. An atlas bot may be measured and may be put on trial.
- **Conditions for a trial of any atlas bot:** Asahi's `gen` panel (29 maps the atlas does not know) not below
  `bokuto-13-cull`'s on the same panel (paired 5th percentile above −5 points); the hidden-layout block not below
  `bokuto-13-cull`'s; and Sugawara's twin with the atlas switched off (`n_maps = 0`), so that the card shows how much
  of any gain is the atlas. Asahi builds the twin as a copy. Cards of atlas bots say that they are.
- Suggested to Bokuto, not ordered: carry Kageyama's hidden bed lists in the atlas and drop a layout at the
  first pearl that contradicts it; four of the five hidden layouts share their template's terrain.

### E. Other results and housekeeping

- `kenma-28-harvest-reserve` on our harness: 241–31, the same count as its parent; against `bokuto-13-cull` 0.00
  points [−1.10, +1.10]; probe passed. Kenma's layer adds nothing on top of Bokuto's bot. No trial.
- Kenma's tree has no uncommitted work; its branch `r/kenma` was local only and is pushed with this unit. Byte
  copies of `kenma-03`, `kenma-21` and `kenma-28` are on `r/asahi`.
- **Bokuto's fresh session works** (started by the lead; shell, commit 5ce986d95 on `r/bokuto`). The job route is
  one BOARD line to Asahi: `JOB <bot folder> : <pool | probe | gen | h2h vs <bot>>`, up to two an hour.
- **The paired live screen is not dispatched.** Daichi's draft: 360 games for a half-width of about 0.09, 720 for
  power 0.8 at a difference of 0.10, at about 20 games an hour, with a temporary activation for every game of an
  inactive arm. A ladder trial gives the same game rate without the switching, and the matched comparison of §A
  recovers most of the pairing. The draft is kept.
- Trial 2 at 45 ranked games (Daichi, 09:55Z; not the look): 21–24, −0.087 [−0.178, +0.020]. The end rule is
  applied at the look.

## D-081 — The end rule: `kenma-03-pocket-queen` becomes the incumbent; `bokuto-13-cull` plays at the old incumbent's level on the ladder (5 Oct 2026 11:23Z, Chair: Ushijima)

### A. Trial 2's table (Daichi, 10:56Z) and the rule

| Window (score minus expectation at rating 1725, series bootstrap) | Games | W–L | Statistic | Against the reference |
|---|---|---|---|---|
| 14585, last 120 ranked games before 02:13Z (reference) | 120 | | −0.043 [−0.109, +0.028] | |
| 17388 `kenma-03-pocket-queen` (trial 1) | 60 | 31–29 | +0.074 [−0.048, +0.197] | +0.117 [−0.022, +0.260] |
| 17530 `bokuto-13-cull` (trial 2) | 60 | 30–30 | −0.041 [−0.132, +0.062] | +0.001 [−0.110, +0.126] |

- The rule (D-075 §C, D-077 §B, D-078 §C): a trial bot must exceed the reference by more than 0.03. 17530 does
  not (+0.001). 17388 does (+0.117). Between the trial bots the windows differ by 0.115, more than 0.10, so the
  live windows decide and not the pool. Both readings give the same answer; no fault in either window.
- **`kenma-03-pocket-queen` (submission 17388) is the incumbent.** Daichi activates it through the restore control
  (previous 17530, candidate 17388), outside the blackout. It stays live. D-052 §B applies with 14585 as the
  rollback target; its trial window counts as its first 60 games.
- **What this choice rests on, stated plainly.** An interval that includes zero; a window that drew no Schooltime
  game, the one map its pocket logic acts on; different opponents in the two windows; and a bot whose lane is
  retired, so nobody develops it. It is the best estimate the rule allows, not an established gain. Its further
  games as incumbent will narrow the estimate, and the next trial candidate is measured against it.
- **Chair's forecasts for trial 2, scored:** point +0.10 (outcome −0.041); exceeds the reference by more than 0.03:
  0.75 (outcome 0, Brier 0.5625); highest of the three: 0.60 (outcome 0, Brier 0.36). The Chair has been too
  optimistic about every candidate today.

### B. What the two trials say together

- **`bokuto-13-cull`: +5.5 points on the pool, +0.001 on the ladder.** It plays at the old incumbent's level. By
  opponent rating at game time: below 1725 −0.019 [−0.163, +0.139] (35 games), at or above 1725 −0.073
  [−0.148, −0.003] (25 games, 7 wins). Lost by the queen rule: 14 of its 30 losses. Hinata's matched column agrees:
  level with 14585 below 1725, behind it above (+0.167 [0.000, +0.362], 15 games).
- **`kenma-03-pocket-queen`: −2.2 points on the pool, +0.117 on the ladder.** At or above 1725: +0.162
  [0.000, +0.324] (35 games); below: −0.048. Lost by the queen rule: 7 of 29 losses. Matched against 14585 on
  shared opponents its loss rate is 0.165 lower [0.007, 0.351] (55 games, P-hinata-06).
- **So the two local measures ranked these two bots in the wrong order.** The pool put Bokuto's bot 21 wins ahead;
  head to head Kenma's later bot lost to it 34–68. Two trials are a small sample, but with k = 16 that is three
  ladder results in a row that the local numbers did not predict. Until a local measure does predict the ladder,
  the ladder trial is the test, and it is cheap: three hours, nothing lost in rating.
- **A hypothesis, not a finding.** What `kenma-03-pocket-queen` adds to carthage-05 outside Schooltime is one thing:
  every non-queen plans with one unit slot kept free, all game. A free slot is what an escape split needs. If the
  queen and the others survive attacks by stronger teams because a split is always available, that would explain
  fewer queen-rule losses and the result against the 1725-and-above band, and it costs economy against weak
  opponents, which is what the pool sees. **Ordered:** Sugawara checks it in the replays of 17388, 17530 and 14585
  (splits made at the unit cap minus one, queen deaths by cause, units at rounds 100 to 400). Asahi builds
  `asahi-27-b13-reserve`: `bokuto-13-cull` with Kenma's global reserve lines and nothing else, for the pool, `qk2`
  and a probe. If the replays support the hypothesis, that bot is a trial candidate.

### C. Local results of this hour

- **`bokuto-17-atlas` is below its parent, and the atlas is the cause.** Pool 228–44; against `bokuto-13-cull` −4.78
  points [−8.46, −1.08]. The twin with the atlas off: 240–32; atlas on minus off −4.41 [−8.46, −0.35]; on the 29
  unknown maps exactly zero. The 17-map atlas costs 4.4 points on the maps where it is exact. Not a trial
  candidate; Bokuto is told. Sugawara's forecast that the atlas gains at least 2 points: 0.55 (outcome 0, Brier
  0.3025).
- **The keeper panel `qk2` shows what the pool cannot** (68 fixtures against `bokuto-13-cull` and
  `kenma-28-harvest-reserve`): carthage-05 21–47 with 0–27 decided by the queen rule; `bokuto-17-atlas` 28–40, and
  6–8 in games where both queens live. On the pool the opponents' queens are almost never alive at the end, so the
  length race is not tested there at all.
- **Queen by round on the pool:** carthage-05's queen is alive in 150 of 265 games at round 100 and 0 of 146 at
  the end; `bokuto-13-cull`'s in 240 of 268 and 94 of 163, with a median length of 3 at the end.
- **Sugawara's census of the top ten** (210 team-games against opponents at 1650 or above): our queen's extra
  deaths are at walls (0.25 a game against 0.03), not in fights (0.42 both). Top queens are alive at rounds 100,
  300 and 400 in 85, 65 and 57 % of games; ours in 74, 46 and 35 %. Feeding starts about round 300 in the top
  quartile; the median top queen is still 3 long at round 400. For `bokuto-18`: first no wall deaths of the queen,
  then feeding from round 280–300.

### D. Trials and lanes from here

- **Qualification for a trial is unchanged** (a passing probe and a pool not below carthage-05, D-076 §A), and
  every candidate's card also carries `qk2` and a 102-game head-to-head against the incumbent, as information.
- **Queue:** `bokuto-18` when Bokuto posts it; `asahi-27-b13-reserve` if §B's check supports it. The incumbent holds
  the slot between trials.
- **The curve table moves to Hinata** (who has the method and the rows); Sugawara's census and Asahi's columns
  already supply the queen part. **Kageyama has not posted since about 07:00Z**; its remaining jobs are cancelled
  or reassigned, and the Chair recommends to the lead that the lane be stood down.
- Hinata's lane continues as a service: the matched column at every look, and the curve table.

## D-082 — The curve table: the top teams win on mid-game growth; the reserve hypothesis is refuted; the incumbent is not yet activated (5 Oct 2026 12:27Z, Chair: Ushijima)

### A. The curve table (Hinata, P-hinata-07, card filed before computing)

1,171 ranked games decoded: 14585's last 300, 17388's 80, 17530's 90, and 701 games of the top ten among
themselves.

| Total length (cells) | Round 100 | Round 300 | Growth 100→300 |
|---|---|---|---|
| Top ten, winner | 78.5 | 153.7 | +75 |
| Top ten, loser | 61.3 | 110.9 | +50 |
| 14585 (old incumbent) | 62.7 | 128.1 | +65 |
| 17388 `kenma-03-pocket-queen` | 59.9 | 115.8 | +56 |
| 17530 `bokuto-13-cull` | 55.1 | 103.2 | +48 |

- **Among the top ten the winner is the side with the bigger economy.** The difference in total length is +17.3
  [14.4, 19.8] at round 100 and +42.8 [36.1, 50.0] at round 300; the side ahead at round 300 wins 73 % of games.
- **Queen survival does not separate winners from losers there:** alive at round 300 in 46 % and 47 %; at the end
  28 % and 32 %.
- **Our economy is at the level of the top ten's losers**, and `bokuto-13-cull` has the smallest of our three.
- **We lose leads through the queen rule.** Of the games it led on total length at round 300, 14585 won 50 %
  (48 of its 66 lost leads by the queen rule); 17530 won 65 % (11 of 15 lost leads by the queen rule); 17388 won 74 %,
  the top ten's rate. Against our own opponents our queens are alive about as often as theirs.
- **This corrects D-080 §A.** That record said the ladder is decided by the queen's survival and length. The curve
  table says there are two separate deficits: (1) growth between rounds 100 and 300, where the top teams add 75
  cells and we add 48 to 65; (2) the conversion of a lead, which the queen rule takes from us. `bokuto-13-cull`
  improved the second and paid in the first. Caveats: the curves are conditioned on games still running; few
  games against teams above 1900; opponent sets differ.
- This is the reading the lead proposed (curves by round: where and when do we fall behind). It took one unit
  and changed the diagnosis. **It becomes a block of every trial look:** total length at rounds 100 and 300
  against the top ten's winner and loser curves, and the share of round-300 leads converted. Hinata computes it.

### B. The reserve hypothesis is refuted (Sugawara, 240 replays)

- `bokuto-13-cull` already keeps one unit slot for the queen; both trial bots are at the unit cap in 0.0 % of
  snapshots between rounds 100 and 400 (14585: 24.6 %). The queen is too short to split when she dies (length 4 or
  more at death in 4 of 58 and 3 of 43 cases).
- `kenma-03-pocket-queen`'s queen survives worse than `bokuto-13-cull`'s (alive at the end 2 of 60 against 17 of 60).
  Its advantage against teams at 1725 or above is in games where both queens are dead and the longest dragon
  decides: 10–5, against 2–6 for `bokuto-13-cull` and 12–4 for 14585. That is the economy of §A again.
- The Chair's hypothesis of D-081 §B was wrong. `asahi-27-b13-reserve` is a measurement only and not a trial
  candidate.

### C. Targets for builders, and for the cards

- **Two targets, both measured in the look:** total length near the top ten's winner curve (about 78 at round 100
  and 154 at round 300), and at least 70 % of round-300 leads converted. A candidate that gains one by giving up
  the other has not gained.
- For Bokuto (`bokuto-18` and after): keep the queen changes that convert leads (no wall deaths, feeding from
  round 280–300), and recover the growth between rounds 100 and 300 that `bokuto-13-cull` gave up; the layers that
  cost economy are the ones to find. Sugawara's layer removal on `bokuto-13-cull` is now read for this: which layer
  costs total length at round 300.
- Asahi adds total length at rounds 100 and 300 (ours and the opponent's) to every card, on the pool, `qk2` and the
  head-to-head against the incumbent.

### D. The incumbent is not yet active

- At 12:25Z the hub still shows 17530 active. Daichi has not posted since 10:56Z; its 11:50Z unit did not act on
  D-081. The Chair does not touch the server controls. Daichi is asked again; if nothing is posted by 13:20Z the
  lead is asked to look at Daichi's scheduled task.
- Nothing is lost meanwhile: 17530 keeps its own rating and its window grows.

### E. Lanes

- Hinata delivered two descriptions today (P-hinata-06, P-hinata-07) that changed the diagnosis, each within one
  unit and with its method fixed before reading. The lane continues as the analysis service of the trials. The
  Chair withdraws its earlier doubt about the lane's use.
- Kageyama: still silent; the recommendation to stand the lane down is unchanged.
- No trial candidate is ready. `bokuto-18` is not posted yet.

## D-083 — Correction of D-082: the queen does separate winners from losers; the incumbent is active; trial 3 is ordered (5 Oct 2026 13:23Z, Chair: Ushijima)

### A. Correction of D-082 §A (Sugawara's review, 12:35Z; Hinata's fix, 12:41Z)

- The curve table read the queen as dragon 0 for one side and dragon 1 for the other. Which side owns which
  follows the map, and the reading was swapped in 593 of 1,171 games. Hinata fixed it at the source; the corrected
  end state agrees with the engine's own queen field in 2,342 of 2,342 team-games (before: 1,894).
- **Two statements of D-082 §A are withdrawn:** that queen survival does not separate the top ten's winners from
  their losers, and that our queens are alive about as often as our opponents'. Corrected:

| Queen alive at round 300 | Side | Opponent |
|---|---|---|
| Top ten, winner against loser | 0.58 | 0.37 |
| 14585 (old incumbent) | 0.06 | 0.45 |
| 17388 `kenma-03-pocket-queen` (incumbent) | 0.12 | 0.47 |
| 17530 `bokuto-13-cull` | 0.50 | 0.57 |

- Top ten at the end: winner's queen alive 0.48 against 0.13, length 8.8 against 1.7.
- **Unchanged:** the total-length curves, the economy gap (winners 78 and 154 at rounds 100 and 300; ours 55–63
  and 103–128), and the conversion of round-300 leads (50, 74 and 65 %).
- **The picture now:** the top ten's winners have both the economy and the queen. The incumbent has the economy of
  the old bot and our worst queen; `bokuto-13-cull` has our best queen and our smallest economy. No bot of ours has
  both. D-080 §A's queen diagnosis stands beside D-082's economy diagnosis.
- **Three targets for a candidate:** total length near 78 and 154 at rounds 100 and 300; queen alive at round 300
  near 0.58; at least 70 % of round-300 leads converted.
- **The Chair's error of process.** D-082 recorded a one-hour-old result from one lane as a correction and
  reported it to the lead. From now on a description that changes the diagnosis is checked by a second lane
  before the Chair records it: Sugawara reviews Hinata's, and the reverse. Sugawara's review came within the hour
  unasked, and Hinata's fix and guard within six minutes of it.

### B. The incumbent is active

- Daichi activated 17388 at 12:34:13Z; its first ranked series started 12:36Z. The delay was the blackout around
  11:52Z. The restore control takes the submission to activate as `previous` and the active one as `candidate`;
  the Chair's wording in D-081 and D-082 had the two reversed and Daichi corrected it.
- 17388 since reactivation: 20 games, 10–10 (too few to read). With its trial window: 80 games.
- **17530 (`bokuto-13-cull`), all 120 ranked games: −0.054 [−0.128, +0.023]** at rating 1725; the second 60 went
  30–30 like the first. It is at the old incumbent's level (−0.043), firmly.

### C. Local results (Asahi, 12:39Z and 12:42Z)

- **`asahi-27-b13-reserve`** (`bokuto-13-cull` plus Kenma's reserve lines): pool 237–35, −1.47 points against its
  parent; head to head against the incumbent 69–33 (its parent 64–38; paired +4.90 [+0.98, +9.80]); `qk2` 33–35
  (carthage-05 21–47, the incumbent 25–43); probe passed. **On the pool the reserve restores the economy the parent
  gave up:** total length at round 300 138.5 against 127.5 (carthage-05 136.4), with the parent's queen survival
  kept. The Chair's hypothesis had the wrong mechanism (survival); the lines are worth having for another reason.
- **A fourth disagreement between local and ladder:** locally `bokuto-13-cull` beats the incumbent 64–38, with 33
  wins and no loss by the queen rule; the ladder preferred the incumbent. The incumbent never keeps its queen, so
  a head-to-head against it rewards queen keeping more than the ladder's field does.
- **The pool cannot see the economy race:** its opponents hold 41 and 81 cells at rounds 100 and 300 (the top
  ten's losers: 61 and 111), so every bot leads at round 300 and converts about 90 %. On `qk2` and the head-to-head
  the opponents are at our level and conversion separates the bots (41 % carthage-05, 54 % the incumbent, 61 %
  `asahi-27-b13-reserve`).

### D. Trial 3, ordered now with its condition

- **`bokuto-18-queenfeed`** (Bokuto, 13:00Z): the atlas-off twin of 17, the queen fed from round 290, queen terrain
  safety from round 0, and the reserve lines. It is the first candidate built on today's diagnosis and addresses
  all three targets.
- **Order.** As soon as Asahi posts a passing deploy probe and a pool not below carthage-05 (paired 5th percentile
  above −5 points) for `bokuto-18-queenfeed`, Daichi registers it from a byte copy and runs trial 3 without a
  further record. If it fails either condition, trial 3 is `asahi-27-b13-reserve`, which has passed both.
- **Look:** the first series boundary at or after 60 ranked games; the table of D-081 (statistic at rating 1725,
  opponent bands, Schooltime apart, end reason by band, queen columns, faults); Hinata's matched column and curve
  block with the corrected code (total length at rounds 100 and 300, queen alive at round 300, leads converted),
  reviewed by Sugawara before the Chair reads it.
- **End rule:** the trial bot becomes the incumbent if its statistic exceeds the incumbent's by more than 0.03,
  the incumbent's being taken over all its ranked games since 05:02Z; otherwise Daichi restores 17388. A fault
  ends the trial at once.

### E. Where we stand, for the lead

- On the ladder nothing we have is separable from the old incumbent: 14585 −0.043, `bokuto-13-cull` −0.054 over
  120 games, the incumbent about +0.04 over 80. The top ten are more than 400 rating points above. Today's work moved
  the understanding (three measured targets and panels that show them), not yet the rating.
