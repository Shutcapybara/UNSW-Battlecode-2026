# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 13:52 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 730 ladder snapshots (latest 2026-10-05 13:43:36+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T1352Z-065d68a2.json.gz` sha256 `065d68a265d7e736…` (4882 games with their snapshot ids, 730 snapshots, index sha `6620f6c8a7ff`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **17388** (kenma-03-pocket-queen; fingerprint `?`); first seen in the corpus 2026-10-05 05:02:01.225000+00:00.
- Ranked games since first seen: **129**, W-L-D 74-55-0; score − E +0.005 [-0.072, +0.081] (n 129 games / 26 series).
- First 40 ranked after first sighting: score − E +0.092 [-0.061, +0.258] (n 40 games / 8 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.003 [-0.158, +0.125] (n 40 games / 9 series); percentile among the submission's own 90 rolling 40-game windows: 0.567 (D-065 §B).
- Elo now 1780 (rank 71); 24 h ago 1721; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 12.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 84: 11, 15, 22, 28, 30, 52, 64, 71, 78, 98, 104, 127, 133, 134, 135, 141, 147, 153, 174, 187 … | +0.005 [-0.072, +0.081] (n 129 games / 26 series) |
| top | current top ten (non-dev) | 10: 264, 306, 91, 507, 454, 55, 213, 952, 566, 842 | n 0 |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 11: 11, 127, 133, 153, 187, 303, 347, 351, 456, 762, 1015 | +0.152 [+0.071, +0.238] (n 75 games / 15 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| weakhold | -0.379 [-0.606, -0.083] (n 6 games / 6 series) |
| Slithery Fight | -0.292 [-0.524, -0.038] (n 8 games / 8 series) |
| Prisoners Dilemma | -0.243 [-0.544, +0.075] (n 6 games / 6 series) |
| ↳ 10 dragons | -0.108 [-0.372, +0.357] (n 4 games / 4 series) |
| ↳ template | -0.511 [-0.576, -0.447] (n 2 games / 2 series) |
| Trauma | -0.202 [-0.482, +0.099] (n 8 games / 8 series) |
| Trophy | -0.138 [-0.412, +0.113] (n 8 games / 8 series) |
| Autarky | -0.105 [-0.323, +0.103] (n 9 games / 9 series) |
| Around UNSW | -0.036 [-0.263, +0.186] (n 6 games / 6 series) |
| Tower Defense | -0.011 [-0.442, +0.356] (n 5 games / 5 series) |
| Queen Of Spades | +0.023 [-0.200, +0.245] (n 9 games / 9 series) |
| Default | +0.092 [-0.160, +0.314] (n 12 games / 12 series) |
| Australia | +0.106 [-0.138, +0.343] (n 6 games / 6 series) |
| Stripes | +0.120 [-0.155, +0.408] (n 7 games / 7 series) |
| Maze | +0.120 [-0.165, +0.387] (n 8 games / 8 series) |
| Devil | +0.151 [-0.112, +0.426] (n 6 games / 6 series) |
| Portals | +0.196 [-0.011, +0.370] (n 12 games / 12 series) |
| Islands | +0.242 [+0.052, +0.408] (n 9 games / 9 series) |
| Schooltime | +0.360 [+0.273, +0.417] (n 4 games / 4 series) |
| ↳ open4 | +0.301 [+0.223, +0.380] (n 2 games / 2 series) |
| ↳ template | +0.419 [+0.415, +0.424] (n 2 games / 2 series) |

## Drift (all our ranked games)

- Last 7 days: -0.029 [-0.049, -0.010] (n 1745 games / 357 series); the 7 days before: n 0.
- submission 14585: -0.022 [-0.048, +0.002] (n 1095 games / 221 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 17388: +0.005 [-0.072, +0.081] (n 129 games / 26 series)
- submission 17530: -0.054 [-0.128, +0.023] (n 120 games / 24 series)
- submission 10473: +0.117 [+0.002, +0.230] (n 59 games / 13 series)
- submission 16979: -0.211 [-0.327, -0.082] (n 44 games / 9 series)
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
- Ranked games without an Elo expectation (no snapshot): 45.

