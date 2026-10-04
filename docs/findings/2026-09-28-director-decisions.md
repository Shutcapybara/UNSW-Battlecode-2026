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
