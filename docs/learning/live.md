# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 07:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 695 ladder snapshots (latest 2026-10-05 07:43:24+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T0751Z-a9e976df.json.gz` sha256 `a9e976df09ca81e8…` (4661 games with their snapshot ids, 695 snapshots, index sha `9c18f5d5dfca`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **17388** (kenma-03-pocket-queen; fingerprint `?`); first seen in the corpus 2026-10-05 05:02:01.225000+00:00.
- Ranked games since first seen: **80**, W-L-D 43-37-0; score − E +0.005 [-0.101, +0.112] (n 80 games / 16 series).
- First 40 ranked after first sighting: score − E +0.092 [-0.061, +0.258] (n 40 games / 8 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.081 [-0.205, +0.045] (n 40 games / 8 series); percentile among the submission's own 41 rolling 40-game windows: 0.268 (D-065 §B).
- Elo now 1768 (rank 78); 24 h ago 1721; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 0.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 80: 11, 15, 28, 30, 52, 64, 71, 78, 98, 104, 127, 133, 134, 135, 141, 147, 174, 178, 187, 196 … | +0.005 [-0.101, +0.112] (n 80 games / 16 series) |
| top | current top ten (non-dev) | 10: 264, 91, 306, 55, 454, 952, 842, 213, 507, 566 | n 0 |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 6: 133, 187, 347, 351, 456, 1015 | +0.184 [+0.047, +0.324] (n 40 games / 8 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| weakhold | -0.436 [-0.583, -0.289] (n 2 games / 2 series) |
| Prisoners Dilemma | -0.336 [-0.594, -0.079] (n 4 games / 4 series) |
| ↳ 10 dragons | -0.257 [-0.598, +0.085] (n 3 games / 3 series) |
| ↳ template | -0.576 [-0.576, -0.576] (n 1 games / 1 series) |
| Trophy | -0.329 [-0.541, -0.092] (n 6 games / 6 series) |
| Slithery Fight | -0.266 [-0.534, +0.045] (n 4 games / 4 series) |
| Around UNSW | -0.142 [-0.361, +0.077] (n 3 games / 3 series) |
| Trauma | -0.112 [-0.503, +0.319] (n 5 games / 5 series) |
| Default | -0.053 [-0.405, +0.293] (n 6 games / 6 series) |
| Autarky | -0.051 [-0.299, +0.172] (n 8 games / 8 series) |
| Australia | +0.117 [-0.205, +0.430] (n 5 games / 5 series) |
| Tower Defense | +0.119 [-0.310, +0.548] (n 3 games / 3 series) |
| Queen Of Spades | +0.133 [-0.180, +0.424] (n 4 games / 4 series) |
| Devil | +0.147 [-0.289, +0.584] (n 2 games / 2 series) |
| Portals | +0.162 [-0.088, +0.391] (n 10 games / 10 series) |
| Maze | +0.178 [-0.171, +0.507] (n 4 games / 4 series) |
| Islands | +0.195 [-0.013, +0.402] (n 7 games / 7 series) |
| Stripes | +0.259 [-0.109, +0.551] (n 5 games / 5 series) |
| Schooltime | +0.324 [+0.223, +0.424] (n 2 games / 2 series) |
| ↳ open4 | +0.223 [+0.223, +0.223] (n 1 games / 1 series) |
| ↳ template | +0.424 [+0.424, +0.424] (n 1 games / 1 series) |

## Drift (all our ranked games)

- Last 7 days: -0.028 [-0.050, -0.005] (n 1576 games / 323 series); the 7 days before: n 0.
- submission 14585: -0.022 [-0.048, +0.002] (n 1095 games / 221 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 17388: +0.005 [-0.101, +0.112] (n 80 games / 16 series)
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

