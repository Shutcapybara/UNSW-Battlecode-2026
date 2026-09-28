# Hub operations

## Install / update (on the Mac)

    cd /Users/alik/Documents/Projects/UNSW-Battlecode-2026
    bash tools/hub/bootstrap_mac.sh

Runs the tests, initialises `HUB` (`hub.toml` with every knob), backs up the legacy record (without replays), deploys a
frozen copy of `tools/hub/` to `HUB/app/<sha>/hub` (the LaunchAgent runs the copy, so editing the working tree never
changes the running daemon), installs `~/Library/LaunchAgents/au.battlecode.jks-hub.plist`, runs one cycle with a
packet, and kickstarts the legacy worker if it has exited without a stop request. Re-run after every change to
`tools/hub/`.

## Daily commands

    .venv/bin/python -m tools.hub.hubctl status            # incumbent, worker health, quota, experiments, queue
    .venv/bin/python -m tools.hub.hubctl packet            # the latest two-hour review packet
    .venv/bin/python -m tools.hub.hubctl cycle --packet    # force a cycle and a packet now
    .venv/bin/python -m tools.hub.hubctl doctor            # paths, toolkit version, launchd state
    tail -f "$HUB/logs/actuator.log"

Stop / resume the hub daemon: `touch "$HUB/control/stop"` (graceful) then `launchctl bootout gui/$(id -u)/au.battlecode.jks-hub`;
`launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/au.battlecode.jks-hub.plist` to resume.

## The legacy worker (still the live executor)

Files under `LIVE/state/` are its control surface: `runner.stop` (drain and exit; remove it and `launchctl kickstart
gui/$(id -u)/au.battlecode.jks-live-validation` to resume), `runner.renew` (build a fresh two-hour plan),
`runner_attention.json` (present ⇒ `needs_review`, no new requests; archive it into `runner_logs/` to clear, as
`runner.py --clear-review` does). The hub's 60 s loop kickstarts the worker when `runner_status.json` goes stale for
more than `legacy.stale_seconds` (300) and no stop file exists (`legacy.keepalive` in `hub.toml`).

D-003 patch (28 Sep 2026, backup `LIVE/state/controller.py.orig-*`): on an external incumbent change the controller
adopts it, freezes running comparisons, re-parents registry entries with `control_policy = "current"` to the new
control, touches `runner.renew` and exits 0; at end of cycle an active/expected mismatch with no open transaction is
adopted on the next cycle instead of raising. Everything else in the legacy system is unchanged.

## Retention

Hub: `tick/` 30 days, `notify/` 30 days, `hub.sqlite` vacuum weekly after a backup (`HUB/backups/`). The legacy
`state/` keeps raw and decoded replays for every game (≈ 1.3 GB for 350 games); replay retention is a cutover item.

## Rollback

`touch "$HUB/control/stop"`, `launchctl bootout gui/$(id -u)/au.battlecode.jks-hub`. The legacy worker is untouched by
the hub (the hub never writes under `LIVE/` except through `hubctl candidate stage-live`, which appends a registry row
and touches `runner.renew`). To revert D-003, copy `LIVE/state/controller.py.orig-<stamp>` back over
`LIVE/system/controller.py`.

## Repository hygiene (decision D-007): `tools/hub/gitkeeper.py`

The hub actuator runs a git pass ten minutes after start and then every `git.interval_seconds` (3 h); `hubctl git
status` shows the plan, `hubctl git sync [--dry-run]` runs it now. Policy, all in `hub.toml [git]`:

- Commit only paths matching `include` (`bots/*`, `docs/*`, `game_stats/runs/*.parquet`, `game_stats/imports/*.json`,
  `tools/*`, `tests/*`, `maps/*.map`, the root TOML/README/.gitignore) that have been **quiet for `quiet_minutes`**
  (60), and never anything on the `never` list (the API key, `experiment_data/`, `build/`, `public_replays/`,
  `hub-state/`, replays, archives, locks, logs).
- A new bot directory is committed whole once it has `bot.toml` and every `.py` parses; a modified `.py` that does
  not parse is skipped and reported. Deletions are never automated. Nothing is ever staged wholesale.
- After committing, fetch and merge `origin/main` with an ordinary merge; on conflict abort and raise attention (a
  director merges by hand). Push only when the merge is clean. Never rebase, never force.
- Commit messages start with `[hub-git]` and list the paths; every pass writes `HUB/git/<epoch>.json` and one line
  in the review packet (§1).

Agents working from the Cowork VM must not run index-writing git commands over the mount (they leave a stale
`.git/index.lock` that they cannot delete); use `git --no-optional-locks status|log|diff` there and let the keeper
commit.

## Failure triage (decision D-009): the legacy worker no longer dies on surprises

`LIVE/system/controller.py` (backups `LIVE/state/controller.py.orig-*-D009`): read-only API calls retry bounded
transport failures (mutations never retry blindly); a fetch or parse failure for one game is recorded as an
unverified row with `harvest error: …` and retried next cycle (twenty tries, then left alone), never raised; the
status report tolerates rows without full identity; a cycle failure of a transient class (transport, 5xx, missing or
malformed fields) with **no open upload/switch/intent transaction** exits with code 3 instead of 1.

`LIVE/system/runner.py` (loaded on restart; `runner_status.json` shows `runner_revision: D-009` when live): exit code
3 backs off five minutes and retries; three transient failures in a row raise attention as before; any other failure
class, or a failure with an open transaction, stops new requests immediately as before. `state/runner.restart` makes
the worker exit non-zero between jobs so launchd relaunches it with new code (`hubctl legacy restart`).

The hub daemon's 60 s loop (`tools/hub/legacy_ops.py`): honours `runner.restart` with `launchctl kickstart -k` when
the worker is idle; auto-clears a `needs_review` whose reason is transient-class and whose state has no open
transaction, at most `legacy.auto_clear_per_hour` (3) times per rolling hour, then notifies and stops clearing; any
non-transient reason is notified and left for the director (`hubctl legacy status`, `hubctl legacy clear-review
--note …`). Every action is appended to `HUB/legacy_ops.jsonl`.

Bootstrap restarts the worker once when it is idle and still running a pre-D-009 runner.
