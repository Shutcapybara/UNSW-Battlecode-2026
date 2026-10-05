# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 20:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 771 ladder snapshots (latest 2026-10-05 20:43:18+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T2051Z-b4c60c50.json.gz` sha256 `b4c60c50f94fdd8b…` (5025 games with their snapshot ids, 771 snapshots, index sha `9858cfa53529`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **17940** (asahi-27-b13-reserve; fingerprint `?`); first seen in the corpus 2026-10-05 18:37:04.646000+00:00.
- Ranked games since first seen: **40**, W-L-D 17-23-0; score − E -0.012 [-0.123, +0.101] (n 40 games / 8 series).
- First 40 ranked after first sighting: score − E -0.012 [-0.123, +0.101] (n 40 games / 8 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.012 [-0.123, +0.101] (n 40 games / 8 series); percentile among the submission's own 1 rolling 40-game windows: 1.000 (D-065 §B).
- Elo now 1818 (rank 62); 24 h ago 1724; 7 d ago 1783.
- Unranked games of the incumbent in the window (exposure only, not scored here): 0.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 83: 11, 22, 28, 30, 40, 52, 63, 64, 71, 78, 98, 104, 127, 133, 134, 135, 141, 147, 153, 174 … | -0.012 [-0.123, +0.101] (n 40 games / 8 series) |
| top | current top ten (non-dev) | 10: 264, 306, 91, 507, 157, 454, 213, 55, 249, 19 | n 0 |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 4: 221, 842, 844, 1055 | +0.148 [+0.051, +0.229] (n 20 games / 4 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Trophy | -0.436 [-0.532, -0.340] (n 2 games / 2 series) |
| Slithery Fight | -0.408 [-0.686, -0.129] (n 2 games / 2 series) |
| Trauma | -0.330 [-0.532, -0.129] (n 2 games / 2 series) |
| Autarky | -0.262 [-0.659, +0.135] (n 3 games / 3 series) |
| Australia | -0.143 [-0.336, +0.088] (n 5 games / 5 series) |
| Maze | -0.129 [-0.129, -0.129] (n 1 games / 1 series) |
| weakhold | -0.101 [-0.597, +0.395] (n 2 games / 2 series) |
| Default | -0.098 [-0.495, +0.299] (n 3 games / 3 series) |
| Portals | +0.037 [-0.293, +0.368] (n 3 games / 3 series) |
| Devil | +0.064 [-0.340, +0.468] (n 2 games / 2 series) |
| Stripes | +0.101 [-0.182, +0.319] (n 4 games / 4 series) |
| Queen Of Spades | +0.197 [-0.496, +0.889] (n 2 games / 2 series) |
| Islands | +0.278 [+0.101, +0.454] (n 4 games / 4 series) |
| Around UNSW | +0.315 [+0.058, +0.572] (n 3 games / 3 series) |
| Prisoners Dilemma | +0.403 [+0.403, +0.403] (n 1 games / 1 series) |
| ↳ 10 dragons | +0.403 [+0.403, +0.403] (n 1 games / 1 series) |
| Schooltime | +0.504 [+0.504, +0.504] (n 1 games / 1 series) |
| ↳ open4 | +0.504 [+0.504, +0.504] (n 1 games / 1 series) |

## Drift (all our ranked games)

- Last 7 days: -0.028 [-0.047, -0.007] (n 1822 games / 372 series); the 7 days before: +0.094 [-0.082, +0.264] (n 29 games / 6 series).
- submission 14585: -0.022 [-0.048, +0.002] (n 1095 games / 221 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 17388: +0.008 [-0.066, +0.084] (n 130 games / 26 series)
- submission 17530: -0.054 [-0.128, +0.023] (n 120 games / 24 series)
- submission 17791: +0.041 [-0.053, +0.140] (n 65 games / 13 series)
- submission 10473: +0.117 [+0.002, +0.230] (n 59 games / 13 series)
- submission 16979: -0.211 [-0.327, -0.082] (n 44 games / 9 series)
- submission 13010: -0.185 [-0.326, -0.034] (n 40 games / 8 series)
- submission 17940: -0.012 [-0.123, +0.101] (n 40 games / 8 series)
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

