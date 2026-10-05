# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 22:50 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 783 ladder snapshots (latest 2026-10-05 22:46:09+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T2250Z-78ce92b3.json.gz` sha256 `78ce92b32a98ceb5…` (5069 games with their snapshot ids, 783 snapshots, index sha `6e154bbec91d`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **17940** (asahi-27-b13-reserve; fingerprint `?`); first seen in the corpus 2026-10-05 18:37:04.646000+00:00.
- Ranked games since first seen: **80**, W-L-D 35-45-0; score − E -0.003 [-0.088, +0.082] (n 80 games / 16 series).
- First 40 ranked after first sighting: score − E -0.012 [-0.123, +0.101] (n 40 games / 8 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E +0.006 [-0.139, +0.140] (n 40 games / 8 series); percentile among the submission's own 41 rolling 40-game windows: 0.220 (D-065 §B).
- Elo now 1840 (rank 59); 24 h ago 1720; 7 d ago 1777.
- Unranked games of the incumbent in the window (exposure only, not scored here): 4.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 83: 11, 22, 28, 30, 40, 52, 63, 64, 71, 78, 98, 104, 127, 133, 134, 135, 147, 153, 174, 187 … | -0.003 [-0.088, +0.082] (n 80 games / 16 series) |
| top | current top ten (non-dev) | 10: 264, 91, 454, 55, 507, 157, 87, 952, 213, 842 | +0.089 [+0.089, +0.089] (n 5 games / 1 series) |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 8: 133, 147, 221, 328, 733, 842, 844, 1055 | +0.118 [+0.035, +0.212] (n 50 games / 10 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Autarky | -0.322 [-0.575, -0.061] (n 6 games / 6 series) |
| weakhold | -0.313 [-0.535, -0.085] (n 6 games / 6 series) |
| Maze | -0.274 [-0.533, +0.010] (n 5 games / 5 series) |
| Default | -0.203 [-0.459, +0.059] (n 6 games / 6 series) |
| Australia | -0.170 [-0.404, +0.063] (n 8 games / 8 series) |
| Trauma | -0.159 [-0.431, +0.170] (n 4 games / 4 series) |
| Slithery Fight | -0.090 [-0.427, +0.246] (n 4 games / 4 series) |
| Stripes | -0.020 [-0.288, +0.268] (n 5 games / 5 series) |
| Trophy | +0.005 [-0.298, +0.425] (n 4 games / 4 series) |
| Prisoners Dilemma | +0.024 [-0.166, +0.215] (n 3 games / 3 series) |
| ↳ 10 dragons | +0.118 [-0.168, +0.403] (n 2 games / 2 series) |
| ↳ template | -0.163 [-0.163, -0.163] (n 1 games / 1 series) |
| Portals | +0.151 [-0.141, +0.443] (n 4 games / 4 series) |
| Islands | +0.219 [-0.114, +0.511] (n 6 games / 6 series) |
| Schooltime | +0.279 [-0.019, +0.547] (n 5 games / 5 series) |
| ↳ open4 | +0.279 [-0.019, +0.547] (n 5 games / 5 series) |
| Around UNSW | +0.337 [+0.142, +0.532] (n 4 games / 4 series) |
| Devil | +0.372 [+0.057, +0.620] (n 5 games / 5 series) |
| Queen Of Spades | +0.406 [+0.044, +0.758] (n 5 games / 5 series) |

## Drift (all our ranked games)

- Last 7 days: -0.027 [-0.046, -0.008] (n 1857 games / 379 series); the 7 days before: +0.092 [-0.058, +0.248] (n 34 games / 7 series).
- submission 14585: -0.022 [-0.048, +0.002] (n 1095 games / 221 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 17388: +0.008 [-0.066, +0.084] (n 130 games / 26 series)
- submission 17530: -0.054 [-0.128, +0.023] (n 120 games / 24 series)
- submission 17940: -0.003 [-0.088, +0.082] (n 80 games / 16 series)
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

