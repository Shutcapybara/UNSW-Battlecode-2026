# avery-v08-crown-race

**Lineage:** Avery · **Parent:** `bots/avery-v07-compact-production` ·
**Status:** promoted over v07.

## Hypothesis

v06/v07 still lose the round-500 longest-dragon race to ouroboros-class
endgames on compact maps (stronghold 17v48 / 10v44, devil 17v33 / 19v30;
on trauma no dragon reaches len 8 so no crown ever volunteers — our r500
longest is 4–11). The field-proven ouroboros-v10 / tew-ladder schedule banks
earlier and feeds much harder. Avery's strict **singular** volunteer rule
(v05+) already prevents v04's mass-volunteer economy freeze, so the banking
schedule can move to the proven envelope without re-introducing the freeze.

## Changes vs v07

- `crown_start` 300 → **220**, `crown_min_len` 8 → **5**
- `feed_start` 410 → **400**, `feed_max_len` 10 → **20**,
  `feed_range` 16 → **30**, `crown_demote` 2 → **3**
  (all ouroboros-v10's tuned values; a len-20 corpse deposits 10 pearls,
  and range 30 lets the whole team deliver)

## Measured results

Native gauntlet (avery-gauntlet.toml, both sides, 11 maps, 132 games), run
`experiment_data/avery-v08-crown-race_20260925122644396505`.
**100–31–1 (76.1%)**, runtime_faults=0. Gauntlet-5 only: **89–20–1 (81.4%)**
(v07: 84–25–1, v06: 79–30–1). No map regressed.

| Opponent | v08 | v07 |
|---|---|---|
| kraken-v04 | 20–1–1 | 17–4–1 |
| fry-v14 | 19–3 | 19–3 |
| hunter-v14 | 18–4 | 17–5 |
| ouroboros-v10 | 17–5 | 17–5 |
| hunter-v20 | 15–7 | 14–8 |
| tew-v12 | 11–11 | 10–12 |

| Map | v08 | v07 |
|---|---|---|
| stronghold | 10–2 | 8–4 |
| big_empty | 9–3 | 7–5 |
| default | 12–0 | 11–1 |
| devil | 11–1 | 10–2 |
| trauma | 5–7 | 5–7 (untouched) |

Crown banking visibly works: big_empty crowns now reach 55 (was 45),
stronghold 32 (was 17). Remaining r500 race losses: big_empty-B 55v61,
stronghold-A 32v52, trauma everywhere (our longest 4–12).

## Diagnostics and remaining uncertainties

- **trauma (5–7) is now the worst map**, and it is not a crown problem:
  the team eats ~37 pearls in 500 rounds while ouro eats ~426 — exploration
  failure in the kelp maze (all dragons orbit the start corner; traced).
  Attacked in v09.
- big_empty vs hunter-v20-A: 34v53 with total 185v844 — hunter dominates the
  open-map economy there; watch after v09's exploration change.
- Arena side-A asymmetry persists from v07 (uninvestigated).
- Native evidence only; no sandbox/judge CPU validation yet
  (runtime_faults=0 over 132 games).
