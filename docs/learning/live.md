# Live monitor (Live ops, lane Daichi)

Generated 2026-10-04 15:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 607 ladder snapshots (latest 2026-10-04 15:42:54+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261004T1551Z-a6195606.json.gz` sha256 `a6195606f4c4bb8f…` (4034 games with their snapshot ids, 607 snapshots, index sha `4a98e67c3d8e`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **14585** (carthage-05-free-sprint; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **940**, W-L-D 472-468-0; score − E -0.017 [-0.044, +0.009] (n 940 games / 190 series).
- First 40 ranked after first sighting: score − E -0.017 [-0.106, +0.065] (n 40 games / 10 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E +0.026 [-0.108, +0.169] (n 40 games / 8 series).
- Elo now 1722 (rank 85); 24 h ago 1733; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 1099.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 82: 11, 15, 28, 30, 45, 46, 52, 64, 71, 74, 78, 91, 98, 133, 134, 141, 147, 174, 178, 187 … | -0.015 [-0.043, +0.012] (n 877 games / 177 series) |
| top | current top ten (non-dev) | 10: 91, 306, 213, 264, 507, 842, 19, 952, 87, 454 | +0.035 [-0.059, +0.135] (n 50 games / 10 series) |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | +0.171 [+0.043, +0.299] (n 15 games / 3 series) |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 43: 15, 30, 46, 55, 64, 71, 87, 98, 134, 174, 178, 196, 217, 221, 258, 262, 280, 306, 312, 328 … | +0.111 [+0.076, +0.147] (n 428 games / 86 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Schooltime | -0.479 [-0.515, -0.439] (n 60 games / 60 series) |
| ↳ open4 | -0.519 [-0.568, -0.474] (n 28 games / 28 series) |
| ↳ template | -0.443 [-0.501, -0.375] (n 32 games / 32 series) |
| weakhold | -0.342 [-0.420, -0.256] (n 61 games / 61 series) |
| Trauma | -0.207 [-0.307, -0.096] (n 54 games / 54 series) |
| Slithery Fight | -0.091 [-0.190, +0.014] (n 54 games / 54 series) |
| Prisoners Dilemma | -0.090 [-0.196, +0.012] (n 54 games / 54 series) |
| ↳ 10 dragons | -0.050 [-0.216, +0.116] (n 27 games / 27 series) |
| ↳ template | -0.129 [-0.283, +0.015] (n 27 games / 27 series) |
| Portals | -0.085 [-0.190, +0.017] (n 61 games / 61 series) |
| Around UNSW | -0.077 [-0.194, +0.035] (n 52 games / 52 series) |
| Australia | -0.034 [-0.149, +0.077] (n 47 games / 47 series) |
| Stripes | -0.021 [-0.136, +0.093] (n 56 games / 56 series) |
| Autarky | +0.011 [-0.086, +0.105] (n 54 games / 54 series) |
| Maze | +0.054 [-0.055, +0.169] (n 60 games / 60 series) |
| Trophy | +0.081 [-0.021, +0.181] (n 60 games / 60 series) |
| Islands | +0.092 [-0.000, +0.190] (n 52 games / 52 series) |
| Default | +0.115 [+0.005, +0.222] (n 50 games / 50 series) |
| Devil | +0.184 [+0.078, +0.280] (n 58 games / 58 series) |
| Queen Of Spades | +0.318 [+0.247, +0.385] (n 59 games / 59 series) |
| Tower Defense | +0.364 [+0.293, +0.429] (n 48 games / 48 series) |

## Drift (all our ranked games)

- Last 7 days: -0.021 [-0.044, +0.002] (n 1297 games / 267 series); the 7 days before: n 0.
- submission 14585: -0.017 [-0.044, +0.009] (n 940 games / 190 series)
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

