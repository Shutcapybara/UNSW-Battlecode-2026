# Live monitor (Live ops, lane Daichi)

Generated 2026-10-04 17:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 619 ladder snapshots (latest 2026-10-04 17:50:22+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261004T1751Z-6f55b653.json.gz` sha256 `6f55b653a7e61f55…` (4103 games with their snapshot ids, 619 snapshots, index sha `3bfc5a02650e`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **14585** (carthage-05-free-sprint; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **965**, W-L-D 484-481-0; score − E -0.019 [-0.044, +0.008] (n 965 games / 195 series).
- First 40 ranked after first sighting: score − E -0.017 [-0.106, +0.065] (n 40 games / 10 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.030 [-0.151, +0.101] (n 40 games / 8 series).
- Elo now 1725 (rank 81); 24 h ago 1732; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 1135.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 82: 11, 15, 28, 30, 45, 46, 52, 64, 71, 74, 78, 91, 98, 104, 133, 134, 141, 147, 174, 178 … | -0.022 [-0.051, +0.008] (n 907 games / 183 series) |
| top | current top ten (non-dev) | 10: 264, 91, 306, 213, 842, 507, 454, 55, 952, 946 | +0.051 [-0.036, +0.140] (n 60 games / 12 series) |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | +0.171 [+0.043, +0.299] (n 15 games / 3 series) |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 42: 15, 30, 46, 55, 64, 71, 87, 98, 134, 174, 178, 196, 217, 221, 258, 262, 280, 306, 312, 328 … | +0.112 [+0.078, +0.149] (n 423 games / 85 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Schooltime | -0.481 [-0.517, -0.439] (n 62 games / 62 series) |
| ↳ open4 | -0.519 [-0.564, -0.474] (n 29 games / 29 series) |
| ↳ template | -0.447 [-0.502, -0.384] (n 33 games / 33 series) |
| weakhold | -0.329 [-0.405, -0.241] (n 62 games / 62 series) |
| Trauma | -0.189 [-0.283, -0.085] (n 57 games / 57 series) |
| Prisoners Dilemma | -0.107 [-0.205, +0.000] (n 56 games / 56 series) |
| ↳ 10 dragons | -0.070 [-0.215, +0.081] (n 28 games / 28 series) |
| ↳ template | -0.145 [-0.294, +0.002] (n 28 games / 28 series) |
| Portals | -0.092 [-0.189, +0.009] (n 64 games / 64 series) |
| Slithery Fight | -0.089 [-0.191, +0.021] (n 56 games / 56 series) |
| Around UNSW | -0.068 [-0.168, +0.038] (n 53 games / 53 series) |
| Stripes | -0.040 [-0.152, +0.071] (n 58 games / 58 series) |
| Australia | -0.034 [-0.149, +0.077] (n 47 games / 47 series) |
| Autarky | +0.020 [-0.086, +0.119] (n 55 games / 55 series) |
| Maze | +0.054 [-0.055, +0.169] (n 60 games / 60 series) |
| Default | +0.077 [-0.028, +0.180] (n 53 games / 53 series) |
| Trophy | +0.087 [-0.011, +0.191] (n 61 games / 61 series) |
| Islands | +0.099 [+0.005, +0.195] (n 53 games / 53 series) |
| Devil | +0.188 [+0.084, +0.284] (n 59 games / 59 series) |
| Queen Of Spades | +0.320 [+0.255, +0.385] (n 60 games / 60 series) |
| Tower Defense | +0.367 [+0.299, +0.429] (n 49 games / 49 series) |

## Drift (all our ranked games)

- Last 7 days: -0.022 [-0.044, +0.000] (n 1322 games / 272 series); the 7 days before: n 0.
- submission 14585: -0.019 [-0.044, +0.008] (n 965 games / 195 series)
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

