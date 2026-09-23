# Bot Workflow

## Small Tournament

```sh
PATH="$PWD/.venv/bin:$PATH" python3 bots/tournament.py \
  --focus-bot <most-recent-bot> \
  --bots <third-most-recent-bot> <second-most-recent-bot> <most-recent-bot> \
  --jobs 8 \
  --no-replays \
  --output build/<most-recent-bot>-small
```

For rapid development, run two tournaments using the three most recent
versions as the shared pool. First focus the most recent version, then focus
the second most recent version. This tests both candidates against each other
and the third-most-recent version on every map and with both side assignments.
Use a fresh output directory for each run. For example, with hunter-v02,
hunter-v03, and hunter-v04:

```sh
PATH="$PWD/.venv/bin:$PATH" python3 bots/tournament.py \
  --focus-bot hunter-v04-team-state-sonar \
  --bots hunter-v02-team-growth hunter-v03-team-growth hunter-v04-team-state-sonar \
  --jobs 8 \
  --no-replays \
  --output build/hunter-v04-small

PATH="$PWD/.venv/bin:$PATH" python3 bots/tournament.py \
  --focus-bot hunter-v03-team-growth \
  --bots hunter-v02-team-growth hunter-v03-team-growth hunter-v04-team-state-sonar \
  --jobs 8 \
  --no-replays \
  --output build/hunter-v03-small
```

The third-most-recent version is included mainly as a tiebreaker and baseline;
the primary comparison is between the two focused versions.

## Full Tournament

```sh
PATH="$PWD/.venv/bin:$PATH" python3 bots/tournament.py \
  --focus-bot <bot> \
  --jobs 8 \
  --no-replays \
  --output build/<bot>-full
```

Use this for extensive testing across every bundled map and bot.

Results are saved in `standings.csv` and `results.json` under the selected output directory.

## Versioning

Use flat, zero-padded names so versions sort naturally:

```text
fry-v01-<strategy>
fry-v02-<strategy>
...
fry-v14-<strategy>
hunter-v01-<strategy>
```

The `fry` lineage contains the existing strategy snapshots. The `hunter`
lineage is for new experimental architecture built from the fry snapshots.
Never rename or modify an older version when creating a new experiment; copy
it into the next version first. Every new version must also be added to this
lineage table and to `docs/strategy-backlog.md`.

Current strategy lineage:

| Version | Strategy |
| --- | --- |
| `fry-v01-danger-levels` | danger-level reproduction |
| `fry-v02-dragon-hunters` | aggressive dragon hunting |
| `fry-v03-portal-hunters` | portal pearl trips |
| `fry-v04` through `fry-v10` | strategy variants and pearl seekers |
| `fry-v11-size-aware-hunters` | size-aware attacks |
| `fry-v12-stateful-size-aware-hunters` | persistent map, pearl, and enemy memory |
| `fry-v13-stateful-size-aware-2` | sonar pearl claims |
| `fry-v14-stateful-size-aware-3` | closest-teammate pearl ownership |
| `hunter-v01-team-growth` | team-length estimates and endgame growth |
| `hunter-v02-team-growth` | adaptive growth timing for the largest teammate |
| `hunter-v03-team-growth` | safe unmatched-portal exploration by smaller dragons |
| `hunter-v04-team-state-sonar` | directional 64-bit shared dragon state |
