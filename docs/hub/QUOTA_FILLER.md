# Automatic quota filler

The hub can keep the two unranked challenge allowances busy without opening a
candidate experiment. When enabled, each executor cycle:

- discovers the current top 10 non-dev ladder teams;
- rotates challenges across the configured dev teams (`team.dev_opponents`) and
  any teams the server marks as `dev`;
- sends distinct active-map IDs in small batches and persists target/map cursors;
- accounts for recent server games, accepted reservations, and requests made
  earlier in the same cycle before spending anything;
- stops on an unknown quota picture, a ranked series in flight, a quota 429, or
  the normal executor stop/attention conditions.

The candidate planner still runs first. Its existing executor caps remain in
place; the filler uses only the remainder up to the full `budget.hourly_games`
limits (60 field and 60 dev by default). It always challenges the currently
active submission, so it never activates a candidate or changes the control.

Enable or disable it on the Mac hub host:

```sh
python -m tools.hub.hubctl quota on
python -m tools.hub.hubctl quota status
python -m tools.hub.hubctl quota off
```

`quota on` takes effect on the next executor cycle. `quota off` prevents new
filler requests but leaves existing requests available for normal harvesting.
The executor must also be in its normal live mode before POST requests are
sent; shadow mode records the planned challenges without mutating the server.

Optional settings live in the external hub `hub.toml` under `[quota_filler]`:

```toml
[quota_filler]
enabled = false
top_n = 10
batch_games = 10
cycle_games = 10
include_ladder_devs = true
field_opponents = []
reserve_games = {}
```

`field_opponents` can pin a reviewed field panel instead of using the live
top-N ladder. `cycle_games` limits automatic filler to that many games per
pool per executor cycle. With the default ten-minute executor cadence and
`cycle_games = 10`, the filler sends at most 10 field and 10 dev games every
10 minutes. `reserve_games` is useful when teammates need guaranteed manual
headroom; leave it empty to try to use the full allowance over time.
