# C1-E status — field pace targets (GLM 5.3, session 29 Sep 2026)

**Delivered, then extended on director request (per-map targets, spatial/churn stats, live bed maps, and three
map-opening specs).** Files, all current:

| deliverable | what |
|---|---|
| `docs/analysis/C1-pace-targets.md` | per-map × cohort tables (pace, economy/survival, relative & space, churn), winner−loser and team7−band gaps, covariates, live-bed-map section, reading, caveats |
| `game_stats/field_pace_targets.json` | the medians the sweeps consume: per-map × cohort; `_class_descriptive` (not a target), `_winner_loser_gap_top30`, `_team7_minus_band`, `_autoscrim_covariate`, `_side_check`, `_meta` |
| `game_stats/live_beds.json` | reconstructed live bed maps per layout (`map_hash`): cells + empirical spawn rates |
| `docs/analysis/C1-E-schooltime-spec.md` | (a) the Schooltime swarm opening from ten top-ten wins |
| `docs/analysis/C1-E-qos-trauma-specs.md` | (b) QoS land-grab + (c) Trauma late-compounding specs |
| `tools/analysis/c1e_pace.py`, `c1e_beds.py`, `c1e_schooltime.py`, `c1e_qos_trauma.py` | re-derive everything |
| `build/c1e/` | decoded replays, frames cache, feature batches, anatomy dumps |

## Round 2 changes (director: per-map not per-class; spatial + churn; Schooltime spec)

- **Class targets demoted**: `class_compact`/`class_open` moved out of the sweep JSON into `_class_descriptive`;
  MD class sections labelled descriptive-only. Reason on record: a class target held the bot back on Schooltime
  (top-10 medians span 5–8 units on PD to ~60 on Slithery; Schooltime's top-10 game is 41 units inside an
  open-class median of ~15).
- **Added per cohort and map**: units/total shares, territory r50/r100/r250, seen/enclosed/reach, contact,
  splits by window + splits/100dt, newborn deaths ≤10r, peak units. Headlines in the reading (lines 11–12):
  QoS is the only territory map (top 10: 74 % r100 → 92 % r250 vs band 49 %); a third of newborns die ≤10r in
  every cohort; the 64-dragon cap is hit by everyone on Slithery and by the top 10 on Schooltime; Schooltime
  production is a r50–100 flywheel (top-10 54 splits in that window vs band 11).
- **Live bed maps (new fact)**: live replay map texts carry no TILE spawn fields — the F1 bed features
  (density/bed-territory/EPG) are NaN on corpus replays, and walls/portals match local files exactly while beds
  do not: Schooltime 444 live vs 326 local, Slithery 497 vs 339, QoS 472 vs 442, Devil 176 vs 174, PD has four
  layouts (88/88/76/76); Autarky/Default/Portals/Trauma/Trophy match. Fixtures on Schooltime/Slithery train on a
  poorer economy than the field plays. Reconstructed per-layout cells + rates: `game_stats/live_beds.json`
  (`tools/analysis/c1e_beds.py`, all 2,393 ranked games).
- **(a) Schooltime spec**: ten top-ten wins (5 swarm: 70×2, 306×2, 91). The loop: r0 split 4→2+2 ×3 starters →
  6 workers travel to bed clusters (first pearl ~r21) → patrol ~5×5 around a bed, move every turn → split at
  length 4, always 2+2 → child stays within ~4–10 cells, claims nearest unclaimed bed → 8/20/31/48 units at
  r50/60/70/80, cap 64 by r90–110, 200–300 pearls in r50–100, ~50 % of 444 beds covered, crowns none before r100.
  Portal coverage (11/12 pairs by r100) emerges from bed spread — beds are not portal-adjacent (4 vs 5 baseline);
  transits optional (team 91 won with 6). Body avoidance is structural: 75 %+ dragons len ≤2, nearest ally 2 cells,
  body cells ≤4.5 % of map, churn accepted (3–28 newborn deaths/100 births; 16 invalid deaths in a rank-2 win).
- **(b) QoS**: steady 3 splits/decade, children claim across the midline (band parks at 49 %; top 10 reach 92 %
  by r250), h2h is the leading death cause; team 7 already matches headcount (12 vs 11) — our heads stay home.
- **(c) Trauma**: 2→4 units at r0, flat till r40, 18.5 at r100 then **46 at r200** — the r100 gap understates the
  lever; 97 of 110 deaths are engine-invalid (boxed in corridors) and the winners accept the churn; territory
  cannot be held (50/50 for everyone). Team 7's collapse map: 6 units at r100, 7 splits.

## Round 1 (unchanged, still true)

Population: all ranked completed games at run time (2,393 games / 4,786 side-games; header records index lines +
newest `fetched_at`). Extraction: F1 feature lab unchanged over gzip-staged copies (`build/c1e/decoded/`), four
batches in `build/c1e/features-00{0..3}`, frames cached (incremental). **macOS gotcha:** the F1 CLI's
ProcessPoolExecutor dies with BrokenProcessPool (spawn children killed in this sandbox); use
`build/c1e/drv.py` (fork start method) — 2,393 games in ~7 min at `--jobs 10`, pandas venv `~/.venvs/bc122`.
Validation: units/total at r100 match the independent vendored decoder exactly; series pearls 0–99 == vendored
cumulative pearls at r100 (spot games 78 = 78, plus 4,786-row 1e-6 check); by-r100 counters are rounds 0–99
(F1's `pearls@100`-style checkpoints include round-100 events — don't mix conventions).

## Not done / next

- Unranked games still undecoded (frames cache makes the A2 pass incremental).
- Nothing committed (commit set: the four `tools/analysis/c1e_*.py`, three docs, two `game_stats/` JSONs,
  `claude/c1-e-status.md`).
- F1 lab follow-up for its owner: teach `frame.terrain`/density/EPG to take reconstructed beds for live replays
  (keyed by `map_hash` against `live_beds.json`) — then bed-territory/EPG become computable on the corpus.
- Then A2 proper (the coverage atlas), per the C1-E prompt.
