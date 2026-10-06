# Live monitor (Live ops, lane Daichi)

Generated 2026-10-06 00:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 795 ladder snapshots (latest 2026-10-06 00:48:55+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261006T0051Z-1ecd54e2.json.gz` sha256 `1ecd54e2a290d4df…` (5134 games with their snapshot ids, 795 snapshots, index sha `bba08b16f52b`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **18078** (bokuto-61-mouth; fingerprint `?`); first seen in the corpus 2026-10-05 23:01:05.464000+00:00.
- Ranked games since first seen: **30**, W-L-D 11-19-0; score − E -0.144 [-0.228, -0.043] (n 30 games / 6 series).
- First 40 ranked after first sighting: score − E -0.144 [-0.228, -0.043] (n 30 games / 6 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.144 [-0.228, -0.043] (n 30 games / 6 series).
- Elo now 1743 (rank 92); 24 h ago 1716; 7 d ago 1762.
- Unranked games of the incumbent in the window (exposure only, not scored here): 35.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 85: 11, 15, 22, 28, 30, 40, 45, 52, 63, 64, 71, 78, 98, 104, 127, 133, 134, 135, 147, 153 … | -0.144 [-0.228, -0.043] (n 30 games / 6 series) |
| top | current top ten (non-dev) | 10: 454, 306, 264, 213, 55, 91, 507, 566, 87, 842 | n 0 |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 0:  | n 0 |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Slithery Fight | -0.676 [-0.676, -0.676] (n 1 games / 1 series) |
| Queen Of Spades | -0.567 [-0.624, -0.511] (n 3 games / 3 series) |
| Around UNSW | -0.506 [-0.519, -0.493] (n 2 games / 2 series) |
| Australia | -0.488 [-0.488, -0.488] (n 1 games / 1 series) |
| Stripes | -0.460 [-0.502, -0.419] (n 3 games / 3 series) |
| Prisoners Dilemma | -0.217 [-0.476, +0.063] (n 4 games / 4 series) |
| ↳ 10 dragons | -0.435 [-0.488, -0.381] (n 2 games / 2 series) |
| ↳ template | +0.000 [-0.507, +0.507] (n 2 games / 2 series) |
| Default | -0.171 [-0.501, +0.158] (n 3 games / 3 series) |
| Maze | -0.016 [-0.416, +0.288] (n 4 games / 4 series) |
| Trophy | +0.086 [-0.252, +0.421] (n 5 games / 5 series) |
| Devil | +0.324 [+0.324, +0.324] (n 1 games / 1 series) |
| Trauma | +0.507 [+0.507, +0.507] (n 1 games / 1 series) |
| weakhold | +0.507 [+0.507, +0.507] (n 1 games / 1 series) |
| Autarky | +0.619 [+0.619, +0.619] (n 1 games / 1 series) |

## Drift (all our ranked games)

- Last 7 days: -0.029 [-0.049, -0.010] (n 1887 games / 385 series); the 7 days before: +0.092 [-0.058, +0.248] (n 34 games / 7 series).
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
- submission 18078: -0.144 [-0.228, -0.043] (n 30 games / 6 series)
- submission 11244: +0.025 [-0.130, +0.180] (n 20 games / 4 series)
- submission 12851: +0.002 [-0.183, +0.251] (n 14 games / 4 series)
- submission 12440: -0.204 [-0.310, -0.099] (n 10 games / 2 series)
- submission 13086: -0.240 [-0.487, -0.092] (n 8 games / 2 series)
- submission 12728: -0.052 [-0.052, -0.052] (n 5 games / 1 series)

## Errors and timeouts

- Not yet measured for ranked games (needs a replay-side fault read; the hub verifies faults only for games it requests). Requested battles report faults per job in `hub-state/battles/`.
- Ranked games without an Elo expectation (no snapshot): 45.

