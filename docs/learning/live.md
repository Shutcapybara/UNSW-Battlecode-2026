# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 18:17 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 756 ladder snapshots (latest 2026-10-05 18:09:50+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T1817Z-365db65e.json.gz` sha256 `365db65eb9d72e86…` (4985 games with their snapshot ids, 756 snapshots, index sha `4a56c76912a5`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **17791** (bokuto-18-queenfeed; fingerprint `?`); first seen in the corpus 2026-10-05 14:17:30.567000+00:00.
- Ranked games since first seen: **65**, W-L-D 33-32-0; score − E +0.041 [-0.053, +0.140] (n 65 games / 13 series).
- First 40 ranked after first sighting: score − E +0.058 [-0.029, +0.145] (n 40 games / 8 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.010 [-0.135, +0.130] (n 40 games / 8 series); percentile among the submission's own 26 rolling 40-game windows: 0.077 (D-065 §B).
- Elo now 1829 (rank 60); 24 h ago 1725; 7 d ago 1770.
- Unranked games of the incumbent in the window (exposure only, not scored here): 37.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 85: 11, 22, 28, 30, 40, 52, 63, 64, 71, 78, 98, 104, 127, 133, 134, 135, 141, 147, 153, 174 … | +0.041 [-0.053, +0.140] (n 65 games / 13 series) |
| top | current top ten (non-dev) | 10: 264, 306, 91, 55, 157, 213, 454, 19, 842, 952 | n 0 |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 8: 40, 135, 357, 499, 566, 801, 844, 919 | +0.165 [+0.067, +0.278] (n 40 games / 8 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Queen Of Spades | -0.482 [-0.529, -0.436] (n 4 games / 4 series) |
| Trauma | -0.476 [-0.476, -0.476] (n 1 games / 1 series) |
| Trophy | -0.409 [-0.547, -0.272] (n 3 games / 3 series) |
| Stripes | -0.396 [-0.567, -0.225] (n 3 games / 3 series) |
| Default | -0.393 [-0.617, -0.170] (n 2 games / 2 series) |
| Prisoners Dilemma | -0.365 [-0.590, -0.140] (n 2 games / 2 series) |
| ↳ 10 dragons | -0.365 [-0.590, -0.140] (n 2 games / 2 series) |
| Autarky | -0.239 [-0.552, +0.073] (n 3 games / 3 series) |
| Australia | -0.012 [-0.338, +0.315] (n 3 games / 3 series) |
| Around UNSW | +0.047 [-0.247, +0.302] (n 6 games / 6 series) |
| weakhold | +0.067 [-0.236, +0.355] (n 7 games / 7 series) |
| Portals | +0.098 [-0.176, +0.371] (n 3 games / 3 series) |
| Maze | +0.137 [-0.262, +0.535] (n 3 games / 3 series) |
| Slithery Fight | +0.170 [-0.129, +0.451] (n 7 games / 7 series) |
| Tower Defense | +0.263 [-0.046, +0.588] (n 6 games / 6 series) |
| Islands | +0.347 [+0.120, +0.557] (n 4 games / 4 series) |
| Schooltime | +0.472 [+0.439, +0.529] (n 4 games / 4 series) |
| ↳ open4 | +0.448 [+0.410, +0.486] (n 3 games / 3 series) |
| ↳ template | +0.542 [+0.542, +0.542] (n 1 games / 1 series) |
| Devil | +0.571 [+0.466, +0.725] (n 4 games / 4 series) |

## Drift (all our ranked games)

- Last 7 days: -0.028 [-0.047, -0.008] (n 1799 games / 368 series); the 7 days before: +0.179 [+0.045, +0.368] (n 12 games / 3 series).
- submission 14585: -0.022 [-0.048, +0.002] (n 1095 games / 221 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 17388: +0.008 [-0.066, +0.084] (n 130 games / 26 series)
- submission 17530: -0.054 [-0.128, +0.023] (n 120 games / 24 series)
- submission 17791: +0.041 [-0.053, +0.140] (n 65 games / 13 series)
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

