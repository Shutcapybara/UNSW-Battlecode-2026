# Live monitor (Live ops, lane Daichi)

Generated 2026-10-04 14:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 602 ladder snapshots (latest 2026-10-04 14:49:56+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261004T1451Z-aca38d40.json.gz` sha256 `aca38d40ebcc47bd…` (4011 games with their snapshot ids, 602 snapshots, index sha `90a55787821a`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **14585** (carthage-05-free-sprint; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **925**, W-L-D 464-461-0; score − E -0.018 [-0.044, +0.010] (n 925 games / 187 series).
- First 40 ranked after first sighting: score − E -0.017 [-0.106, +0.065] (n 40 games / 10 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E +0.027 [-0.103, +0.165] (n 40 games / 8 series).
- Elo now 1721 (rank 80); 24 h ago 1742; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 1091.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 84: 11, 15, 28, 30, 40, 45, 46, 52, 55, 64, 71, 74, 78, 91, 98, 133, 134, 141, 147, 174 … | -0.015 [-0.042, +0.011] (n 887 games / 179 series) |
| top | current top ten (non-dev) | 10: 264, 91, 306, 213, 507, 842, 19, 952, 87, 454 | +0.035 [-0.059, +0.135] (n 50 games / 10 series) |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | +0.171 [+0.043, +0.299] (n 15 games / 3 series) |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 42: 15, 30, 46, 55, 64, 71, 87, 98, 134, 174, 178, 196, 217, 258, 262, 280, 306, 312, 328, 440 … | +0.113 [+0.080, +0.149] (n 413 games / 83 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Schooltime | -0.478 [-0.517, -0.437] (n 58 games / 58 series) |
| ↳ open4 | -0.519 [-0.568, -0.474] (n 28 games / 28 series) |
| ↳ template | -0.440 [-0.502, -0.372] (n 30 games / 30 series) |
| weakhold | -0.342 [-0.420, -0.256] (n 61 games / 61 series) |
| Trauma | -0.207 [-0.307, -0.096] (n 54 games / 54 series) |
| Portals | -0.095 [-0.198, +0.014] (n 60 games / 60 series) |
| Prisoners Dilemma | -0.090 [-0.196, +0.012] (n 54 games / 54 series) |
| ↳ 10 dragons | -0.050 [-0.216, +0.116] (n 27 games / 27 series) |
| ↳ template | -0.129 [-0.283, +0.015] (n 27 games / 27 series) |
| Slithery Fight | -0.085 [-0.191, +0.026] (n 53 games / 53 series) |
| Around UNSW | -0.077 [-0.194, +0.035] (n 52 games / 52 series) |
| Australia | -0.044 [-0.154, +0.066] (n 46 games / 46 series) |
| Stripes | -0.021 [-0.136, +0.093] (n 56 games / 56 series) |
| Autarky | +0.022 [-0.075, +0.122] (n 53 games / 53 series) |
| Maze | +0.062 [-0.055, +0.178] (n 59 games / 59 series) |
| Trophy | +0.074 [-0.022, +0.179] (n 59 games / 59 series) |
| Islands | +0.103 [+0.002, +0.198] (n 51 games / 51 series) |
| Default | +0.119 [+0.023, +0.228] (n 48 games / 48 series) |
| Devil | +0.172 [+0.064, +0.268] (n 56 games / 56 series) |
| Queen Of Spades | +0.315 [+0.247, +0.385] (n 58 games / 58 series) |
| Tower Defense | +0.362 [+0.294, +0.424] (n 47 games / 47 series) |

## Drift (all our ranked games)

- Last 7 days: -0.022 [-0.045, +0.001] (n 1282 games / 264 series); the 7 days before: n 0.
- submission 14585: -0.018 [-0.044, +0.010] (n 925 games / 187 series)
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

