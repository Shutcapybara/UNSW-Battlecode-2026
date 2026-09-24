# hunter-v12-static-map-spacing

Python v11 fork that measures exploration spacing over observed static map
routes, ignoring temporary dragon bodies that may move before a later visit.
Pearl ownership keeps its body-aware path check; unknown routes still fall back
to wrapped Manhattan distance.

Map memory is sparse: v09 caches only observed edges and visited tiles, indexes
portal endpoints as they are seen, and computes neighboring positions on demand.
This avoids dense whole-map startup work. A passing `big_empty` mirror does
not rule out the reported intermittent large-map timeouts; see the results
report.

Run from the repository root:

```sh
PATH="$PWD/.venv/bin:$PATH" unswbc run maps/arena.map \
  bots/hunter-v12-static-map-spacing bots/hunter-v11-route-distance-exploration
```

V12 preserves v09's expiring teammate lengths and sparse map cache. It responds
to V11's 0–4 `small` result by separating static-map spacing estimates from
body-aware pearl ownership. Its all-map tournament will test whether that
removes the regression.
