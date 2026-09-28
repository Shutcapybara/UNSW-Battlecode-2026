# The hub executor (protocol v2): design, failure matrix, cutover

Director decision D-012, 28 September 2026 (user approval granted for major changes to the runner and A/B suite).
Code: `tools/hub/executor.py` (cycle), `api.py` (client), `preflight.py` (metered probes + contracts),
`actuator.py` (daemon: lease, shadow/live guard, 60 s safety loop, 600 s cycles), `cutover_mac.sh`, `rollback_mac.sh`.
Tests: `tests/test_hub_executor.py` (a fake server that replays today's incidents), 33 hub tests in all.

## Principles

1. **One reconciling cycle, no state to lose.** Every cycle reads the server (active submission, submissions, maps,
   team, ladder, the 200 most recent series) and the hub ledger, and decides from scratch. Nothing is cached in
   memory between cycles; code changes take effect on the next cycle; a crash costs one cycle.
2. **Every mutation is a durable intent with an identity.** Activate, battle, upload and promotion are written to
   `intents` before the POST. 4xx resolves the intent as rejected; 5xx or transport leaves it *open* and stops
   dispatch for the cycle. The next cycle reconciles first: a battle intent is matched against the server's own
   history by requester, time window, opponent, submission, game count and map (attach the ids; release after ten
   minutes if nothing matches; stop only if two series match); an activation by the observed active submission; an
   upload by its exact name. Nothing is ever re-posted while an intent is open.
3. **Unknown is unknown.** Missing fields in a payload make a row unverified with the requested submission attached;
   it is re-fetched (twenty tries) and never counted as a loss. The status report and the pairing tolerate partial rows.
4. **The control is whatever the team has live.** An external activation is recorded, running comparisons are
   frozen (a confirmation with ≥ 6 complete blocks is still evaluated for futility), the control moves, and the
   candidates are re-queued against the new control in the same cycle. Our own temporary activation is restored only
   when it is still what is active; a teammate's choice made in the meantime is preserved.
5. **Stop only for humans.** Dispatch stops for: an ambiguous intent older than six hours, an upload name matching
   two submissions or none after six hours, an archive that does not match its frozen files, a promotion whose
   acknowledgement was lost. Everything else logs, backs off and continues; harvest never stops.
6. **Exact pairs, honest completion.** Blocks pair on (map, side, opponent submission, starting layout). A block
   that lost an arm gets the missing arm requested; a block with unpaired maps gets fills (alternating arms, at most
   six); after six fills a block with ≥ 8 exact pairs is complete on the pairs it has, fewer is excluded. Both arms
   of a new block are requested in one cycle or not at all.
7. **Ranked exposure guard.** No temporary activation from 8 minutes before to 12 minutes after each even UTC hour.
8. **Quota from the server's own record** (every member's requests in the rolling hour) plus reservations; a 429
   blocks the pool for the server's stated wait; an executor cap leaves headroom for teammates.
9. **Protocol v2** (`docs/hub/PROTOCOL_V2.md`): three-block screen with futility stops, twelve-block confirmation with
   futility-only interims at 6 and 9, efficacy once at 12 (mean paired delta ≥ +0.03, one-sided sign-randomization
   p ≤ 0.025, no map below −0.25, twelve distinct opponents, zero candidate faults); promotion activates the
   candidate and opens probation (automatic rollback on any runtime fault); one confirmation per (candidate, control).

## Failure matrix (each of today's incidents → what v2 does)

| Incident (28 Sep) | Legacy behaviour | Executor v2 |
|---|---|---|
| Teammate activates another bot (×5) | controller raises, worker `needs_review`, queue orphaned | recorded as external action, comparisons frozen, candidates re-queued against the new control in the same cycle |
| API payload without submission ids (474236) | `KeyError`, loop dead 25 min | unverified row with the requested submission; re-fetched; block waits for fill |
| `None` in a status sort | loop dead | tolerant views; no in-memory report path can stop dispatch |
| `POST /battles` answered 502 (10:23) | intent parked 84 min for a human | identity reconciliation next cycle: ids attached or reservation released; never re-posted |
| Codex leaves `runner.stop`; worker exits | loop dead until a human kickstarts | one daemon, launchd `KeepAlive`, executor lease; no control files |
| Opposite starting layouts in every game of a block | fills (unbounded cost) or exclusion | fills alternating arms, ≤ 6; then ≥ 8 pairs counts, fewer excludes |
| Teammates use the shared 60 games; 429 | pool blocked 1 h blindly | server's stated wait honoured; executor cap below the allowance |
| Runner needs a restart to load code | manual kickstart | cycle-scoped code; the daemon is the only long-lived process and is supervised |
| 7 MB `state.json` rewritten on every event | growing rewrite cost | SQLite (WAL) rows, one file per replay |
| Confirmation α = 0.05/((n+1)(n+2)) unattainable | no promotion possible | fixed α = 0.025 with declared futility interims |
| Confirmation frozen after 6+ blocks by a switch | evidence discarded | futility evaluated on the blocks it has; otherwise `superseded_incomplete` with the partial estimate recorded |
| One unverified game excludes a whole screen block | block replaced (20 games) | the game is a missing pair: fill or drop, never exclude for one row |

