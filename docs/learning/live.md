# Live monitor (Live ops, lane Daichi)

Generated 2026-10-04 11:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 586 ladder snapshots (latest 2026-10-04 11:48:19+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

## Incumbent

- Live submission **14585** (not a registered candidate; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **611**, W-L-D 304-307-0; score − E -0.029 [-0.059, +0.001] (n 611 games / 125 series).
- First 40 ranked after first sighting: score − E -0.052 [-0.204, +0.071] (n 40 games / 10 series). Rollback rule (binds a promoted candidate: mean < −0.08 and 95th pct < 0 over its first 40): **not met**.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.069 [-0.154, +0.007] (n 40 games / 8 series).
- Elo now 1716 (rank 83); 24 h ago 1744; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 350.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 68: 15, 28, 30, 45, 46, 52, 55, 64, 71, 74, 78, 91, 98, 133, 141, 147, 174, 178, 187, 196 … | -0.029 [-0.059, +0.004] (n 598 games / 122 series) |
| top | current top ten (non-dev) | 10: 306, 91, 264, 213, 507, 566, 842, 952, 55, 19 | +0.013 [-0.082, +0.145] (n 21 games / 5 series) |
| style | one per style — awaits Data's top-teams pages | 0:  | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 30: 15, 30, 46, 64, 71, 98, 104, 174, 178, 196, 217, 262, 280, 306, 312, 328, 440, 465, 467, 485 … | +0.111 [+0.068, +0.154] (n 254 games / 52 series) |

## Per map (ranked, incumbent)

| map | score − E |
|---|---|
| Schooltime | -0.454 [-0.510, -0.395] (n 35 games / 35 series) |
| weakhold | -0.315 [-0.421, -0.216] (n 42 games / 42 series) |
| Trauma | -0.251 [-0.371, -0.119] (n 35 games / 35 series) |
| Prisoners Dilemma | -0.147 [-0.281, -0.019] (n 33 games / 33 series) |
| Australia | -0.141 [-0.277, -0.006] (n 30 games / 30 series) |
| Slithery Fight | -0.114 [-0.240, +0.004] (n 39 games / 39 series) |
| Portals | -0.110 [-0.241, +0.028] (n 41 games / 41 series) |
| Around UNSW | -0.051 [-0.181, +0.081] (n 35 games / 35 series) |
| Stripes | -0.041 [-0.171, +0.086] (n 41 games / 41 series) |
| Autarky | -0.013 [-0.145, +0.123] (n 35 games / 35 series) |
| Trophy | +0.056 [-0.066, +0.174] (n 37 games / 37 series) |
| Default | +0.092 [-0.045, +0.224] (n 29 games / 29 series) |
| Islands | +0.099 [-0.012, +0.207] (n 38 games / 38 series) |
| Maze | +0.117 [-0.015, +0.236] (n 39 games / 39 series) |
| Devil | +0.186 [+0.056, +0.307] (n 35 games / 35 series) |
| Queen Of Spades | +0.285 [+0.192, +0.370] (n 40 games / 40 series) |
| Tower Defense | +0.403 [+0.313, +0.484] (n 27 games / 27 series) |

## Drift (all our ranked games)

- Last 7 days: -0.026 [-0.051, +0.000] (n 983 games / 205 series); the 7 days before: -0.116 [-0.216, -0.016] (n 10 games / 2 series).
- submission 14585: -0.029 [-0.059, +0.001] (n 611 games / 125 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 10473: +0.117 [+0.002, +0.230] (n 59 games / 13 series)
- submission 13010: -0.185 [-0.326, -0.034] (n 40 games / 8 series)
- submission 11398: -0.031 [-0.131, +0.082] (n 32 games / 7 series)
- submission 11969: -0.046 [-0.150, +0.088] (n 31 games / 7 series)
- submission 11244: +0.025 [-0.130, +0.180] (n 20 games / 4 series)
- submission 12851: +0.002 [-0.183, +0.251] (n 14 games / 4 series)
- submission 9508: +0.206 [+0.134, +0.278] (n 10 games / 2 series)
- submission 12440: -0.204 [-0.310, -0.099] (n 10 games / 2 series)
- submission 13086: -0.240 [-0.487, -0.092] (n 8 games / 2 series)
- submission 6422: -0.016 [-0.016, -0.016] (n 5 games / 1 series)
- submission 6394: -0.216 [-0.216, -0.216] (n 5 games / 1 series)
- submission 9663: +0.426 [+0.426, +0.426] (n 5 games / 1 series)
- submission 12728: -0.052 [-0.052, -0.052] (n 5 games / 1 series)

## Errors and timeouts

- Not yet measured for ranked games (needs a replay-side fault read; the hub verifies faults only for games it requests). Requested battles report faults per job in `hub-state/battles/`.
- Ranked games without an Elo expectation (no snapshot): 15.

