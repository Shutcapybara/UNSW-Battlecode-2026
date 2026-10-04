# Live monitor (Live ops, lane Daichi)

Generated 2026-10-04 21:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 638 ladder snapshots (latest 2026-10-04 21:41:52+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261004T2151Z-c0d7fa30.json.gz` sha256 `c0d7fa30433a5e32…` (4281 games with their snapshot ids, 638 snapshots, index sha `c38148ba6730`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **14585** (carthage-05-free-sprint; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **1020**, W-L-D 509-511-0; score − E -0.021 [-0.046, +0.005] (n 1020 games / 206 series).
- First 40 ranked after first sighting: score − E -0.017 [-0.106, +0.065] (n 40 games / 10 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.052 [-0.188, +0.096] (n 40 games / 8 series).
- Elo now 1720 (rank 86); 24 h ago 1735; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 1224.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 80: 11, 15, 28, 30, 45, 46, 52, 64, 71, 74, 78, 91, 98, 104, 133, 134, 135, 141, 147, 174 … | -0.028 [-0.055, +0.000] (n 922 games / 186 series) |
| top | current top ten (non-dev) | 10: 264, 55, 306, 507, 213, 91, 454, 952, 842, 87 | +0.050 [-0.040, +0.137] (n 65 games / 13 series) |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | +0.171 [+0.043, +0.299] (n 15 games / 3 series) |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 44: 15, 30, 46, 55, 64, 71, 87, 98, 134, 135, 174, 178, 196, 217, 221, 258, 262, 280, 306, 312 … | +0.109 [+0.075, +0.144] (n 448 games / 90 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Schooltime | -0.482 [-0.516, -0.446] (n 69 games / 69 series) |
| ↳ open4 | -0.517 [-0.556, -0.480] (n 34 games / 34 series) |
| ↳ template | -0.448 [-0.503, -0.390] (n 35 games / 35 series) |
| weakhold | -0.336 [-0.418, -0.258] (n 64 games / 64 series) |
| Trauma | -0.197 [-0.296, -0.102] (n 62 games / 62 series) |
| Prisoners Dilemma | -0.123 [-0.225, -0.014] (n 58 games / 58 series) |
| ↳ 10 dragons | -0.103 [-0.249, +0.046] (n 30 games / 30 series) |
| ↳ template | -0.145 [-0.294, +0.002] (n 28 games / 28 series) |
| Portals | -0.100 [-0.203, +0.001] (n 67 games / 67 series) |
| Slithery Fight | -0.077 [-0.173, +0.024] (n 59 games / 59 series) |
| Around UNSW | -0.077 [-0.183, +0.038] (n 54 games / 54 series) |
| Stripes | -0.048 [-0.153, +0.065] (n 59 games / 59 series) |
| Australia | -0.034 [-0.144, +0.078] (n 51 games / 51 series) |
| Autarky | +0.001 [-0.102, +0.092] (n 61 games / 61 series) |
| Maze | +0.038 [-0.061, +0.149] (n 64 games / 64 series) |
| Default | +0.097 [-0.009, +0.198] (n 55 games / 55 series) |
| Trophy | +0.103 [+0.007, +0.200] (n 64 games / 64 series) |
| Islands | +0.109 [+0.017, +0.200] (n 55 games / 55 series) |
| Devil | +0.199 [+0.103, +0.291] (n 64 games / 64 series) |
| Queen Of Spades | +0.324 [+0.250, +0.385] (n 62 games / 62 series) |
| Tower Defense | +0.373 [+0.306, +0.434] (n 52 games / 52 series) |

## Drift (all our ranked games)

- Last 7 days: -0.024 [-0.047, -0.002] (n 1377 games / 283 series); the 7 days before: n 0.
- submission 14585: -0.021 [-0.046, +0.005] (n 1020 games / 206 series)
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