## Cutover

**Default (`executor.mode = "auto"`): one command, no waiting.** `bash tools/hub/bootstrap_mac.sh` deploys the daemon,
which starts in shadow; after `auto_cutover_after` (3) consecutive clean shadow cycles it performs the cutover itself:
it writes the legacy worker's `runner.stop`, waits until that worker has no job and no open upload/switch/intent
(a drain longer than `drain_timeout_seconds` pages once and keeps waiting — nothing is forced), unloads the legacy
LaunchAgent (plist backed up under `HUB/backups`), adopts the legacy record (`adopt-legacy`), records `cutover` in the
ledger and flips to live in-process. Every step is an event; the notification channel gets "auto-cutover started" and
"executor is LIVE". On a daemon restart, `auto` + a recorded cutover + no live legacy worker = live immediately.

**Later code changes never need the terminal.** The director commits files into the checkout and runs
`python3 tools/hub/request_redeploy.py --note "…"` (from any session that mounts the repository); the daemon verifies
the listed files' sha256 against its own view of the checkout (a stale or partial write is refused), runs the gate
tests (`test_hub_core`, `_git`, `_legacy_ops`, `_executor`, `_daemon`), snapshots `tools/hub` (including `vendor/`)
into `HUB/app/<sha>`, relinks `current`, writes `hub-state/control/redeploy.done.json` (or `.rejected.json` with the
reason) and exits non-zero so launchd relaunches it on the new code. A redeploy is deferred while an intent or
transaction is open (rejected after 30 minutes of that).

The manual sequence below remains for `mode = "live"` and for operators who prefer to watch each step.

### Manual steps (Mac; each step checks the previous)

1. `bash tools/hub/bootstrap_mac.sh` — deploys this code; the daemon starts in **shadow** mode: it reads the API
   read-only every ten minutes, computes the plan it would execute, and logs it (`hubctl executor status`). The legacy
   worker keeps dispatching. `executor_shadow_clean` counts consecutive clean cycles. A shadow cycle writes no
   experiment, block, decision or verdict row (it only observes the control and harvests); and the executor never
   evaluates, freezes or extends a `protocol='v1'` experiment in any mode — legacy rows are evidence, frozen once by
   `adopt-legacy` (tested: `test_shadow_writes_no_experiment_state`, `test_legacy_v1_experiment_is_never_evaluated_or_frozen`).
2. After ≥ 3 clean shadow cycles (≈ 30 min): `bash tools/hub/cutover_mac.sh` — stops the legacy worker gracefully
   (waits for its jobs and for no open upload/switch/intent), unloads its LaunchAgent (plist kept), adopts the legacy
   record (v1 experiments frozen `superseded_by_cutover`; legacy candidates that were rejected are retired; legacy
   candidates the director did not re-queue are retired `legacy_not_requeued`; control-following ones stay), sets
   `executor.mode = "live"` and restarts the daemon. The daemon refuses live mode while the legacy worker is alive.
   Adoption also sets `legacy_adopted`, after which the observer stops re-importing `LIVE/state` (otherwise each
   cycle would overwrite the executor's candidate and experiment statuses with the frozen legacy ones); `hubctl
   executor release-legacy` (run by `rollback_mac.sh`) resumes the import. The legacy worker's open screen is not
   continued: its games stay in the record for analysis, and the candidate is re-screened from scratch under v2.
3. Watch `hubctl executor status` and the packet for the first two live cycles (restoration matched, no open intents).
4. Rollback at any time: `bash tools/hub/rollback_mac.sh` (refuses while an intent or transaction is open).

## What stays the same

The evidence rules (exact pairs, sign-randomization, dev games never promote, screens never promote), the legacy
decoder (vendored byte-identical), the retained legacy record (imported, protocol v1, verbatim), the `-ai` naming,
the standing authorizations, and the credential path.
