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

For Python candidates, include `--sandbox` in both runs to enforce judge CPU
limits and retain verbose diagnostics such as `exceeded CPU limit` and `no
valid action`. The comparison helper excludes those failed matches.

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
| `hunter-v05-safe-attack-routes` | reachable combat targets |
| `hunter-v06-pearl-routing` | route-based pearl ownership |
| `hunter-v07-wide-team-state` | wider sonar IDs and ordered message updates |
| `hunter-v08-pearl-wide-sonar` | pearl routing with wider sonar |
| `hunter-v09-confidence-team-state` | freshness-aware teammate lengths |
| `hunter-v10-confidence-enemy-state` | timestamped enemy-size bounds |
| `hunter-v11-route-distance-exploration` | route-aware teammate spacing |
| `hunter-v12-static-map-spacing` | static terrain routes for exploration spacing |
| `hunter-v13-hybrid-route-spacing` | hybrid portal routing and exploration spacing |
| `hunter-v14-cpp-hybrid-route-spacing` | C++ port of V13; experimental |
| `hunter-v15-shared-territory` | shared hotspots and safe portal exploration |
| `hunter-v16-boost-traps` | size-gated boosts and compact surround; current measured candidate |
| `hunter-v17-portal-first-traps` | portal routes take priority over boost attacks; experimental |
| `hunter-v18-self-trap-lookahead` | six-move safe-route checks for growth and survival; experimental |
| `hunter-v19-safe-growth-lookahead` | survival-aware pearl-route selection and wider equal-depth survival choices; experimental |
| `hunter-v20-portal-scouts` | time-aware pearl hotspots, demand-based single-scout claims, bounded unmatched-portal probing, and a compact-board scout guard; experimental, 13W/9L vs V19 |
| `kraken-v01-roles` | role-based scouts, hunters, and gatherers with sonar gossip |
| `kraken-v02-bigmap` | big-map production, brawl mode, and judge-safe metered search |

## Python Hunter experiments

Use standalone `main.py` plus a Python `bot.toml` for new Hunter snapshots.
Keep older snapshots intact. Run focus tournaments sequentially with `--jobs 4`
and `--timeout 600`: overlapping eight-worker Python tournaments can exhaust
host process resources because every live dragon has a process.

After both focus runs finish, compare their equally weighted, shared-map results:

```sh
python3 bots/summarize_hunter.py build/<candidate>-small build/<previous>-small \
  --output build/<candidate>-comparison.json
python3 tests/test_hunter_python.py
python3 tests/test_hunter_summary.py
```

The summary checks source fingerprints and flags disagreement between repeated
head-to-head fixtures. It reports raw standings and a clean comparison excluding
maps with bot failures in either run. A higher score only establishes improvement
on this small opponent pool; medium/full tests are still needed before submission.
In particular, old C++ Hunter snapshots reject the 16x8 `small` map at startup.
Do not present wins against those failed bots as tactical gains.

Python regression tests are also registered with CTest. CMake/CTest were not
available on PATH during the initial Python iteration, so tests were run directly.

| Version | Strategy |
| --- | --- |
| `hunter-v05-safe-attack-routes` | Python port; current-observation, reachable combat targets |
| `hunter-v06-pearl-routing` | Route-based pearl ownership and shorter food routes |
| `hunter-v07-wide-team-state` | v05 branch with wider sonar IDs and ordered updates |
| `hunter-v08-pearl-wide-sonar` | v06 pearl routes with v07 wide-ID sonar |
| `hunter-v09-confidence-team-state` | v08 with explicit freshness and confidence for teammate lengths |
| `hunter-v10` through `hunter-v13` | See the experiment report for changes, CPU safety, and measured status |
See [Python Hunter results](hunter-python-results.md) for current candidate performance and known regressions.
The Python V14 experiment was removed after losing to V13 (20–24 versus 25–19
in the latest shared pool); its build artifacts remain as historical evidence.
The distinct `hunter-v14-cpp-hybrid-route-spacing` is a C++ port of Python
V13. Its action parity tests pass and it scored 22–22 versus V13's 23–21 in
the paired pool, but it lost all four `big_empty` games. It remains experimental
despite passing a 500-round `big_empty` sandbox mirror at 10.4M peak CPU points;
diagnose its tactical loss before promotion. See the [Hunter results](hunter-python-results.md).
