# Live monitor (Live ops, lane Daichi)

Generated 2026-10-04 10:45 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 580 ladder snapshots (latest 2026-10-04 10:45:16+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

## Incumbent

- Live submission **14585** (not a registered candidate; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **417**, W-L-D 211-206-0; score − E -0.037 [-0.079, +0.003] (n 417 games / 87 series).
- First 40 ranked after first sighting: score − E -0.052 [-0.204, +0.071] (n 40 games / 10 series). Rollback rule (binds a promoted candidate: mean < −0.08 and 95th pct < 0 over its first 40): **not met**.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.093 [-0.184, -0.002] (n 40 games / 8 series) — **below −0.08 with 95th pct < 0**.
- Elo now 1716 (rank 82); 24 h ago 1744; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 272.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 46: 15, 28, 30, 52, 55, 64, 71, 78, 98, 133, 141, 147, 174, 196, 203, 213, 217, 262, 312, 328 … | -0.038 [-0.080, +0.003] (n 401 games / 83 series) |
| top | current top ten (non-dev) | 10: 264, 306, 91, 507, 566, 112, 213, 842, 952, 55 | -0.071 [-0.084, -0.059] (n 10 games / 2 series) |
| style | one per style — awaits Data's top-teams pages | 0:  | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 22: 15, 30, 64, 71, 98, 104, 174, 196, 203, 217, 262, 312, 328, 440, 465, 501, 529, 844, 939, 1055 … | +0.108 [+0.051, +0.162] (n 170 games / 34 series) |

## Per map (ranked, incumbent)

| map | score − E |
|---|---|
| Schooltime | -0.447 [-0.519, -0.370] (n 24 games / 24 series) |
| weakhold | -0.299 [-0.420, -0.183] (n 30 games / 30 series) |
| Trauma | -0.259 [-0.418, -0.111] (n 23 games / 23 series) |
| Prisoners Dilemma | -0.140 [-0.292, +0.019] (n 23 games / 23 series) |
| Slithery Fight | -0.123 [-0.264, +0.015] (n 31 games / 31 series) |
| Around UNSW | -0.113 [-0.259, +0.049] (n 24 games / 24 series) |
| Australia | -0.103 [-0.283, +0.058] (n 21 games / 21 series) |
| Portals | -0.053 [-0.215, +0.109] (n 26 games / 26 series) |
| Stripes | -0.004 [-0.156, +0.140] (n 28 games / 28 series) |
| Autarky | +0.019 [-0.165, +0.193] (n 21 games / 21 series) |
| Islands | +0.058 [-0.074, +0.199] (n 27 games / 27 series) |
| Default | +0.072 [-0.110, +0.233] (n 18 games / 18 series) |
| Trophy | +0.074 [-0.061, +0.208] (n 26 games / 26 series) |
| Maze | +0.088 [-0.058, +0.225] (n 26 games / 26 series) |
| Devil | +0.127 [-0.026, +0.263] (n 23 games / 23 series) |
| Queen Of Spades | +0.226 [+0.100, +0.334] (n 28 games / 28 series) |
| Tower Defense | +0.373 [+0.250, +0.482] (n 18 games / 18 series) |

## Drift (all our ranked games)

- Last 7 days: -0.029 [-0.060, +0.000] (n 789 games / 167 series); the 7 days before: -0.116 [-0.216, -0.016] (n 10 games / 2 series).
- submission 14585: -0.037 [-0.079, +0.003] (n 417 games / 87 series)
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

