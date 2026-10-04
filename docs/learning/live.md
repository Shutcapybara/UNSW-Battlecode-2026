# Live monitor (Live ops, lane Daichi)

Generated 2026-10-04 12:56 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 591 ladder snapshots (latest 2026-10-04 12:49:11+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261004T1256Z-2be3ac55.json.gz` sha256 `2be3ac557bcbf689…` (3253 games with their snapshot ids, 591 snapshots, index sha `7e433eb13296`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **14585** (not a registered candidate; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **690**, W-L-D 347-343-0; score − E -0.022 [-0.053, +0.007] (n 690 games / 140 series).
- First 40 ranked after first sighting: score − E -0.052 [-0.204, +0.071] (n 40 games / 10 series). Rollback rule (binds a promoted candidate: mean < −0.08 and 95th pct < 0 over its first 40): **not met**.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.006 [-0.092, +0.065] (n 40 games / 8 series).
- Elo now 1720 (rank 81); 24 h ago 1738; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 573.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 72: 11, 15, 28, 30, 45, 46, 52, 55, 64, 71, 74, 78, 91, 98, 133, 134, 141, 147, 174, 178 … | -0.022 [-0.054, +0.008] (n 682 games / 138 series) |
| top | current top ten (non-dev) | 10: 91, 306, 264, 213, 507, 952, 842, 566, 19, 454 | +0.006 [-0.104, +0.137] (n 35 games / 7 series) |
| style | one per style — awaits Data's top-teams pages | 0:  | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 34: 11, 15, 30, 46, 64, 71, 98, 104, 134, 174, 178, 196, 217, 262, 280, 306, 312, 328, 440, 465 … | +0.108 [+0.066, +0.151] (n 298 games / 60 series) |

## Per map (ranked, incumbent)

| map | score − E |
|---|---|
| Schooltime | -0.474 [-0.521, -0.423] (n 41 games / 41 series) |
| weakhold | -0.349 [-0.432, -0.248] (n 49 games / 49 series) |
| Trauma | -0.185 [-0.312, -0.064] (n 41 games / 41 series) |
| Prisoners Dilemma | -0.147 [-0.268, -0.023] (n 37 games / 37 series) |
| Australia | -0.139 [-0.267, -0.004] (n 32 games / 32 series) |
| Slithery Fight | -0.134 [-0.252, -0.019] (n 43 games / 43 series) |
| Portals | -0.084 [-0.211, +0.038] (n 45 games / 45 series) |
| Stripes | -0.052 [-0.179, +0.076] (n 42 games / 42 series) |
| Around UNSW | -0.026 [-0.151, +0.105] (n 37 games / 37 series) |
| Autarky | -0.001 [-0.130, +0.117] (n 41 games / 41 series) |
| Default | +0.059 [-0.062, +0.180] (n 32 games / 32 series) |
| Trophy | +0.094 [-0.019, +0.204] (n 43 games / 43 series) |
| Islands | +0.121 [+0.013, +0.219] (n 41 games / 41 series) |
| Maze | +0.134 [+0.006, +0.254] (n 42 games / 42 series) |
| Devil | +0.161 [+0.057, +0.273] (n 44 games / 44 series) |
| Queen Of Spades | +0.295 [+0.215, +0.371] (n 45 games / 45 series) |
| Tower Defense | +0.406 [+0.335, +0.471] (n 35 games / 35 series) |

## Drift (all our ranked games)

- Last 7 days: -0.026 [-0.052, -0.001] (n 1047 games / 217 series); the 7 days before: n 0.
- submission 14585: -0.022 [-0.053, +0.007] (n 690 games / 140 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 10473: +0.117 [+0.002, +0.230] (n 59 games / 13 series)
- submission 13010: -0.185 [-0.326, -0.034] (n 40 games / 8 series)
- submission 11398: -0.031 [-0.131, +0.082] (n 32 games / 7 series)
- submission 11969: -0.046 [-0.150, +0.088] (n 31 games / 7 series)
- submission 11244: +0.025 [-0.130, +0.180] (n 20 games / 4 series)
- submission 12851: +0.002 [-0.183, +0.251] (n 14 games / 4 series)
- submission 12440: -0.204 [-0.310, -0.099] (n 10 games / 2 series)
- submission 13086: -0.240 [-0.487, -0.092] (n 8 games / 2 series)
- submission 12728: -0.052 [-0.052, -0.052] (n 5 games / 1 series)

## Errors and timeouts

- Not yet measured for ranked games (needs a replay-side fault read; the hub verifies faults only for games it requests). Requested battles report faults per job in `hub-state/battles/`.
- Ranked games without an Elo expectation (no snapshot): 40.

