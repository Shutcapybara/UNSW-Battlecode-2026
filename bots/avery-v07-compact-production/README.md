# avery-v07-compact-production

**Lineage:** Avery · **Parent:** `bots/avery-v06-late-feed` (protocol.py
unchanged, including the v06 None-command port) · **Status:** promoted over
v06 (pending v08 crown-race measurement on top).

## Hypothesis

v06's worst leak is early **elimination on small maps**, not the crown race:
arena 3–8–1 with all eight losses by rounds 54–104, plus mid-game wipes on
default_small (5), trophy (5) and Colosseum (3). Arena per-round series in
the v06 run show the mechanism: enemy-kill attrition is near-even, but
hunter-v20 splits whenever length ≥ 4 up to the 64-unit limit and tew-v12's
ladder splits unconditionally (hunter: 89 splits by r78 vs avery 33; tew
sustains 21+ units). Avery's production gates — `team_target_small=24`,
`split_crowd_max=8`, `split_danger_max=0.3` — were tuned for big-map swarm
spacing and lose the production race on ≤600-cell maps.

## Changes vs v06 (small maps only, NC ≤ `small_map_cells=600`)

- `team_target_small` 24 → **44** (hunter/tew sustain 20–26 units on arena).
- `split_crowd_max` 8 → **14** (`split_crowd_max_small`; small maps are
  always dense).
- `split_danger_max` 0.3 → **0.6** (`split_danger_max_small`; splitting under
  fire is production insurance — the child is born at the tail, usually off
  the threat axis).
- Trace counters for split-gate rejections (`SPLIT-BLOCKED` lines when
  `/tmp/avery-trace-on` exists; diagnostics only).

Maps affected by the threshold: arena (121), Colosseum (256),
default_small (256), devil (512). Trophy (625) deliberately excluded.

## Measured results

Native gauntlet (avery-gauntlet.toml: gauntlet-5 + tew-v12-mid-support,
both sides, 11 maps, 132 games), run
`experiment_data/avery-v07-compact-production_20260925121511670436`
(run id in its manifest.json). Opponent sources hash-verified unchanged
against the v06 run's frozen manifest before comparison.

**94–37–1 (71.6%)**, runtime_faults=0. vs v06's 89–42–1: **+5 net**.
Gauntlet-5 only (excl. tew): **84–25–1 (76.4%)** vs v06's 79–30–1 (72.3%).

| Opponent | v07 | v06 |
|---|---|---|
| fry-v14 | 19–3 | 18–4 |
| hunter-v14 | 17–5 | 16–6 |
| hunter-v20 | 14–8 | 12–10 |
| kraken-v04 | 17–4–1 | 17–4–1 |
| ouroboros-v10 | 17–5 | 16–6 |
| tew-v12 | 10–12 | 10–12 |

| Map | v07 | v06 |
|---|---|---|
| arena | **7–4–1** | 3–8–1 |
| devil | **10–2** | 8–4 |
| Colosseum | 8–4 | 9–3 (regression, −1) |
| others | unchanged | |

Arena production responded as predicted: wins now come with 13–17 surviving
units and 41–106 splits (v06: 20–56 splits). Losses still show the opponent
out-producing (hunter-v14 159 splits vs our 106; hunter-v20-A 51 vs 22).

## Diagnostics and remaining uncertainties

- **Arena side-A asymmetry**: v07 is 4–1–1 as side B but 2–4 as side A on
  arena. In the side-A losses production collapses (22/50/20 splits vs 61–106
  when winning). Untested whether act-order (A moves first), start geometry
  or opponent side bias drives it. Next investigation target.
- Colosseum lost one game (9–3 → 8–4): small-sample noise or crowd-gate
  side effect; watch next run.
- trauma (5–7), stronghold (8–4), big_empty (7–5) r500 crown-race losses are
  unchanged — attacked separately in v08.
- All evidence is native; no sandbox/judge CPU validation done for avery yet
  (v07 run had runtime_faults=0 over 132 games).
- Trace hook: `/tmp/avery-trace-on` must NOT exist during benchmarking.
