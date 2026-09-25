# Shared game statistics

`game_stats.parquet` at the repository root contains one row per completed game.
The comparison runner updates it after saving each result, including games with
replay-analysis errors. Harness errors are excluded; engine outcomes with bot
runtime faults are included and flagged. It is a result ledger, not an aggregate
counter: filter by map, side, bot version or runtime before calculating W/L/D.

## Sharing through Git

```text
game_stats/runs/<run UUID>.parquet  # Commit these contributions.
game_stats.parquet                 # Generated union; git-ignored.
game_stats/.write.lock             # Local process lock; git-ignored.
```

Each new experiment gets a UUID. Independent experiments add different files,
so team members normally merge additions rather than edit one binary file.
Replays and frozen sources remain in the ignored `experiment_data/` directory;
the small contribution files are sufficient to share outcomes and fingerprints.

Commit your new/updated files under `game_stats/runs/` along with your bot changes.
After pulling or merging your teammates' contributions, rebuild the central file:

```sh
uv run tools/game_stats.py rebuild
uv run tools/game_stats.py summary --output /tmp/bot-pairs.csv
```

`uv` installs the declared PyArrow and filelock dependencies. Summary rows contain
wins, losses and draws from each bot's perspective, separated by source hash,
opponent source hash, runtime mode and toolkit version. Every game contributes
to **two** perspective rows, so summing all summary rows counts each game twice.

To combine exported central Parquets or contribution files:

```sh
uv run tools/game_stats.py merge /path/to/teammate.parquet /path/to/another.parquet
```

The command merges into the local contribution store and rebuilds the central
file. It is safe to import overlapping files repeatedly. A contradictory copy of
the same game fails before any ledger file is changed; it is never silently
overwritten. Unsupported schemas also fail explicitly.

If both branches resumed the **same experiment**, its contribution file may have
a Git conflict. Save both stages outside the contribution directory, remove the
conflicted working copy, then union the preserved copies and stage the result:

```sh
git show :2:game_stats/runs/<uuid>.parquet > /tmp/ours.parquet
git show :3:game_stats/runs/<uuid>.parquet > /tmp/theirs.parquet
rm game_stats/runs/<uuid>.parquet
uv run tools/game_stats.py merge /tmp/ours.parquet /tmp/theirs.parquet
git add game_stats/runs/<uuid>.parquet
```

If this detects conflicting outcomes, inspect the original experiment records
before correcting the data. Keep both saved copies until resolution succeeds.
Do not resolve by choosing one entire file: that can discard different games.

## Identity and schema (version 1)

- `run_id` is a persisted UUID; `game_key` identifies a logical game within it.
  Comparisons use `(opponent, map, candidate side)`. `game_id` hashes those two
  fields. Resume and re-import reuse it, preventing duplicate counts.
- An intentional new experiment receives a new UUID and counts again, even on
  identical inputs. Such repeated deterministic fixtures are not independent
  statistical evidence. `fixture_id` groups identical ordered bot hashes, map
  hash, runtime mode, toolkit version and seed for analyses that want to collapse
  repeats. A missing seed means the runner did not specify one.
- `bot_a`, `bot_b`, their source SHA-256 fingerprints, `map`, its SHA-256,
  `mode`, `runner_version` and `seed` preserve game context. A bot fingerprint
  hashes the sorted relative-path/file-hash dictionary of its frozen source;
  it is not a hash of the compiled binary. Toolkit version is the CLI-reported
  version, not a complete machine/environment fingerprint.
- `outcome` is `A`, `B` or `draw`. `a_wins`, `a_losses`, `b_wins`, `b_losses` and
  `draws` are consistent 0/1 columns. `rounds` and `runtime_faults` may be null
  when unavailable. `source` identifies the producer and `run_started_at` is UTC.
- Files carry `game_stats_schema_version=1` metadata. Future changes need an
  explicit migration rather than silently combining incompatible columns.

Do not rename a contribution independently of its `run_id`. Do not edit or
commit the generated central file: rebuilding uses only the contributions.
Source changes under the same bot directory name remain distinct in summaries.

## Existing and future runners

Import an older comparison without rerunning its games:

```sh
uv run tools/game_stats.py import experiment_data/<run-directory>
```

Old manifests receive a deterministic UUID based on their saved inputs and start
time, so copied experiment directories deduplicate too. Other historical runner
formats need their own adapter; they are not automatically ingested.

New runners can import `make_record` and `publish_games` from `tools/game_stats.py`.
Persist one UUID per run, allocate a stable key per scheduled game (including
repetition/seed where applicable), and supply both source fingerprints, map hash,
runtime and result to `make_record`. Save the original result first, then call
`publish_games(records)`; retries with the same records are harmless. Batch large
imports to avoid rebuilding the whole ledger per row.

All writers share a process lock. Individual Parquet replacements are atomic;
contributions are written before the central union. After a crash, `rebuild`
recovers committed contributions, and runner resume imports saved results not
yet published. A publication failure stops the comparison with its results
preserved. Do not concurrently resume the same experiment directory; independent
experiments can safely publish to the same ledger.
