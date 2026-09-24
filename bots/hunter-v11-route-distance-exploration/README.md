# hunter-v11-route-distance-exploration

Python v09 fork that uses visible route distance for exploration spacing when
known paths connect a candidate tile to a teammate. When the local map has no
known route, it falls back to wrapped Manhattan distance. This targets the
segmented-map weakness tracked in the strategy backlog.

Map memory is sparse: v09 caches only observed edges and visited tiles, indexes
portal endpoints as they are seen, and computes neighboring positions on demand.
This avoids dense whole-map startup work. A passing `big_empty` mirror does
not rule out the reported intermittent large-map timeouts; see the results
report.

Run from the repository root:

```sh
PATH="$PWD/.venv/bin:$PATH" unswbc run maps/arena.map \
  bots/hunter-v11-route-distance-exploration bots/hunter-v09-confidence-team-state
```

V11 preserves v09's expiring teammate lengths and sparse map cache. The
all-map tournament will determine whether route-aware exploration improves
the `schooltime` results without regressing other maps.
