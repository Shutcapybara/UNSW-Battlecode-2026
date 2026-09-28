# chaewon-y06-lean

`chaewon-y04-probe` with a cheaper first turn (behaviour-identical): the atlas load resets the destination caches by
slice assignment instead of 2 × W·H Python stores, and a candidate's portal map is built only when a portal edge is
in view. The atlas makes every process's first turn the expensive one (y05 on Schooltime: first-turn p50 59M, max
74M vs p99 34M on other turns).

## Metering (`--sandbox -v` vs sinbad-v07; 0 CPU faults, 0 caught errors)

| Toolkit | Fixture | p50 | p99 | max | turns | first-turn p50 / max |
|---|---|---|---|---|---|---|
| 1.2.2 (seed 1) | Schooltime, we are A | 17.3M | 50.2M | 67.5M | 10,742 | 48.1M / 67.5M |
| 1.2.2 (seed 1) | Portals, we are B | 19.0M | 54.4M | 68.9M | 7,463 | 50.7M / 65.1M |
| 1.0.0 | Schooltime, we are A | 17.1M | 46.1M | 57.0M | 24,441 | 48.1M / 57.0M |
| 1.0.0 | Portals, we are B | 19.1M | 54.3M | 68.8M | 7,657 | — |

yuna-v05-core on the same 1.2.2 Schooltime fixture: p99 47.9M, max 57.2M, first-turn p50 47.8M — the lean atlas load
costs nothing measurable on the first turn (y05: 59M).
Panel evidence: identical policy to `chaewon-y04-probe` (pooled 196 fixtures vs yuna-v05: +0.036, 33/26, p = 0.44).
