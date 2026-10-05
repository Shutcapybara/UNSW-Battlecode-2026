# Live monitor (Live ops, lane Daichi)

Generated 2026-10-05 02:51 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 667 ladder snapshots (latest 2026-10-05 02:48:22+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261005T0251Z-8c32adc5.json.gz` sha256 `8c32adc53d455d55…` (4547 games with their snapshot ids, 667 snapshots, index sha `0af4d893bf93`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **16979** (asahi-05-kz12-k16; fingerprint `?`); first seen in the corpus 2026-10-04 17:42:35.009000+00:00.
- Ranked games since first seen: **10**, W-L-D 3-7-0; score − E -0.439 [-0.522, -0.357] (n 10 games / 2 series).
- First 40 ranked after first sighting: score − E -0.439 [-0.522, -0.357] (n 10 games / 2 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E -0.439 [-0.522, -0.357] (n 10 games / 2 series).
- Elo now 1643 (rank 110); 24 h ago 1699; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 86.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 85: 11, 15, 28, 30, 45, 46, 52, 64, 71, 74, 78, 91, 98, 104, 133, 134, 135, 141, 147, 174 … | -0.439 [-0.522, -0.357] (n 10 games / 2 series) |
| top | current top ten (non-dev) | 10: 306, 91, 264, 454, 55, 213, 952, 507, 842, 87 | n 0 |
| style | one per style (Data top-teams.md v1, 13:55Z): 306 invalid-move cull, 264 suicide cull + fast portals, 213 queen keeper, 952 split-heavy sonar-silent | 4: 306, 264, 213, 952 | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 0:  | n 0 |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Around UNSW | -0.757 [-0.757, -0.757] (n 1 games / 1 series) |
| Australia | -0.757 [-0.757, -0.757] (n 1 games / 1 series) |
| Maze | -0.757 [-0.757, -0.757] (n 1 games / 1 series) |
| Schooltime | -0.722 [-0.722, -0.722] (n 1 games / 1 series) |
| ↳ open4 | -0.722 [-0.722, -0.722] (n 1 games / 1 series) |
| Trauma | -0.722 [-0.722, -0.722] (n 1 games / 1 series) |
| Default | -0.722 [-0.722, -0.722] (n 1 games / 1 series) |
| Tower Defense | -0.239 [-0.722, +0.243] (n 2 games / 2 series) |
| Stripes | +0.243 [+0.243, +0.243] (n 1 games / 1 series) |
| Islands | +0.278 [+0.278, +0.278] (n 1 games / 1 series) |

## Drift (all our ranked games)

- Last 7 days: -0.027 [-0.051, -0.008] (n 1462 games / 300 series); the 7 days before: n 0.
- submission 14585: -0.022 [-0.048, +0.002] (n 1095 games / 221 series)
- submission 14265: -0.034 [-0.111, +0.045] (n 138 games / 29 series)
- submission 10473: +0.117 [+0.002, +0.230] (n 59 games / 13 series)
- submission 13010: -0.185 [-0.326, -0.034] (n 40 games / 8 series)
- submission 11398: -0.031 [-0.131, +0.082] (n 32 games / 7 series)
- submission 11969: -0.046 [-0.150, +0.088] (n 31 games / 7 series)
- submission 11244: +0.025 [-0.130, +0.180] (n 20 games / 4 series)
- submission 12851: +0.002 [-0.183, +0.251] (n 14 games / 4 series)
- submission 12440: -0.204 [-0.310, -0.099] (n 10 games / 2 series)
- submission 16979: -0.439 [-0.522, -0.357] (n 10 games / 2 series)
- submission 13086: -0.240 [-0.487, -0.092] (n 8 games / 2 series)
- submission 12728: -0.052 [-0.052, -0.052] (n 5 games / 1 series)

## Errors and timeouts

- Not yet measured for ranked games (needs a replay-side fault read; the hub verifies faults only for games it requests). Requested battles report faults per job in `hub-state/battles/`.
- Ranked games without an Elo expectation (no snapshot): 45.

