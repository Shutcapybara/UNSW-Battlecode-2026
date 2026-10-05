# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 17:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 754 ladder snapshots (latest 2026-10-05 17:49:17+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T1751Z-0a353f64.json.gz` sha256 `0a353f647d088cf6…` (4979 games with their snapshot ids, 754 snapshots, index sha `ff10ddf9420b`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **17791** (bokuto-18-queenfeed; fingerprint `?`); first seen in the corpus 2026-10-05 14:17:30.567000+00:00.
- Ranked games since first seen: **59**, W-L-D 31-28-0; score − E +0.035 [-0.072, +0.154] (n 59 games / 12 series).
- First 40 ranked after first sighting: score − E +0.058 [-0.029, +0.145] (n 40 games / 8 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.011 [-0.149, +0.138] (n 40 games / 9 series); percentile among the submission's own 20 rolling 40-game windows: 0.050 (D-065 §B).
- Elo now 1838 (rank 59); 24 h ago 1725; 7 d ago 1767.
- Unranked games of the incumbent in the window (exposure only, not scored here): 37.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 85: 11, 15, 22, 28, 30, 40, 52, 63, 64, 71, 78, 98, 104, 127, 133, 134, 135, 141, 147, 153 … | +0.035 [-0.072, +0.154] (n 59 games / 12 series) |
| top | current top ten (non-dev) | 10: 264, 306, 55, 91, 157, 507, 213, 454, 19, 952 | n 0 |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 7: 40, 135, 357, 499, 801, 844, 919 | +0.180 [+0.081, +0.303] (n 35 games / 7 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Prisoners Dilemma | -0.590 [-0.590, -0.590] (n 1 games / 1 series) |
| ↳ 10 dragons | -0.590 [-0.590, -0.590] (n 1 games / 1 series) |
| Stripes | -0.524 [-0.653, -0.395] (n 2 games / 2 series) |
| Queen Of Spades | -0.482 [-0.529, -0.436] (n 4 games / 4 series) |
| Trauma | -0.476 [-0.476, -0.476] (n 1 games / 1 series) |
| Trophy | -0.409 [-0.547, -0.272] (n 3 games / 3 series) |
| Default | -0.393 [-0.617, -0.170] (n 2 games / 2 series) |
| Autarky | -0.239 [-0.552, +0.073] (n 3 games / 3 series) |
| Around UNSW | +0.018 [-0.416, +0.428] (n 4 games / 4 series) |
| Australia | +0.052 [-0.437, +0.542] (n 2 games / 2 series) |
| weakhold | +0.067 [-0.236, +0.355] (n 7 games / 7 series) |
| Portals | +0.098 [-0.176, +0.371] (n 3 games / 3 series) |
| Maze | +0.137 [-0.262, +0.535] (n 3 games / 3 series) |
| Tower Defense | +0.143 [-0.196, +0.483] (n 5 games / 5 series) |
| Slithery Fight | +0.170 [-0.129, +0.451] (n 7 games / 7 series) |
| Islands | +0.347 [+0.120, +0.557] (n 4 games / 4 series) |
| Schooltime | +0.472 [+0.439, +0.529] (n 4 games / 4 series) |
| ↳ open4 | +0.448 [+0.410, +0.486] (n 3 games / 3 series) |
| ↳ template | +0.542 [+0.542, +0.542] (n 1 games / 1 series) |
| Devil | +0.571 [+0.466, +0.725] (n 4 games / 4 series) |

## Drift (all our ranked games)

- Last 7 days: -0.027 [-0.047, -0.005] (n 1796 games / 367 series); the 7 days before: +0.070 [-0.001, +0.159] (n 9 games / 2 series).
- submission 14585: -0.022 [-0.048, +0.002] (n 1095 games / 221 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 17388: +0.008 [-0.066, +0.084] (n 130 games / 26 series)
- submission 17530: -0.054 [-0.128, +0.023] (n 120 games / 24 series)
- submission 10473: +0.117 [+0.002, +0.230] (n 59 games / 13 series)
- submission 17791: +0.035 [-0.072, +0.154] (n 59 games / 12 series)
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

