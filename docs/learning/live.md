# Live monitor (Live ops, lane Daichi)

Generated 2026-10-04 23:52 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 650 ladder snapshots (latest 2026-10-04 23:47:49+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261004T2352Z-2627f49c.json.gz` sha256 `2627f49cfac66dbd…` (4392 games with their snapshot ids, 650 snapshots, index sha `d5ee7935d7ad`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **14585** (carthage-05-free-sprint; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **1055**, W-L-D 525-530-0; score − E -0.022 [-0.047, +0.003] (n 1055 games / 213 series).
- First 40 ranked after first sighting: score − E -0.017 [-0.106, +0.065] (n 40 games / 10 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.083 [-0.178, -0.004] (n 40 games / 8 series) — **below −0.08 with 95th pct < 0**; percentile among the submission's own 1016 rolling 40-game windows: 0.263 (D-065 §B).
- Elo now 1719 (rank 91); 24 h ago 1714; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 1280.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 83: 11, 15, 28, 30, 45, 46, 52, 64, 71, 74, 78, 91, 98, 104, 133, 134, 135, 141, 147, 174 … | -0.026 [-0.052, -0.001] (n 957 games / 193 series) |
| top | current top ten (non-dev) | 10: 264, 952, 306, 454, 91, 213, 507, 842, 55, 566 | +0.051 [-0.036, +0.140] (n 60 games / 12 series) |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | +0.171 [+0.043, +0.299] (n 15 games / 3 series) |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 44: 15, 30, 46, 55, 64, 71, 87, 98, 134, 135, 174, 178, 196, 217, 221, 258, 262, 280, 306, 312 … | +0.108 [+0.077, +0.139] (n 458 games / 92 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Schooltime | -0.481 [-0.515, -0.445] (n 73 games / 73 series) |
| ↳ open4 | -0.513 [-0.552, -0.473] (n 36 games / 36 series) |
| ↳ template | -0.450 [-0.502, -0.392] (n 37 games / 37 series) |
| weakhold | -0.337 [-0.419, -0.260] (n 66 games / 66 series) |
| Trauma | -0.219 [-0.302, -0.123] (n 66 games / 66 series) |
| Prisoners Dilemma | -0.119 [-0.215, -0.012] (n 60 games / 60 series) |
| ↳ 10 dragons | -0.088 [-0.226, +0.060] (n 31 games / 31 series) |
| ↳ template | -0.153 [-0.293, -0.003] (n 29 games / 29 series) |
| Portals | -0.100 [-0.198, -0.012] (n 69 games / 69 series) |
| Around UNSW | -0.091 [-0.200, +0.015] (n 56 games / 56 series) |
| Slithery Fight | -0.077 [-0.173, +0.024] (n 59 games / 59 series) |
| Stripes | -0.058 [-0.163, +0.046] (n 61 games / 61 series) |
| Australia | -0.034 [-0.144, +0.078] (n 51 games / 51 series) |
| Autarky | +0.015 [-0.080, +0.110] (n 63 games / 63 series) |
| Maze | +0.038 [-0.064, +0.136] (n 66 games / 66 series) |
| Trophy | +0.096 [-0.004, +0.189] (n 66 games / 66 series) |
| Default | +0.107 [+0.004, +0.212] (n 56 games / 56 series) |
| Islands | +0.134 [+0.046, +0.222] (n 59 games / 59 series) |
| Devil | +0.195 [+0.103, +0.285] (n 66 games / 66 series) |
| Queen Of Spades | +0.332 [+0.269, +0.390] (n 65 games / 65 series) |
| Tower Defense | +0.377 [+0.312, +0.435] (n 53 games / 53 series) |

## Drift (all our ranked games)

- Last 7 days: -0.024 [-0.048, -0.004] (n 1412 games / 290 series); the 7 days before: n 0.
- submission 14585: -0.022 [-0.047, +0.003] (n 1055 games / 213 series)
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

