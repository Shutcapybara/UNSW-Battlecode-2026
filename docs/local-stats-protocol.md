# Local Statistics Protocol

This is the authoritative, agent-first protocol for experiment statistics.

## Rules

- Every intentional experiment gets a new unique `run_id`.
- While running, write only to `game_stats/local/runs/<run_id>/`.
- Append events to that run's `events.jsonl`; never update shared aggregates.
- Use stable event identities so retries are deduplicable.
- Preserve errors, diagnostics, replay analysis, and bot-specific telemetry.
- Never reuse, rename, move, or delete another run's directory.
- Never repair source queues by editing an aggregate.
- On conflicts, stop and report the run ID, event type, and event key.

## Layout

~~~text
game_stats/local/
  runs/<run-id>/
    manifest.json
    events.jsonl
    raw/
  ledger.sqlite3          # generated only
~~~

Run queues are authoritative. SQLite, Parquet, CSV, standings, and reports are
derived outputs and may be rebuilt.

## Event format

Each line is a JSON object containing `event_id`, `run_id`, `event_type`,
`event_key`, `created_at`, and a free-form `payload`. Match payloads should
include bots, map, mode, outcome, winner, rounds, runtime faults, seed, errors,
and analysis errors. Use `match_error` for a failed attempt that may later be
retried as `match_completed`.

## Aggregation

After runs finish:

~~~sh
python3 tools/stats_store.py rebuild
python3 tools/stats_dashboard.py
~~~

Rebuild reads every queue, deduplicates exact retries, rejects contradictions,
and recreates the local ledger. A failed rebuild must not cause source files to
be moved private or deleted.

## Agent handoff

Report the `run_id` and queue path. Leave partial runs in place. Do not claim an
aggregate is authoritative without naming the source runs used to build it.
