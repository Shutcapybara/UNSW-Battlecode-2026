# Live monitor (Live ops, lane Daichi)

Generated 2026-10-04 13:53 UTC by `tools/daichi/live_monitor.py` from the corpus index (team 7 games, replay-header attribution) and 596 ladder snapshots (latest 2026-10-04 13:45:58+00:00). Population: **ranked** games only unless stated. Statistic: score − Elo expectation per game; interval = whole-series cluster bootstrap, 1,000 resamples, seed 7, 5th/95th percentile. Corpus lag: games appear when the collector fetches them (minutes to hours).

Frozen inputs (D-051 §4): `docs/learning/live-inputs/20261004T1353Z-6578d155.json.gz` sha256 `6578d15514fce301…` (3678 games with their snapshot ids, 596 snapshots, index sha `9f0a8de27ab2`). Expectations use the last snapshot at or before the game; a game before the first snapshot gets none.

## Incumbent

- Live submission **14585** (carthage-05-free-sprint; fingerprint `?`); first seen in the corpus 2026-10-02 04:22:43.966000+00:00.
- Ranked games since first seen: **849**, W-L-D 432-417-0; score − E -0.013 [-0.041, +0.014] (n 849 games / 172 series).
- First 40 ranked after first sighting: score − E -0.052 [-0.204, +0.071] (n 40 games / 10 series). Old absolute screen (mean < −0.08 and 95th pct < 0): **not met** — superseded by D-052 §B (difference vs the replaced submission's last 120, our rating fixed at activation); that look is computed by `tools/daichi/rollback_d052.py` → `docs/learning/rollback-d052.md` §3 and binds only a candidate Live ops promoted.
- Rolling last 40 ranked (drift signal, not a rollback trigger): score − E +0.027 [-0.066, +0.114] (n 40 games / 8 series).
- Elo now 1721 (rank 78); 24 h ago 1742; 7 d ago n/a (no snapshot).
- Unranked games of the incumbent in the window (exposure only, not scored here): 839.

## Rosters (ranked, incumbent only)

| roster | definition | teams | score − E |
|---|---|---|---|
| band | teams met in ranked, last 48 h | 83: 11, 15, 28, 30, 40, 45, 46, 52, 55, 64, 71, 74, 78, 91, 98, 133, 134, 141, 147, 174 … | -0.013 [-0.041, +0.016] (n 841 games / 170 series) |
| top | current top ten (non-dev) | 10: 91, 306, 264, 213, 507, 842, 952, 19, 566, 454 | +0.035 [-0.075, +0.145] (n 45 games / 9 series) |
| style | one per style — awaits Data's top-teams pages | 0:  | n 0 |
| regression | opponents with ≥ 5 ranked games and mean score − E > 0 | 42: 15, 30, 40, 46, 55, 64, 71, 98, 104, 134, 174, 178, 196, 217, 258, 262, 280, 306, 312, 328 … | +0.108 [+0.072, +0.143] (n 397 games / 80 series) |

## Per map (ranked, incumbent)

Schooltime and Prisoners Dilemma are also split by layout variant (D-052 §E; variant from the replay map_hash, Shenzhen unit 7). Variant rows are subsets of their map row, not extra games.

| map | score − E |
|---|---|
| Schooltime | -0.478 [-0.519, -0.430] (n 51 games / 51 series) |
| ↳ open4 | -0.515 [-0.565, -0.466] (n 27 games / 27 series) |
| ↳ template | -0.436 [-0.507, -0.353] (n 24 games / 24 series) |
| weakhold | -0.353 [-0.430, -0.266] (n 59 games / 59 series) |
| Trauma | -0.209 [-0.312, -0.092] (n 51 games / 51 series) |
| Prisoners Dilemma | -0.106 [-0.217, +0.006] (n 47 games / 47 series) |
| ↳ 10 dragons | -0.044 [-0.202, +0.109] (n 23 games / 23 series) |
| ↳ template | -0.166 [-0.308, -0.010] (n 24 games / 24 series) |
| Portals | -0.096 [-0.219, +0.018] (n 53 games / 53 series) |
| Australia | -0.080 [-0.200, +0.035] (n 40 games / 40 series) |
| Slithery Fight | -0.074 [-0.188, +0.038] (n 52 games / 52 series) |
| Around UNSW | -0.059 [-0.174, +0.063] (n 47 games / 47 series) |
| Stripes | -0.009 [-0.128, +0.110] (n 50 games / 50 series) |
| Autarky | +0.035 [-0.075, +0.134] (n 48 games / 48 series) |
| Trophy | +0.076 [-0.029, +0.174] (n 53 games / 53 series) |
| Maze | +0.090 [-0.028, +0.201] (n 54 games / 54 series) |
| Default | +0.109 [+0.001, +0.221] (n 44 games / 44 series) |
| Islands | +0.120 [+0.030, +0.213] (n 50 games / 50 series) |
| Devil | +0.192 [+0.087, +0.289] (n 52 games / 52 series) |
| Queen Of Spades | +0.305 [+0.232, +0.374] (n 55 games / 55 series) |
| Tower Defense | +0.395 [+0.338, +0.455] (n 43 games / 43 series) |

## Drift (all our ranked games)

- Last 7 days: -0.019 [-0.042, +0.005] (n 1206 games / 249 series); the 7 days before: n 0.
- submission 14585: -0.013 [-0.041, +0.014] (n 849 games / 172 series)
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
- Ranked games without an Elo expectation (no snapshot): 40.

