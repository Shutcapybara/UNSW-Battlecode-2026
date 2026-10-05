# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 01:52 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 661 ladder snapshots (latest 2026-10-05 01:44:46+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T0152Z-c510ee88.json.gz` sha256 `c510ee885ab71a61…` (4511 games with their snapshot ids, 661 snapshots, index sha `4cae274ba6c1`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **14585** (carthage-05-free-sprint; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **1085**, W-L-D 539-546-0; score − E -0.023 [-0.048, +0.002] (n 1085 games / 219 series).
- First 40 ranked after first sighting: score − E -0.017 [-0.106, +0.065] (n 40 games / 10 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.044 [-0.191, +0.102] (n 40 games / 8 series); percentile among the submission's own 1046 rolling 40-game windows: 0.435 (D-065 §B).
- Elo now 1720 (rank 90); 24 h ago 1704; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 1349.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 84: 11, 15, 28, 30, 45, 46, 52, 64, 71, 74, 78, 91, 98, 104, 133, 134, 135, 141, 147, 174 … | -0.028 [-0.053, -0.002] (n 972 games / 196 series) |
| top | current top ten (non-dev) | 10: 306, 264, 952, 213, 91, 454, 55, 842, 507, 19 | +0.051 [-0.036, +0.140] (n 60 games / 12 series) |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | +0.171 [+0.043, +0.299] (n 15 games / 3 series) |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 45: 15, 30, 46, 55, 64, 71, 87, 98, 134, 135, 174, 178, 196, 199, 217, 221, 258, 262, 280, 306 … | +0.106 [+0.074, +0.138] (n 468 games / 94 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Schooltime | -0.483 [-0.514, -0.450] (n 77 games / 77 series) |
| ↳ open4 | -0.518 [-0.555, -0.481] (n 38 games / 38 series) |
| ↳ template | -0.449 [-0.496, -0.395] (n 39 games / 39 series) |
| weakhold | -0.314 [-0.389, -0.234] (n 68 games / 68 series) |
| Trauma | -0.210 [-0.304, -0.111] (n 68 games / 68 series) |
| Prisoners Dilemma | -0.118 [-0.214, -0.018] (n 64 games / 64 series) |
| ↳ 10 dragons | -0.085 [-0.228, +0.054] (n 33 games / 33 series) |
| ↳ template | -0.153 [-0.284, -0.018] (n 31 games / 31 series) |
| Portals | -0.100 [-0.198, -0.012] (n 69 games / 69 series) |
| Around UNSW | -0.091 [-0.200, +0.015] (n 56 games / 56 series) |
| Slithery Fight | -0.081 [-0.178, +0.014] (n 62 games / 62 series) |
| Stripes | -0.063 [-0.168, +0.045] (n 62 games / 62 series) |
| Australia | -0.044 [-0.151, +0.063] (n 52 games / 52 series) |
| Autarky | +0.010 [-0.093, +0.110] (n 65 games / 65 series) |
| Maze | +0.029 [-0.075, +0.125] (n 67 games / 67 series) |
| Trophy | +0.076 [-0.020, +0.180] (n 68 games / 68 series) |
| Default | +0.107 [+0.004, +0.212] (n 56 games / 56 series) |
| Islands | +0.134 [+0.047, +0.221] (n 62 games / 62 series) |
| Devil | +0.195 [+0.103, +0.285] (n 66 games / 66 series) |
| Queen Of Spades | +0.336 [+0.277, +0.395] (n 67 games / 67 series) |
| Tower Defense | +0.381 [+0.323, +0.437] (n 56 games / 56 series) |

## Drift (all our ranked games)

- Last 7 days: -0.025 [-0.047, -0.004] (n 1442 games / 296 series); the 7 days before: n 0.
- submission 14585: -0.023 [-0.048, +0.002] (n 1085 games / 219 series)
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
- Ranked games without an Elo expectation (no snapshot): 45.

