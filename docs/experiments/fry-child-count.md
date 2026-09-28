# Historical Fry child-count comparison

[`tools/experiments/fry_child_count/compare.py`](../../tools/experiments/fry_child_count/compare.py)
compares the frozen `fry-v06-one-child` and `fry-v07-two-children` snapshots.
It runs both team assignments for each top-level `maps/*.map` file and writes
logs, replays, and `results.json` under the ignored
`build/child-comparison/` directory.

Run it from the repository root with:

```sh
python3 tools/experiments/fry_child_count/compare.py
```

This is a small, non-sandboxed matchup reproduction. The script scans only the
top-level map files, so it does not include maps nested under `maps/new/`. Treat
it as historical experiment tooling; use the current roster and methods in
[`FRONTIER.md`](../../FRONTIER.md) and
[`docs/benchmarking.md`](../benchmarking.md) for current bot evaluations.
