# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 12:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 724 ladder snapshots (latest 2026-10-05 12:42:08+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T1251Z-09ca9563.json.gz` sha256 `09ca9563abfd2029…` (4842 games with their snapshot ids, 724 snapshots, index sha `d69292e07390`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **17388** (kenma-03-pocket-queen; fingerprint `?`); first seen in the corpus 2026-10-05 05:02:01.225000+00:00.
- Ranked games since first seen: **100**, W-L-D 53-47-0; score − E -0.007 [-0.106, +0.083] (n 100 games / 20 series).
- First 40 ranked after first sighting: score − E +0.092 [-0.061, +0.258] (n 40 games / 8 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.067 [-0.202, +0.067] (n 40 games / 8 series); percentile among the submission's own 61 rolling 40-game windows: 0.393 (D-065 §B).
- Elo now 1769 (rank 76); 24 h ago 1720; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 1.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 82: 11, 15, 22, 28, 30, 52, 64, 71, 78, 98, 104, 127, 133, 134, 135, 141, 147, 174, 187, 196 … | -0.007 [-0.106, +0.083] (n 100 games / 20 series) |
| top | current top ten (non-dev) | 10: 264, 306, 91, 507, 454, 55, 213, 842, 566, 258 | n 0 |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 7: 127, 133, 187, 347, 351, 456, 1015 | +0.158 [+0.052, +0.263] (n 55 games / 11 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| weakhold | -0.508 [-0.628, -0.387] (n 3 games / 3 series) |
| Prisoners Dilemma | -0.359 [-0.583, +0.014] (n 5 games / 5 series) |
| ↳ 10 dragons | -0.257 [-0.598, +0.085] (n 3 games / 3 series) |
| ↳ template | -0.511 [-0.576, -0.447] (n 2 games / 2 series) |
| Slithery Fight | -0.255 [-0.514, +0.036] (n 7 games / 7 series) |
| Around UNSW | -0.218 [-0.437, +0.055] (n 4 games / 4 series) |
| Trauma | -0.168 [-0.517, +0.196] (n 6 games / 6 series) |
| Trophy | -0.138 [-0.412, +0.113] (n 8 games / 8 series) |
| Tower Defense | -0.073 [-0.594, +0.389] (n 4 games / 4 series) |
| Autarky | -0.051 [-0.299, +0.172] (n 8 games / 8 series) |
| Default | -0.011 [-0.277, +0.271] (n 9 games / 9 series) |
| Queen Of Spades | +0.078 [-0.221, +0.380] (n 6 games / 6 series) |
| Australia | +0.117 [-0.205, +0.430] (n 5 games / 5 series) |
| Stripes | +0.131 [-0.234, +0.470] (n 6 games / 6 series) |
| Maze | +0.178 [-0.171, +0.507] (n 4 games / 4 series) |
| Portals | +0.192 [-0.041, +0.407] (n 11 games / 11 series) |
| Islands | +0.214 [+0.026, +0.393] (n 8 games / 8 series) |
| Devil | +0.262 [-0.029, +0.554] (n 3 games / 3 series) |
| Schooltime | +0.342 [+0.275, +0.410] (n 3 games / 3 series) |
| ↳ open4 | +0.301 [+0.223, +0.380] (n 2 games / 2 series) |
| ↳ template | +0.424 [+0.424, +0.424] (n 1 games / 1 series) |

## Drift (all our ranked games)

- Last 7 days: -0.030 [-0.050, -0.010] (n 1716 games / 351 series); the 7 days before: n 0.
- submission 14585: -0.022 [-0.048, +0.002] (n 1095 games / 221 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 17530: -0.054 [-0.128, +0.023] (n 120 games / 24 series)
- submission 17388: -0.007 [-0.106, +0.083] (n 100 games / 20 series)
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

