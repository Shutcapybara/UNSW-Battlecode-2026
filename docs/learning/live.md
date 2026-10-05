# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 16:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 748 ladder snapshots (latest 2026-10-05 16:47:36+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T1651Z-87afd764.json.gz` sha256 `87afd764699bbea1…` (4960 games with their snapshot ids, 748 snapshots, index sha `afcfdc658e0e`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **17791** (bokuto-18-queenfeed; fingerprint `?`); first seen in the corpus 2026-10-05 14:17:30.567000+00:00.
- Ranked games since first seen: **40**, W-L-D 22-18-0; score − E +0.058 [-0.029, +0.145] (n 40 games / 8 series).
- First 40 ranked after first sighting: score − E +0.058 [-0.029, +0.145] (n 40 games / 8 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E +0.058 [-0.029, +0.145] (n 40 games / 8 series); percentile among the submission's own 1 rolling 40-game windows: 1.000 (D-065 §B).
- Elo now 1836 (rank 63); 24 h ago 1721; 7 d ago 1737.
- Unranked games of the incumbent in the window (exposure only, not scored here): 37.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 83: 11, 15, 22, 28, 30, 40, 52, 64, 71, 78, 98, 104, 127, 133, 134, 135, 141, 147, 153, 174 … | +0.058 [-0.029, +0.145] (n 40 games / 8 series) |
| top | current top ten (non-dev) | 10: 264, 306, 507, 91, 213, 454, 55, 157, 842, 19 | n 0 |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 6: 40, 357, 499, 801, 844, 919 | +0.120 [+0.042, +0.198] (n 30 games / 6 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Prisoners Dilemma | -0.590 [-0.590, -0.590] (n 1 games / 1 series) |
| ↳ 10 dragons | -0.590 [-0.590, -0.590] (n 1 games / 1 series) |
| Autarky | -0.533 [-0.590, -0.476] (n 2 games / 2 series) |
| Queen Of Spades | -0.528 [-0.581, -0.476] (n 2 games / 2 series) |
| Trauma | -0.476 [-0.476, -0.476] (n 1 games / 1 series) |
| Australia | -0.437 [-0.437, -0.437] (n 1 games / 1 series) |
| Default | -0.393 [-0.617, -0.170] (n 2 games / 2 series) |
| Trophy | -0.375 [-0.581, -0.170] (n 2 games / 2 series) |
| Portals | -0.027 [-0.437, +0.383] (n 2 games / 2 series) |
| weakhold | +0.065 [-0.344, +0.443] (n 5 games / 5 series) |
| Islands | +0.120 [-0.170, +0.410] (n 2 games / 2 series) |
| Tower Defense | +0.143 [-0.196, +0.483] (n 5 games / 5 series) |
| Slithery Fight | +0.278 [-0.057, +0.481] (n 6 games / 6 series) |
| Schooltime | +0.448 [+0.410, +0.486] (n 3 games / 3 series) |
| ↳ open4 | +0.448 [+0.410, +0.486] (n 3 games / 3 series) |
| Around UNSW | +0.473 [+0.383, +0.563] (n 2 games / 2 series) |
| Maze | +0.522 [+0.522, +0.522] (n 1 games / 1 series) |
| Devil | +0.587 [+0.447, +0.727] (n 3 games / 3 series) |

## Drift (all our ranked games)

- Last 7 days: -0.027 [-0.048, -0.006] (n 1786 games / 365 series); the 7 days before: n 0.
- submission 14585: -0.022 [-0.048, +0.002] (n 1095 games / 221 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 17388: +0.008 [-0.066, +0.084] (n 130 games / 26 series)
- submission 17530: -0.054 [-0.128, +0.023] (n 120 games / 24 series)
- submission 10473: +0.117 [+0.002, +0.230] (n 59 games / 13 series)
- submission 16979: -0.211 [-0.327, -0.082] (n 44 games / 9 series)
- submission 13010: -0.185 [-0.326, -0.034] (n 40 games / 8 series)
- submission 17791: +0.058 [-0.029, +0.145] (n 40 games / 8 series)
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

