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
| `hunter-v21-emergency-portals` | V20 plus a last-resort portal crossing when ordinary exits are blocked; experimental, 10W/12L vs V20 |
| `hunter-v22-frontier-exploration` | V21 with frontier-first exploration and multiple shortage-based portal scouts; 9W/13L vs V21 on all maps, no errors |
| `hunter-v23-supported-arrival-feed` | V22 with radius-four supported hunts, arrival-time bed targets, Estuary regional bias, and guarded late crown feeding; native focus gauntlet 71W/137L overall, 15W/11L vs V22, not promoted |
| `kraken-v01-roles` | role-based scouts, hunters, and gatherers with sonar gossip |
| `kraken-v02-bigmap` | big-map production, brawl mode, and judge-safe metered search |
| `kraken-v03-judge-safe` | snapshot of kraken-v02 after sandbox CPU hardening |
| `kraken-v04-eval` | v03 with kbench-parameterised CFG; eval-function baseline (identical behavior) |
| `hydra-v01-core` | python from-scratch swarm with sonar gossip map |
| `hydra-v02-hunters` | python pack hunting (beats fry-v03 17-9) |
| `hydra-v03-grower` | python swarm-of-equals + late split freeze |
| `hydra-v06-echo` | hunter-v03 forked to protocol 3: status radio, enemy gossip, echo radar |
| `hydra-v07-farm-first` | v06 + gossip chase gated on units>=6 && length>=4 (not promoted) |
| `hydra-v08-claims` | v07 + whole-swarm r400 farm switch + owns_pearl growth BFS (not promoted) |
| `hydra-v09-lanchester` | v08 + retreat-while-outnumbered evasion (not promoted) |
| `hydra-v10-farmclean` | v08 minus stalker-flee in farm mode (not promoted; field 150 vs v06 159) |

## Iteration loop (kraken)

`docs/kraken-design-framework.md` defines the method; `bots/kbench.py` is
the tooling:

```sh
python3 bots/kbench.py variant kraken-v04-eval kraken-v05-<hypo> --set key=value ...
python3 bots/kbench.py run screen --bots kraken-v05-<hypo>      # fast kill/keep
python3 bots/kbench.py run bench  --bots kraken-v05-<hypo>      # sandbox confirm
python3 bots/kbench.py analyze build/kbench-bench-kraken-v05-<hypo>
python3 bots/kbench.py compare build/kbench-bench-A build/kbench-bench-B
```

Long runs go through `nohup`; screen is non-sandbox (fast), bench and pool
are sandboxed (judge-true). One hypothesis per variant; see the framework
doc for the full rules.
