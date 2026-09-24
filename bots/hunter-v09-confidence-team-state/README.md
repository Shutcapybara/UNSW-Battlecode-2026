# hunter-v09-confidence-team-state

Python v08 fork that separates exact teammate length reports from current
visible body counts. Sonar records keep their sender round and expire after 20
rounds; partial visual observations stay lower bounds and cannot refresh stale
lengths. Older messages still cannot overwrite newer reports.

Map memory is sparse: v09 caches only observed edges and visited tiles, indexes
portal endpoints as they are seen, and computes neighboring positions on demand.
Sparse caching fixes the observed round-0 startup overrun. Two current 500-round
64x64 `big_empty` sandbox runs passed: a mirror peaked at 65.3M CPU points, and
a match against the existing C++ baseline peaked at 64.1M, with no invalid
actions in either. A report of intermittent large-map timeouts remains
unresolved; these runs do not establish reliability across all submitted maps.

Run from the repository root:

```sh
PATH="$PWD/.venv/bin:$PATH" unswbc run maps/arena.map \
  bots/hunter-v09-confidence-team-state bots/hunter-v08-pearl-wide-sonar
```

V09 addresses stale friendly lengths and the `big_empty` startup CPU failure.
Its old normal-runner score needs remeasurement after the sparse-map fix.
