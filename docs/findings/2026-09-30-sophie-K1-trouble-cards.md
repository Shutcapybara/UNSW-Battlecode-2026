# K-1 Part 1 — trouble cards: what kills us on each pool map, and what loses the games

Lineage **sophie** (Opus 5.5), 30 Sep 2026. Branch `r/sophie`. Tools `tools/sophie/`. Raw numbers in
`game_stats/runs/sophie-trouble-{all,ranked,residual}.json`. Per-cell grids are in `build/sophie/agg2/cellrows.parquet`
(not committed); the committed summary is in `docs/findings/data/sophie-K1-extras.json` (`hot_cells`).

Host note: this ran in the MacBook's Cowork VM (3 GB, 4 cores), not in a Claude Code session, at the lead's instruction
("Parts 1–2 here only"). It is statistics over replays that already existed. No games were played. Parts 3–4 (synthetic maps,
validation games, the transfer demonstration) are not started; see the handoff at the end.

## Summary

1. **On the maps we lose, the games are lost to economy, not to deaths.** Across the eleven pool-map rows, our
   win-probability residual (actual minus rating-expected score, `performance_model.py` strength fit on 46.6k corpus
   games) tracks our field percentile on pearls at r100 at **Spearman ρ = +0.90** (p = 0.0002). It runs *against*
   our percentile on avoidable deaths (ρ = −0.66): the maps where we die less than the field are the maps we lose.
   Prisoners Dilemma (−0.31), Autarky (−0.19), Trophy (−0.10), Queen Of Spades, Default, Trauma and Devil are
   economy-percentile maps (0.19–0.45). Slithery (+0.29), Portals (+0.23) and Schooltime (+0.21) are the maps we win.
2. **The biggest literal leaks are on the maps we already win.** Portals: +40 length lost per 1k dragon-turns over the
   field (percentile 0.14; ally head-on at portal mouths +18, wall +16). Slithery: +23.5 (self +13, wall +10, mostly
   length-4–7 dragons in bed corridors). Fixing these buys length on winning maps. It does not address the losing
   maps, where our death percentile is 0.39–0.56 (field-typical).
3. **Read of the losses (decoded timelines of 10 ranked losses, not yet checked in the visualiser):** one shape with two
   openings.
   - On Trophy, Queen Of Spades and Trauma the opponent's bed intake in the first 40–50 rounds is 1.4–7× ours.
   - On Autarky and Default the opening is level, or ours, and the gap opens at r40–r80.
   - In every read except Trauma, the opponent's split rate then runs 2–4× ours per 25–40 rounds and head-on trades
     stay about one-for-one; the opponent simply out-produces us (median first-behind round r20, field r30).
   - The Trauma loss is the exception: we out-eat and out-split from r50, then lose on longest at r500 after heavy
     corridor attrition.
   On Prisoners Dilemma we split the three length-11 starters into 2–3-segment pieces by r20, trade them away, and then
   eat **0 pearls for 100+ rounds**. The field-winning opponents' dead-end deaths look like throughput (small dragons dying in
   cul-de-sacs and being re-eaten), the L29 churn economy.
4. **Cross-map general gaps (all maps, medians, ours · field):**
   - behind on length at r100 in 65 % of games, against 49 %;
   - first behind at r20, against r30;
   - last split r393 against r453;
   - dragons at r100 12 against 16;
   - **loop turns** (head back on a cell it held 2–4 rounds earlier) 104 against 60 per 1k dragon-turns, field
     percentile 0.28, worst on Trauma, Devil, Slithery and Queen Of Spades;
   - deaths within 2 rounds of a portal step 20 against 15 per 100 transits;
   - sonar: exactly 4.0 rays per dragon-turn in every game, against 2.6.
5. **TLE:** our `invalid` deaths are all TLE turns. There are 3.1 per game overall and 12.3 on Portals. They come
   entirely from the Tyr/fenrir-era submissions (9508, 9943, 10413, 10473). The latest subs (11244, 11325, 11398,
   11969) have none, so Ares has fixed this. It is recorded here so nobody re-diagnoses it.
6. **Length-band artefact to check before acting:** our length-≥16 dragons die to their own body at 8× the field's
   rate per dragon-turn (8.0 against 1.0 per 1k) and to walls at 5×. But 46 % of the length-≥8 self/wall deaths
   fall in r401–480, and 91 % are on Schooltime, Slithery and Portals (winning maps). That looks like a deliberate late cash-in,
   not a leak; one visualiser look settles it.

### Ranking (worst residual first)

| rank | map | win-prob residual | pearls r100 ÷ field median (pct) | length lost /1k dt: excess over field (pct) | dominant literal class (excess length /1k) | weakest general row (pct) |
|---|---|---|---|---|---|---|
| 1 | Prisoners Dilemma | -0.305 ± 0.033 | 0.36 (0.23) | -25.5 (0.49) | h2h_enemy +12.9 | length r100 (0.22) |
| 2 | Prisoners Dilemma 10 | -0.305 ± 0.033 | 0.32 (0.19) | -12.2 (0.50) | h2h_enemy +16.4 | births r100 (0.18) |
| 3 | Autarky | -0.191 ± 0.036 | 0.78 (0.33) | +10.6 (0.32) | wall +11.5 | length r100 (0.20) |
| 4 | Trophy | -0.103 ± 0.051 | 0.68 (0.31) | +3.2 (0.39) | ally_body +1.7 | length r100 (0.30) |
| 5 | Queen Of Spades | -0.073 ± 0.050 | 0.93 (0.45) | -0.6 (0.48) | h2h_ally +1.3 | loop turns (0.28) |
| 6 | Default | -0.065 ± 0.049 | 0.85 (0.37) | +4.7 (0.41) | h2h_ally +3.0 | newborn survival (0.32) |
| 7 | Trauma | -0.045 ± 0.043 | 0.43 (0.34) | +5.0 (0.45) | wall +3.4 | loop turns (0.11) |
| 8 | Devil | -0.031 ± 0.046 | 0.57 (0.36) | -5.1 (0.56) | ally_body +3.4 | loop turns (0.15) |
| 9 | Schooltime | +0.213 ± 0.046 | 1.69 (0.52) | +0.9 (0.48) | self +4.3 | loop turns (0.22) |
| 10 | Portals | +0.232 ± 0.050 | 1.03 (0.50) | +40.0 (0.14) | h2h_ally +17.9 | newborn survival (0.12) |
| 11 | Slithery Fight | +0.292 ± 0.041 | 1.15 (0.61) | +23.5 (0.27) | self +12.7 | loop turns (0.12) |

Prisoners Dilemma and Prisoners Dilemma 10 share a terrain and a residual (the corpus index does not separate them). Percentiles
follow BENCHMARKS: the share of field side-games on the same map that we beat, ties counted half, averaged over our
side-games, so 0.5 is field-typical and higher is better for every row, deaths included.

## Data and definitions

- **Us:** every team-7 game in `public_replays/corpus` at extraction time (881 side-games, 28 Sep 02:28 – 30 Sep 00:00 UTC, 169
  ranked). These are **16 submissions**, not one bot: the live slot as it was at each game (10473 Tyr V12 n = 215, 10013 n = 112,
  11398 n = 110, 9508 n = 91, 11969 n = 55, …). `sophie-trouble-ranked.json` repeats every card on the ranked subset.
  Ranked win shares are higher (rating-band opponents). The residual adjusts for opponent strength.
- **Field:** the A2 field sample (`build/a2-field`, 4,563 games without team 7, ~470 per map). Top-10 = the ten highest-rated
  teams other than 7 in the latest ladder snapshot (`tools.analysis.features.compare.ladder_lookup`).
- **Local base:** the lanes' base (`lune-r1-07-latecap8x-only`, `W==32 && H==16` off) has **no replays on the Mac**, and running 1,600
  games here was out of scope, so it is **not in these cards**. `renoir-00-base` (Ares V06, 345 pool + gen replays under
  `build/ra/runs/`) is used in Part 2 only, as the one bot with gen-map deaths. Desktop run needed; see the handoff.
- **Rates:** pooled deaths (or length lost) ÷ dragon-turns × 1000 per cohort and map, with the percentile on per-side-game rates.
  Round and length bands use the dragon-turns spent in that band as the denominator.
- **Classes and credit:** F1's (`tools/analysis/features/extract.py death_class`). Contexts overlap, as in the C1-C ledger:
  - newborn: child ≤ 10 rounds old;
  - trapped: ≤ 15 cells reachable in 5 steps with bodies blocking, suicide excluded;
  - portal: head within 2 steps of a portal cell;
  - transit: own portal step this round or in the previous two;
  - crowd23: length ≤ 3 dying into own-side bodies;
  - fight: C2-0's window evaluated at the death round (an enemy head within 4; ≥ 3 heads of one side and ≥ 1 of the
    other within 6; wrap Manhattan). This is a per-death stand-in, not C2-0's event detector.
- **General:** pearls and births at checkpoint c count events at rounds ≤ c (F1 convention; verified against A2 features on game 498496).
  - Loop turns: a dragon's head is on a cell it held 2–4 rounds earlier (a length-≥2 dragon cannot reverse in 2 rounds, so
    this is a small circle).
  - Idle: the head did not move.
  - First behind: the earliest 5-round sample from which our total length stays below theirs through r100.
  - Spawn P/Q: the two seat-hashes of each map. Terrain is identical and the spawns are swapped.
- **Check against F1:** on 200 random field games the extractor reproduces the A2 feature lab exactly: 1,694 per-side
  class counts with 0 mismatches; near-portal, newborn and enclosed flags identical; and pearls@100, births@100 and
  dragon-turns identical on all 9,290 side-games.
- **Replay reading:** `tools/sophie/k1_timeline.py <game>` prints a 20–50-round decoded timeline with deaths tagged by class,
  trapped flag and signature. Read so far: Prisoners Dilemma ×3, Autarky ×2, Trophy ×2, Default, Queen Of Spades and Trauma ×1
  each, all ranked losses. **The visualiser pass the brief requires is still owed** for every map, and Devil, Portals,
  Slithery and Schooltime have no read at all. Their paragraphs are marked as not read and say only what the ledger says.

## Cards

### Autarky

n = 90 side-games of ours (ranked 15), 948 field (172 top-10). Win share 0.18 (ranked 0.47); win-probability residual **-0.191 ± 0.036** (actual 0.18 vs 0.37 expected from ratings, n = 90).
Seat/spawn: spawn P 0.14 (n 49, field 0.50), spawn Q 0.22 (n 41, field 0.50).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 9.28 · 6.27 · 4.17 | +5.12 | 25.7 · 14.1 | 0.29 |
| self | 1.10 · 3.50 · 2.42 | -1.32 | 3.9 · 8.8 | 0.59 |
| ally_body | 0.77 · 0.87 · 0.71 | +0.06 | 1.8 · 2.1 | 0.57 |
| h2h_ally | 0.94 · 0.62 · 0.67 | +0.27 | 2.2 · 1.6 | 0.41 |
| enemy_body | 0.18 · 0.05 · 0.01 | +0.16 | 0.4 · 0.1 | 0.39 |
| h2h_enemy | 8.03 · 5.16 · 4.85 | +3.18 | 20.2 · 14.2 | 0.31 |
| invalid | 0.01 · 1.09 · 2.85 | -2.84 | 0.0 · 2.7 | 0.56 |
| all | 20.31 · 17.57 · 15.69 | +4.62 | 54.2 · 43.6 | 0.35 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 5.53 · 7.13 | 14.7 · 15.8 | 0.43 |
| trapped | 11.66 · 11.26 | 31.7 · 26.0 | 0.39 |
| portal | 3.58 · 2.35 | 9.1 · 6.3 | 0.29 |
| transit | 1.26 · 0.72 | 3.0 · 1.9 | 0.33 |
| crowd23 | 2.52 · 4.67 | 6.0 · 10.6 | 0.59 |
| fight | 10.75 · 7.91 | 27.6 · 19.7 | 0.36 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 13.3 / 10.8 | 0.4 / 3.6 | 0.1 / 0.6 | 0.9 / 0.4 | 7.7 / 7.1 |
| r50-99 | 10.7 / 8.0 | 0.4 / 2.7 | 0.5 / 0.5 | 0.9 / 0.5 | 10.3 / 7.3 |
| r100-249 | 8.7 / 6.1 | 0.5 / 2.2 | 0.8 / 0.7 | 1.1 / 0.7 | 8.3 / 6.2 |
| r250+ | 7.1 / 5.3 | 2.8 / 4.9 | 1.2 / 1.2 | 0.8 / 0.6 | 6.6 / 3.5 |
| L1-3 | 9.9 / 6.9 | 0.9 / 3.6 | 0.8 / 0.9 | 1.0 / 0.7 | 8.2 / 5.2 |
| L4-7 | 0.9 / 1.4 | 3.8 / 2.8 | 0.1 / 0.4 | 0.2 / 0.4 | 6.5 / 5.8 |
| L8-15 | 0.0 / 0.2 | 3.8 / 2.1 | 0.0 / 0.1 | 0.0 / 0.1 | 2.0 / 2.0 |
| L16+ | 3.6 / 0.2 | 5.0 / 0.3 | 0.0 / 0.0 | 0.0 / 0.0 | 0.7 / 0.4 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 41.50 · 46.00 · 53.00 / 75.00 · 96.00 · 113.00 / 139.50 · 257.50 · 321.00 | 0.40 / 0.33 / 0.25 |
| dragons r100 | 10.50 · 18.00 · 24.00 | 0.25 |
| length r100 | 25.50 · 45.00 · 57.00 | 0.20 |
| births by r100 | 34.00 · 45.00 · 54.00 | 0.29 |
| pearls /100 dt (r<100) | 6.10 · 6.49 · 6.80 | 0.44 |
| moves per pearl | 18.03 · 19.05 · 18.03 | 0.55 |
| newborn deaths /100 births | 27.58 · 24.71 · 25.09 | 0.44 |
| behind on length at r100 (share) | 0.82 · 0.49 · 0.24 | 0.34 |
| idle turns /1k dt | 21.71 · 19.87 · 20.83 | 0.45 |
| loop turns /1k dt (head back within 4) | 67.64 · 46.07 · 39.15 | 0.33 |
| portal transits per game | 34.00 · 45.50 · 98.00 | – |
| deaths /100 transits (≤2 rounds) | 11.40 · 7.55 · 6.06 | 0.37 |
| last split round | 319.00 · 416.00 · 364.00 | – |
| sonar rays per dragon-turn | 4.01 · 2.60 · 2.61 | – |
| TLE turns per game (mean) | 0.04 · 0.00 · 0.00 | 0.48 |
| first-behind round (median, games behind at r100) | 20.0 · 27.5 | |

Economy: pearls at r100 = **0.78× the field median** (top-10 1.18×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 2933 segments over 90 games; by signature: H1_dead_end +1611, _rest +1120, H7_dense_open_cluster +376; top cells: (34,0) H1_dead_end 1370 vs 1062, (19,17) H1_dead_end 1358 vs 1103, (34,17) H1_dead_end 1262 vs 1027, (19,0) H1_dead_end 1263 vs 1081.

**What goes wrong here.** Read: ranked losses 581399 (vs 375) and 595921 (vs 311), both eliminations. The games are level to r50 (in 595921 we out-eat the opponent in the first 25 rounds). The opponent's split engine then runs at 13–22 splits per 25 rounds against our 2–9, and its eating keeps pace (40–60 pearls per 25 rounds against our 5–15). Many of its dead-end deaths look like deliberate throughput: small dragons dying in cul-de-sacs, with ally-corpse pearls re-eaten. Our own dead-end wall deaths (H1) run at 3–8 per 25 rounds for the whole game, which is the literal excess (+11 wall length/1k). But at 8–40 dragons against 40 that is not what decides the game. Where it goes wrong: we stop producing. Last split is at r319 against the field's r416, pearls at r250 are 140 against 258, and we have a third of the field's portal transits per game. Autarky is an out-produced map, with a dead-end wall leak on top.

### Default

n = 91 side-games of ours (ranked 18), 1016 field (198 top-10). Win share 0.32 (ranked 0.50); win-probability residual **-0.065 ± 0.049** (actual 0.32 vs 0.38 expected from ratings, n = 91).
Seat/spawn: spawn P 0.38 (n 42, field 0.51), spawn Q 0.27 (n 49, field 0.49).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 0.93 · 1.20 · 0.76 | +0.17 | 2.1 · 2.8 | 0.48 |
| self | 1.84 · 1.83 · 1.29 | +0.55 | 6.1 · 5.0 | 0.46 |
| ally_body | 2.17 · 1.75 · 2.21 | -0.04 | 5.5 · 4.5 | 0.46 |
| h2h_ally | 3.08 · 1.88 · 1.56 | +1.52 | 7.9 · 4.9 | 0.38 |
| enemy_body | 0.45 · 0.27 · 0.17 | +0.28 | 1.3 · 0.8 | 0.40 |
| h2h_enemy | 6.89 · 6.22 · 5.48 | +1.42 | 17.8 · 16.9 | 0.43 |
| invalid | 0.00 · 0.44 · 1.20 | -1.20 | 0.0 · 1.2 | 0.56 |
| all | 15.37 · 13.59 · 12.67 | +2.70 | 40.7 · 36.0 | 0.40 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 3.67 · 3.06 | 8.4 · 7.1 | 0.39 |
| trapped | 5.36 · 5.77 | 14.4 · 15.1 | 0.51 |
| portal | 10.03 · 8.12 | 26.2 · 21.4 | 0.40 |
| transit | 4.56 · 3.28 | 12.0 · 8.9 | 0.39 |
| crowd23 | 6.34 · 4.98 | 14.9 · 11.7 | 0.44 |
| fight | 6.07 · 5.76 | 15.1 · 15.1 | 0.47 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 0.2 / 0.2 | 0.5 / 0.3 | 0.2 / 0.4 | 0.5 / 0.7 | 7.6 / 7.0 |
| r50-99 | 0.3 / 0.6 | 1.0 / 0.6 | 1.2 / 1.2 | 2.4 / 1.7 | 6.2 / 7.6 |
| r100-249 | 0.9 / 1.2 | 1.3 / 1.0 | 2.2 / 1.7 | 4.0 / 2.2 | 8.4 / 7.7 |
| r250+ | 1.2 / 1.5 | 2.7 / 3.0 | 2.7 / 2.1 | 2.8 / 1.8 | 5.6 / 4.5 |
| L1-3 | 1.0 / 1.3 | 1.5 / 1.8 | 2.3 / 1.8 | 3.2 / 1.9 | 7.1 / 6.3 |
| L4-7 | 0.1 / 0.3 | 4.7 / 2.6 | 1.3 / 1.2 | 2.4 / 1.9 | 5.8 / 6.4 |
| L8-15 | 0.0 / 0.1 | 4.9 / 1.3 | 0.7 / 0.8 | 1.1 / 0.7 | 2.3 / 2.2 |
| L16+ | 0.0 / 0.0 | 2.2 / 0.8 | 0.9 / 0.8 | 0.4 / 0.3 | 1.7 / 1.5 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 13.00 · 16.00 · 20.00 / 39.00 · 46.00 · 56.50 / 136.00 · 170.00 · 219.00 | 0.39 / 0.37 / 0.39 |
| dragons r100 | 14.00 · 14.00 · 18.00 | 0.42 |
| length r100 | 33.00 · 35.00 · 44.50 | 0.40 |
| births by r100 | 19.00 · 21.00 · 25.00 | 0.38 |
| pearls /100 dt (r<100) | 4.19 · 4.65 · 5.19 | 0.40 |
| moves per pearl | 21.96 · 21.04 · 20.03 | 0.46 |
| newborn deaths /100 births | 23.66 · 18.70 · 17.19 | 0.32 |
| behind on length at r100 (share) | 0.60 · 0.50 · 0.32 | 0.45 |
| idle turns /1k dt | 16.51 · 17.15 · 17.96 | 0.52 |
| loop turns /1k dt (head back within 4) | 57.41 · 46.68 · 42.02 | 0.40 |
| portal transits per game | 114.00 · 147.00 · 250.50 | – |
| deaths /100 transits (≤2 rounds) | 15.86 · 13.02 · 9.96 | 0.40 |
| last split round | 359.00 · 386.00 · 343.50 | – |
| sonar rays per dragon-turn | 4.01 · 2.29 · 2.28 | – |
| TLE turns per game (mean) | 0.01 · 0.01 · 0.00 | 0.50 |
| first-behind round (median, games behind at r100) | 30.0 · 30.0 | |

Economy: pearls at r100 = **0.85× the field median** (top-10 1.23×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 2138 segments over 91 games; by signature: H4_portal_mouth +1341, _rest +459, H5_portal_approach_beds +357; top cells: (27,28) H4_portal_mouth 252 vs 156, (4,4) H4_portal_mouth 251 vs 180, (4,3) H4_portal_mouth 229 vs 166, (27,27) H4_portal_mouth 237 vs 176.

**What goes wrong here.** Read: ranked loss 628699 (vs 573). This is the same shape as Trophy and Queen Of Spades: even to r40, then the opponent's bed pearls run 40–46 per 40 rounds against our 0–6, and its splits 22–28 against 0–3. The ledger shows a small ally head-on excess at portals (+3 length/1k, H4/H5), but the loss is an economy loss: r100 pearls 0.85×, births 19 against 21, and then a stall after r80.

### Devil

n = 81 side-games of ours (ranked 17), 838 field (135 top-10). Win share 0.33 (ranked 0.71); win-probability residual **-0.031 ± 0.046** (actual 0.33 vs 0.36 expected from ratings, n = 81).
Seat/spawn: spawn P 0.44 (n 43, field 0.57), spawn Q 0.21 (n 38, field 0.43).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 6.23 · 8.51 · 10.66 | -4.43 | 15.8 · 19.9 | 0.47 |
| self | 9.49 · 9.77 · 3.37 | +6.12 | 25.7 · 23.4 | 0.45 |
| ally_body | 5.08 · 3.54 · 2.30 | +2.77 | 11.5 · 8.1 | 0.42 |
| h2h_ally | 0.09 · 1.12 · 0.06 | +0.02 | 0.3 · 2.9 | 0.51 |
| enemy_body | 0.23 · 0.17 · 0.04 | +0.19 | 0.5 · 0.4 | 0.43 |
| h2h_enemy | 7.77 · 8.28 · 8.16 | -0.39 | 20.1 · 22.8 | 0.44 |
| invalid | 1.14 · 1.70 · 8.11 | -6.97 | 2.7 · 4.1 | 0.43 |
| all | 30.02 · 33.08 · 32.71 | -2.69 | 76.5 · 81.7 | 0.54 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 13.02 · 15.90 | 31.1 · 37.1 | 0.59 |
| trapped | 24.64 · 28.07 | 62.3 · 67.9 | 0.60 |
| portal | 0.00 · 0.00 | 0.0 · 0.0 | 0.50 |
| transit | 0.00 · 0.00 | 0.0 · 0.0 | 0.50 |
| crowd23 | 13.14 · 14.02 | 30.0 · 32.5 | 0.51 |
| fight | 10.24 · 11.76 | 25.6 · 30.9 | 0.48 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 3.6 / 4.1 | 5.2 / 3.7 | 2.4 / 1.3 | 0.0 / 0.6 | 12.1 / 10.2 |
| r50-99 | 5.7 / 7.3 | 7.7 / 7.2 | 5.3 / 3.0 | 0.0 / 1.1 | 14.8 / 12.9 |
| r100-249 | 6.9 / 9.1 | 9.5 / 10.0 | 5.3 / 3.6 | 0.0 / 1.1 | 6.6 / 8.0 |
| r250+ | 6.4 / 9.5 | 11.8 / 12.5 | 5.6 / 4.4 | 0.2 / 1.3 | 4.7 / 5.7 |
| L1-3 | 6.3 / 9.4 | 8.8 / 10.7 | 5.4 / 3.9 | 0.1 / 1.1 | 7.6 / 8.1 |
| L4-7 | 6.1 / 1.1 | 18.7 / 2.5 | 1.0 / 0.4 | 0.4 / 1.0 | 10.3 / 10.3 |
| L8-15 | 2.4 / 0.5 | 17.8 / 2.0 | 1.0 / 0.2 | 0.0 / 0.6 | 1.4 / 5.2 |
| L16+ | 1.9 / 0.2 | 7.5 / 0.6 | 0.0 / 0.2 | 0.0 / 0.1 | 7.5 / 3.4 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 30.00 · 34.50 · 45.00 / 56.00 · 98.00 · 143.00 / 70.00 · 206.50 · 247.00 | 0.44 / 0.36 / 0.35 |
| dragons r100 | 6.00 · 14.00 · 26.00 | 0.34 |
| length r100 | 13.00 · 34.00 · 61.00 | 0.33 |
| births by r100 | 26.00 · 39.50 · 58.00 | 0.36 |
| pearls /100 dt (r<100) | 9.00 · 10.00 · 11.80 | 0.40 |
| moves per pearl | 12.91 · 10.49 · 9.04 | 0.29 |
| newborn deaths /100 births | 38.46 · 37.22 · 35.71 | 0.47 |
| behind on length at r100 (share) | 0.65 · 0.50 · 0.32 | 0.42 |
| idle turns /1k dt | 31.67 · 36.83 · 41.05 | 0.68 |
| loop turns /1k dt (head back within 4) | 119.90 · 55.37 · 52.05 | 0.15 |
| portal transits per game | 0.00 · 0.00 · 0.00 | – |
| deaths /100 transits (≤2 rounds) | – | – |
| last split round | 133.00 · 185.00 · 157.00 | – |
| sonar rays per dragon-turn | 4.01 · 2.64 · 2.48 | – |
| TLE turns per game (mean) | 3.95 · 0.00 · 0.00 | 0.38 |
| first-behind round (median, games behind at r100) | 25.0 · 25.0 | |

Economy: pearls at r100 = **0.57× the field median** (top-10 1.46×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 1568 segments over 81 games; by signature: H6_bed_pocket +795, H2_bed_corridor +584, H3_bare_corridor +96; top cells: (16,15) H2_bed_corridor 440 vs 187, (15,15) H2_bed_corridor 392 vs 194, (16,0) H2_bed_corridor 438 vs 264, (15,1) H6_bed_pocket 319 vs 144.

**What goes wrong here.** Not read. The ledger is field-typical on deaths (length-lost percentile 0.56). The economy falls away after r50 (r100 0.57×, r250 70 against 206 pearls, last split r133 against r185), and the loop rate is 2.2× the field's (120 against 55 per 1k). Spawn asymmetry: 0.46 from one spawn and 0.24 from the other, against the field's 0.57/0.43, so the field sees it too. The terms keyed on Devil's dimensions (D-033) are in some of the subs in this corpus, so treat this card as mixed.

### Portals

n = 86 side-games of ours (ranked 18), 954 field (214 top-10). Win share 0.65 (ranked 0.78); win-probability residual **+0.232 ± 0.050** (actual 0.65 vs 0.42 expected from ratings, n = 86).
Seat/spawn: spawn P 0.69 (n 48, field 0.51), spawn Q 0.61 (n 38, field 0.49).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 20.29 · 15.59 · 16.93 | +3.36 | 54.7 · 38.7 | 0.37 |
| self | 13.16 · 10.58 · 4.36 | +8.80 | 35.1 · 27.9 | 0.32 |
| ally_body | 4.28 · 5.16 · 4.55 | -0.27 | 11.3 · 13.7 | 0.54 |
| h2h_ally | 12.50 · 5.76 · 4.06 | +8.44 | 34.1 · 16.1 | 0.11 |
| enemy_body | 0.00 · 0.00 · 0.00 | +0.00 | 0.0 · 0.0 | 0.50 |
| h2h_enemy | 0.00 · 0.00 · 0.00 | +0.00 | 0.0 · 0.0 | 0.50 |
| invalid | 1.61 · 1.32 · 3.39 | -1.78 | 4.8 · 3.5 | 0.40 |
| all | 51.84 · 38.41 · 33.29 | +18.55 | 140.0 · 100.0 | 0.18 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 28.13 · 19.60 | 72.2 · 48.5 | 0.17 |
| trapped | 45.04 · 36.10 | 122.6 · 93.6 | 0.25 |
| portal | 43.53 · 29.55 | 116.8 · 79.6 | 0.15 |
| transit | 24.29 · 15.34 | 66.6 · 42.9 | 0.17 |
| crowd23 | 26.44 · 19.07 | 60.7 · 44.9 | 0.24 |
| fight | 37.79 · 27.40 | 102.0 · 71.4 | 0.20 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 17.6 / 12.5 | 9.5 / 5.3 | 1.1 / 1.7 | 8.3 / 4.2 | 0.0 / 0.0 |
| r50-99 | 16.7 / 14.2 | 10.9 / 7.0 | 2.6 / 3.6 | 11.3 / 5.7 | 0.0 / 0.0 |
| r100-249 | 23.1 / 16.5 | 13.9 / 9.5 | 4.0 / 5.2 | 15.6 / 6.6 | 0.0 / 0.0 |
| r250+ | 18.8 / 15.2 | 13.1 / 12.6 | 5.0 / 5.7 | 10.5 / 5.2 | 0.0 / 0.0 |
| L1-3 | 23.5 / 18.3 | 14.7 / 11.6 | 4.8 / 5.4 | 12.3 / 5.6 | 0.0 / 0.0 |
| L4-7 | 4.6 / 1.5 | 3.8 / 5.7 | 1.7 / 4.3 | 17.4 / 8.4 | 0.0 / 0.0 |
| L8-15 | 3.1 / 0.8 | 12.0 / 5.0 | 2.1 / 1.7 | 2.6 / 1.8 | 0.0 / 0.0 |
| L16+ | 0.2 / 0.2 | 4.7 / 0.9 | 0.7 / 0.8 | 0.5 / 0.6 | 0.0 / 0.0 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 34.50 · 42.00 · 44.00 / 137.00 · 133.50 · 142.50 / 634.50 · 619.50 · 669.00 | 0.45 / 0.50 / 0.54 |
| dragons r100 | 18.50 · 21.00 · 22.00 | 0.37 |
| length r100 | 45.00 · 53.00 · 55.00 | 0.33 |
| births by r100 | 51.00 · 53.00 · 58.00 | 0.48 |
| pearls /100 dt (r<100) | 14.58 · 11.19 · 11.22 | 0.76 |
| moves per pearl | 6.76 · 8.86 · 8.58 | 0.84 |
| newborn deaths /100 births | 54.90 · 45.81 · 46.15 | 0.12 |
| behind on length at r100 (share) | 0.79 · 0.49 · 0.48 | 0.35 |
| idle turns /1k dt | 50.82 · 39.94 · 42.51 | 0.21 |
| loop turns /1k dt (head back within 4) | 132.81 · 99.48 · 131.68 | 0.32 |
| portal transits per game | 491.00 · 418.00 · 434.50 | – |
| deaths /100 transits (≤2 rounds) | 39.82 · 33.87 · 32.85 | 0.35 |
| last split round | 457.00 · 492.00 · 491.00 | – |
| sonar rays per dragon-turn | 4.01 · 2.44 · 2.99 | – |
| TLE turns per game (mean) | 12.31 · 0.00 · 0.00 | 0.33 |
| first-behind round (median, games behind at r100) | 10.0 · 25.0 | |

Economy: pearls at r100 = **1.03× the field median** (top-10 1.07×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 11279 segments over 86 games; by signature: H4_portal_mouth +7033, H1_dead_end +4708, H2_bed_corridor +3127; top cells: (28,1) H4_portal_mouth 384 vs 174, (28,9) H4_portal_mouth 357 vs 158, (15,8) H1_dead_end 1367 vs 1156, (22,13) H4_portal_mouth 373 vs 183.

**What goes wrong here.** Not read. This is the largest literal excess in the pool: ally head-on +18 length/1k at portal mouths (H4) and wall +16, newborn deaths 55 against 46 per 100 births, and deaths per 100 transits 40 against 34, TLE 12.3 turns per game. But it is a winning map (residual +0.23) with an above-field pearl rate (14.8 against 11.3 per 100 dt, percentile 0.85). The sides never meet by terrain here, so there are no enemy deaths at all. It is a pure self-economy race, and we win it while leaking. Fixing the leak here buys length, not wins.

### Prisoners Dilemma

n = 51 side-games of ours (ranked 8), 374 field (67 top-10). Win share 0.10 (ranked 0.25); win-probability residual **-0.305 ± 0.033** (actual 0.11 vs 0.42 expected from ratings, n = 90).
Seat/spawn: spawn P 0.04 (n 23, field 0.52), spawn Q 0.14 (n 28, field 0.48).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 6.42 · 16.06 · 8.41 | -1.99 | 16.8 · 35.5 | 0.54 |
| self | 6.24 · 13.39 · 6.41 | -0.18 | 17.2 · 29.8 | 0.38 |
| ally_body | 0.34 · 1.22 · 1.43 | -1.09 | 0.7 · 2.7 | 0.62 |
| h2h_ally | 0.69 · 0.39 · 0.52 | +0.16 | 1.6 · 1.0 | 0.47 |
| enemy_body | 0.02 · 0.08 · 0.08 | -0.05 | 0.0 · 0.2 | 0.53 |
| h2h_enemy | 10.05 · 3.88 · 3.27 | +6.78 | 23.0 · 10.0 | 0.32 |
| invalid | 0.05 · 2.37 · 6.39 | -6.34 | 0.1 · 5.7 | 0.54 |
| all | 23.80 · 37.39 · 26.51 | -2.71 | 59.5 · 85.0 | 0.52 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 10.89 · 25.63 | 26.7 · 55.5 | 0.60 |
| trapped | 13.68 · 32.70 | 35.9 · 72.7 | 0.61 |
| portal | 2.24 · 1.02 | 5.0 · 2.6 | 0.31 |
| transit | 0.66 · 0.40 | 1.5 · 1.0 | 0.42 |
| crowd23 | 7.01 · 14.75 | 17.3 · 32.2 | 0.45 |
| fight | 13.93 · 18.91 | 32.4 · 43.0 | 0.48 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 11.9 / 19.1 | 12.3 / 12.8 | 0.2 / 1.0 | 1.0 / 0.4 | 19.5 / 12.8 |
| r50-99 | 6.2 / 17.8 | 5.5 / 12.2 | 0.2 / 0.8 | 0.2 / 0.3 | 9.3 / 5.8 |
| r100-249 | 5.0 / 14.5 | 3.7 / 11.7 | 0.5 / 1.0 | 0.9 / 0.3 | 6.9 / 3.0 |
| r250+ | 0.9 / 15.7 | 2.5 / 15.7 | 0.4 / 1.7 | 0.3 / 0.5 | 2.5 / 0.4 |
| L1-3 | 6.7 / 18.3 | 6.3 / 15.1 | 0.4 / 1.4 | 0.7 / 0.4 | 10.1 / 4.2 |
| L4-7 | 0.0 / 0.2 | 3.6 / 2.4 | 0.0 / 0.3 | 0.0 / 0.4 | 9.7 / 3.3 |
| L8-15 | 9.8 / 0.2 | 24.5 / 0.6 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.3 |
| L16+ | 0.0 / 0.0 | 0.0 / 0.2 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.0 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 19.00 · 36.00 · 38.00 / 22.00 · 60.50 · 74.00 / 30.00 · 98.50 · 149.00 | 0.25 / 0.23 / 0.23 |
| dragons r100 | 2.00 · 5.00 · 10.00 | 0.29 |
| length r100 | 4.00 · 18.00 · 25.00 | 0.22 |
| births by r100 | 14.00 · 28.00 · 37.00 | 0.26 |
| pearls /100 dt (r<100) | 6.63 · 10.83 · 10.88 | 0.27 |
| moves per pearl | 18.43 · 10.38 · 9.78 | 0.27 |
| newborn deaths /100 births | 57.32 · 46.15 · 45.07 | 0.41 |
| behind on length at r100 (share) | 0.86 · 0.49 · 0.27 | 0.31 |
| idle turns /1k dt | 24.97 · 41.94 · 44.44 | 0.67 |
| loop turns /1k dt (head back within 4) | 92.05 · 43.46 · 40.34 | 0.32 |
| portal transits per game | 6.00 · 4.00 · 12.00 | – |
| deaths /100 transits (≤2 rounds) | 0.00 · 0.00 · 0.00 | 0.42 |
| last split round | 96.00 · 150.00 · 124.00 | – |
| sonar rays per dragon-turn | 4.01 · 2.87 · 2.58 | – |
| TLE turns per game (mean) | 0.04 · 0.00 · 0.00 | 0.48 |
| first-behind round (median, games behind at r100) | 15.0 · 20.0 | |

Economy: pearls at r100 = **0.36× the field median** (top-10 1.22×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 19 segments over 51 games; by signature: H7_dense_open_cluster +42, _rest -2, H4_portal_mouth -22; top cells: (18,4) H7_dense_open_cluster 92 vs 29, (13,11) H7_dense_open_cluster 56 vs 19, (17,10) H7_dense_open_cluster 67 vs 38, (18,11) H7_dense_open_cluster 43 vs 25.

**What goes wrong here.** Read (decoded, not yet in the visualiser): ranked losses 625947 (vs 608, eliminated r28), 510088 (vs 40, r146), 512167 (vs 456, r199). The three length-11 starters are split into 2–3-segment pieces inside the first 20 rounds (7–10 splits against the opponent's 9–13) and those pieces trade head-on with the enemy at an even rate; by r20 we hold 5–7 segments against their 17. From there we eat nothing: 0 pearls per 20 rounds from r40 onward in 510088 and 512167 while the opponent eats 20–40 per 20 rounds from the beds we no longer reach. The literal ledger calls this map clean (our wall/self deaths are below the field's) because the dragons that would have died are already gone. What loses is the opening conversion of a few long starters into many weak pieces, then exclusion from the beds; the r100 economy is 0.36× the field median, the worst of any map, and the residual (−0.31) is the largest in the pool.

### Prisoners Dilemma 10

n = 39 side-games of ours (ranked 3), 336 field (55 top-10). Win share 0.13 (ranked 0.33); win-probability residual **-0.305 ± 0.033** (actual 0.11 vs 0.42 expected from ratings, n = 90).
Seat/spawn: spawn P 0.09 (n 22, field 0.51), spawn Q 0.18 (n 17, field 0.49).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 3.31 · 9.04 · 6.02 | -2.70 | 7.2 · 19.4 | 0.54 |
| self | 4.77 · 11.25 · 5.35 | -0.58 | 12.6 · 25.1 | 0.45 |
| ally_body | 1.21 · 1.85 · 2.27 | -1.06 | 2.7 · 4.2 | 0.65 |
| h2h_ally | 0.71 · 0.64 · 0.45 | +0.26 | 1.7 · 1.5 | 0.53 |
| enemy_body | 0.16 · 0.15 · 0.07 | +0.09 | 0.3 · 0.3 | 0.49 |
| h2h_enemy | 11.34 · 4.36 · 3.74 | +7.60 | 27.8 · 11.4 | 0.32 |
| invalid | 0.00 · 1.10 · 3.77 | -3.77 | 0.0 · 2.6 | 0.55 |
| all | 21.51 · 28.39 · 21.66 | -0.15 | 52.4 · 64.6 | 0.50 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 7.21 · 17.12 | 16.3 · 36.7 | 0.61 |
| trapped | 9.62 · 23.10 | 22.2 · 50.6 | 0.69 |
| portal | 2.38 · 1.07 | 5.6 · 2.7 | 0.34 |
| transit | 0.93 · 0.40 | 2.1 · 1.0 | 0.47 |
| crowd23 | 6.27 · 13.46 | 14.1 · 29.3 | 0.55 |
| fight | 14.71 · 16.31 | 34.6 · 36.8 | 0.45 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 6.1 / 11.9 | 6.5 / 9.9 | 0.2 / 0.8 | 0.2 / 0.4 | 28.9 / 18.7 |
| r50-99 | 2.1 / 9.4 | 2.8 / 9.3 | 1.1 / 1.1 | 0.4 / 0.5 | 13.5 / 6.7 |
| r100-249 | 2.1 / 7.9 | 3.0 / 10.0 | 1.5 / 2.0 | 1.2 / 0.7 | 4.6 / 2.2 |
| r250+ | 2.6 / 8.9 | 6.2 / 13.5 | 2.0 / 2.4 | 0.8 / 0.7 | 0.2 / 0.3 |
| L1-3 | 3.4 / 10.1 | 4.6 / 12.4 | 1.2 / 2.1 | 0.7 / 0.7 | 11.3 / 4.5 |
| L4-7 | 0.8 / 0.2 | 6.2 / 3.5 | 1.6 / 0.1 | 0.0 / 0.4 | 15.6 / 5.3 |
| L8-15 | 0.0 / 0.2 | 19.5 / 0.5 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.2 |
| L16+ | 0.0 / 0.0 | 0.0 / 0.7 | 0.0 / 0.0 | 0.0 / 0.0 | 0.0 / 0.2 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 15.00 · 32.50 · 34.00 / 19.00 · 58.50 · 59.00 / 19.00 · 72.00 · 65.00 | 0.19 / 0.19 / 0.21 |
| dragons r100 | 1.00 · 6.00 · 12.00 | 0.25 |
| length r100 | 3.00 · 18.00 · 30.00 | 0.22 |
| births by r100 | 9.00 · 27.00 · 29.00 | 0.18 |
| pearls /100 dt (r<100) | 5.07 · 8.76 · 8.80 | 0.24 |
| moves per pearl | 21.18 · 12.43 · 12.06 | 0.24 |
| newborn deaths /100 births | 50.00 · 44.44 · 39.13 | 0.45 |
| behind on length at r100 (share) | 0.85 · 0.50 · 0.33 | 0.33 |
| idle turns /1k dt | 23.78 · 36.96 · 39.12 | 0.70 |
| loop turns /1k dt (head back within 4) | 75.41 · 48.52 · 45.38 | 0.38 |
| portal transits per game | 3.00 · 4.00 · 6.00 | – |
| deaths /100 transits (≤2 rounds) | 0.00 · 0.00 · 0.00 | 0.45 |
| last split round | 37.50 · 106.50 · 71.00 | – |
| sonar rays per dragon-turn | 4.00 · 2.84 · 2.59 | – |
| TLE turns per game (mean) | 0.00 · 0.00 · 0.00 | 0.50 |
| first-behind round (median, games behind at r100) | 5.0 · 15.0 | |

Economy: pearls at r100 = **0.32× the field median** (top-10 1.01×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 13 segments over 39 games; by signature: H7_dense_open_cluster +13; top cells: (16,11) H7_dense_open_cluster 107 vs 65.

**What goes wrong here.** Same terrain as Prisoners Dilemma with ten starters; the same opening collapse. We are behind by r5 (median first-behind round), last split at r38 against the field's r106, and the r100 economy is 0.32× the field median. Death rates are at or below the field's, apart from enemy head-on (+15 length/1k): we trade small pieces head-on and run out of pieces. (No separate replay read; the ledger matches the three Prisoners Dilemma reads.)

### Queen Of Spades

n = 75 side-games of ours (ranked 15), 836 field (119 top-10). Win share 0.31 (ranked 0.53); win-probability residual **-0.073 ± 0.050** (actual 0.31 vs 0.38 expected from ratings, n = 75).
Seat/spawn: spawn P 0.38 (n 40, field 0.54), spawn Q 0.23 (n 35, field 0.46).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 4.47 · 4.75 · 3.28 | +1.19 | 11.3 · 11.6 | 0.51 |
| self | 3.50 · 3.55 · 2.00 | +1.50 | 10.0 · 9.1 | 0.43 |
| ally_body | 2.13 · 1.68 · 1.36 | +0.77 | 5.4 · 4.3 | 0.51 |
| h2h_ally | 2.15 · 1.62 · 0.74 | +1.42 | 5.7 · 4.4 | 0.43 |
| enemy_body | 0.29 · 0.21 · 0.20 | +0.09 | 0.8 · 0.6 | 0.42 |
| h2h_enemy | 5.23 · 5.75 · 5.65 | -0.42 | 13.4 · 15.6 | 0.45 |
| invalid | 0.01 · 0.67 · 2.39 | -2.38 | 0.0 · 1.7 | 0.54 |
| all | 17.78 · 18.23 · 15.61 | +2.17 | 46.6 · 47.3 | 0.47 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 6.06 · 7.19 | 15.6 · 17.7 | 0.55 |
| trapped | 12.36 · 12.96 | 32.7 · 33.2 | 0.53 |
| portal | 8.82 · 9.73 | 22.8 · 25.5 | 0.54 |
| transit | 4.72 · 4.74 | 12.4 · 12.8 | 0.50 |
| crowd23 | 7.19 · 6.34 | 17.5 · 15.2 | 0.47 |
| fight | 4.74 · 6.11 | 12.0 · 15.7 | 0.53 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 2.0 / 4.5 | 2.3 / 2.6 | 1.1 / 1.4 | 2.1 / 1.6 | 3.3 / 2.8 |
| r50-99 | 5.9 / 7.0 | 3.9 / 3.9 | 1.8 / 2.1 | 3.2 / 2.4 | 7.3 / 6.6 |
| r100-249 | 5.2 / 5.1 | 3.3 / 3.3 | 2.4 / 1.8 | 2.5 / 1.9 | 5.9 / 6.9 |
| r250+ | 3.4 / 3.8 | 3.8 / 3.8 | 2.1 / 1.4 | 1.3 / 1.2 | 4.0 / 4.7 |
| L1-3 | 4.7 / 5.2 | 3.4 / 3.7 | 2.2 / 1.7 | 2.2 / 1.6 | 5.3 / 5.8 |
| L4-7 | 2.1 / 0.9 | 4.1 / 2.8 | 0.7 / 1.4 | 2.2 / 2.1 | 5.2 / 6.9 |
| L8-15 | 1.6 / 0.4 | 6.0 / 1.1 | 1.6 / 0.5 | 1.6 / 0.6 | 1.6 / 2.1 |
| L16+ | 0.0 / 0.0 | 8.6 / 0.4 | 0.0 / 0.3 | 0.0 / 0.3 | 2.9 / 1.0 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 10.00 · 14.00 · 14.00 / 39.00 · 42.00 · 43.00 / 87.00 · 122.00 · 140.00 | 0.43 / 0.45 / 0.43 |
| dragons r100 | 7.00 · 8.00 · 10.00 | 0.47 |
| length r100 | 17.00 · 20.00 · 24.00 | 0.44 |
| births by r100 | 15.00 · 17.00 · 17.00 | 0.44 |
| pearls /100 dt (r<100) | 7.62 · 7.86 · 7.38 | 0.44 |
| moves per pearl | 19.46 · 16.17 · 17.08 | 0.41 |
| newborn deaths /100 births | 30.87 · 30.33 · 27.42 | 0.51 |
| behind on length at r100 (share) | 0.57 · 0.49 · 0.40 | 0.46 |
| idle turns /1k dt | 18.66 · 22.74 · 21.80 | 0.58 |
| loop turns /1k dt (head back within 4) | 123.48 · 61.66 · 57.25 | 0.28 |
| portal transits per game | 26.00 · 32.00 · 36.00 | – |
| deaths /100 transits (≤2 rounds) | 35.94 · 33.33 · 32.34 | 0.41 |
| last split round | 233.50 · 271.00 · 254.00 | – |
| sonar rays per dragon-turn | 4.01 · 2.63 · 2.57 | – |
| TLE turns per game (mean) | 0.03 · 0.00 · 0.00 | 0.49 |
| first-behind round (median, games behind at r100) | 20.0 · 35.0 | |

Economy: pearls at r100 = **0.93× the field median** (top-10 1.02×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to -188 segments over 75 games; by signature: _rest +71, H3_bare_corridor +10, H4_portal_mouth +7; top cells: (21,31) H2_bed_corridor 358 vs 271, (8,33) H2_bed_corridor 848 vs 814, (5,3) H5_portal_approach_beds 84 vs 57, (3,3) H2_bed_corridor 309 vs 268.

**What goes wrong here.** Read: ranked loss 622388 (vs 838), an opening collapse: 5 bed pearls against 26 in the first 50 rounds, 3 dragons against 10 at r50, 23 against 4 at r100. Deaths are field-typical, and the opponent loses more than we do in corridors (H2) from r100. The literal ledger has nothing large here. The general ledger shows loop turns (head back on a cell within 4 rounds) at 123 against 62 per 1k, 2× the field: dragons circling instead of reaching beds, which fits a bed-access failure in a compact map. That link is unverified until the visualiser pass.

### Schooltime

n = 99 side-games of ours (ranked 15), 1124 field (315 top-10). Win share 0.63 (ranked 0.80); win-probability residual **+0.213 ± 0.046** (actual 0.63 vs 0.41 expected from ratings, n = 99).
Seat/spawn: spawn P 0.56 (n 50, field 0.47), spawn Q 0.69 (n 49, field 0.53).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 3.18 · 3.37 · 3.83 | -0.66 | 10.4 · 9.1 | 0.41 |
| self | 3.17 · 3.13 · 1.24 | +1.93 | 14.7 · 10.5 | 0.36 |
| ally_body | 2.24 · 1.69 · 1.47 | +0.76 | 6.9 · 5.0 | 0.32 |
| h2h_ally | 1.00 · 0.69 · 0.40 | +0.59 | 2.8 · 2.1 | 0.29 |
| enemy_body | 0.29 · 0.26 · 0.17 | +0.12 | 0.8 · 0.9 | 0.43 |
| h2h_enemy | 5.62 · 6.63 · 7.02 | -1.40 | 17.0 · 21.4 | 0.59 |
| invalid | 0.06 · 0.93 · 2.22 | -2.16 | 0.1 · 2.9 | 0.46 |
| all | 15.55 · 16.71 · 16.36 | -0.82 | 52.9 · 51.9 | 0.52 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 3.63 · 4.72 | 10.2 · 12.6 | 0.55 |
| trapped | 8.83 · 9.59 | 31.6 · 29.3 | 0.47 |
| portal | 4.96 · 5.82 | 14.9 · 18.4 | 0.52 |
| transit | 1.87 · 1.78 | 5.7 · 5.9 | 0.42 |
| crowd23 | 4.60 · 4.45 | 11.0 · 10.5 | 0.37 |
| fight | 6.11 · 7.04 | 17.7 · 21.1 | 0.56 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 0.5 / 0.5 | 0.2 / 0.4 | 0.1 / 0.2 | 0.2 / 0.2 | 2.0 / 2.2 |
| r50-99 | 7.0 / 4.9 | 3.1 / 2.6 | 2.1 / 1.7 | 1.1 / 0.6 | 4.5 / 5.7 |
| r100-249 | 3.3 / 3.4 | 2.2 / 1.9 | 2.1 / 1.5 | 1.1 / 0.7 | 6.0 / 8.1 |
| r250+ | 2.8 / 3.3 | 4.0 / 4.2 | 2.4 / 1.9 | 0.9 / 0.7 | 5.6 / 5.9 |
| L1-3 | 3.3 / 4.1 | 2.5 / 3.2 | 2.3 / 1.9 | 1.1 / 0.7 | 5.9 / 7.0 |
| L4-7 | 2.8 / 1.3 | 5.2 / 3.2 | 2.3 / 1.2 | 0.9 / 0.6 | 5.2 / 6.9 |
| L8-15 | 2.5 / 1.0 | 6.2 / 2.6 | 1.7 / 0.8 | 0.3 / 0.3 | 2.7 / 3.1 |
| L16+ | 3.5 / 0.7 | 10.3 / 1.6 | 0.9 / 0.6 | 0.1 / 0.2 | 2.7 / 2.1 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 13.00 · 12.00 · 16.00 / 86.00 · 51.00 · 121.00 / 388.00 · 283.50 · 547.00 | 0.50 / 0.52 / 0.55 |
| dragons r100 | 23.00 · 19.00 · 28.00 | 0.54 |
| length r100 | 55.00 · 47.00 · 69.00 | 0.53 |
| births by r100 | 38.00 · 22.00 · 49.00 | 0.52 |
| pearls /100 dt (r<100) | 7.42 · 5.65 · 8.22 | 0.52 |
| moves per pearl | 15.35 · 17.81 · 14.15 | 0.45 |
| newborn deaths /100 births | 21.49 · 20.60 · 20.79 | 0.53 |
| behind on length at r100 (share) | 0.39 · 0.49 · 0.37 | 0.55 |
| idle turns /1k dt | 14.53 · 16.95 · 17.19 | 0.58 |
| loop turns /1k dt (head back within 4) | 90.58 · 55.67 · 58.86 | 0.22 |
| portal transits per game | 136.00 · 134.00 · 242.00 | – |
| deaths /100 transits (≤2 rounds) | 21.57 · 15.17 · 12.43 | 0.28 |
| last split round | 470.00 · 489.00 · 491.00 | – |
| sonar rays per dragon-turn | 4.01 · 2.73 · 3.60 | – |
| TLE turns per game (mean) | 0.93 · 0.01 · 0.00 | 0.31 |
| first-behind round (median, games behind at r100) | 45.0 · 40.0 | |

Economy: pearls at r100 = **1.69× the field median** (top-10 2.37×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 7254 segments over 99 games; by signature: H2_bed_corridor +3977, H7_dense_open_cluster +2671, H6_bed_pocket +1210; top cells: (40,16) H2_bed_corridor 619 vs 194, (49,16) H2_bed_corridor 591 vs 190, (41,11) H2_bed_corridor 582 vs 286, (30,37) H7_dense_open_cluster 299 vs 107.

**What goes wrong here.** Not read. A winning map (residual +0.21). Deaths are field-level apart from self (+4 length/1k) and a 1.4× transit death rate. The r100 economy is 1.69× the field median. Nothing to fix for wins here. It is a guard map: a mechanism that costs Schooltime economy is paying for its gains elsewhere.

### Slithery Fight

n = 101 side-games of ours (ranked 22), 942 field (158 top-10). Win share 0.72 (ranked 0.68); win-probability residual **+0.292 ± 0.041** (actual 0.72 vs 0.43 expected from ratings, n = 101).
Seat/spawn: spawn P 0.72 (n 47, field 0.48), spawn Q 0.72 (n 54, field 0.52).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 15.05 · 11.49 · 8.47 | +6.58 | 39.6 · 29.6 | 0.36 |
| self | 12.51 · 9.53 · 3.13 | +9.37 | 39.1 · 26.3 | 0.27 |
| ally_body | 5.26 · 3.16 · 1.90 | +3.37 | 12.5 · 7.6 | 0.26 |
| h2h_ally | 0.90 · 0.59 · 0.30 | +0.60 | 2.5 · 1.8 | 0.21 |
| enemy_body | 0.06 · 0.06 · 0.02 | +0.03 | 0.1 · 0.2 | 0.49 |
| h2h_enemy | 4.11 · 3.41 · 3.46 | +0.65 | 12.0 · 11.5 | 0.34 |
| invalid | 0.33 · 2.24 · 8.75 | -8.43 | 0.8 · 6.1 | 0.42 |
| all | 38.21 · 30.49 · 26.03 | +12.18 | 106.6 · 83.1 | 0.30 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 20.99 · 18.04 | 55.5 · 45.4 | 0.34 |
| trapped | 34.03 · 26.98 | 93.7 · 71.7 | 0.31 |
| portal | 2.12 · 0.89 | 5.8 · 2.9 | 0.14 |
| transit | 0.79 · 0.35 | 2.4 · 1.3 | 0.17 |
| crowd23 | 14.33 · 11.58 | 32.6 · 26.1 | 0.30 |
| fight | 13.98 · 10.26 | 39.3 · 29.2 | 0.26 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 25.5 / 20.3 | 13.4 / 11.6 | 4.6 / 3.1 | 1.6 / 1.0 | 2.5 / 1.9 |
| r50-99 | 21.1 / 15.2 | 13.2 / 9.7 | 6.1 / 3.5 | 1.1 / 0.8 | 6.3 / 4.6 |
| r100-249 | 15.9 / 10.8 | 11.8 / 8.0 | 5.6 / 3.1 | 0.9 / 0.6 | 4.5 / 3.9 |
| r250+ | 11.7 / 10.1 | 12.8 / 10.5 | 4.9 / 3.2 | 0.8 / 0.5 | 3.6 / 3.0 |
| L1-3 | 14.7 / 13.2 | 10.1 / 10.4 | 5.7 / 3.9 | 0.9 / 0.6 | 4.1 / 3.2 |
| L4-7 | 20.3 / 6.6 | 31.7 / 7.3 | 2.9 / 0.9 | 1.4 / 0.7 | 4.6 / 4.5 |
| L8-15 | 4.7 / 3.1 | 13.0 / 4.5 | 0.4 / 0.4 | 0.2 / 0.3 | 3.9 / 2.8 |
| L16+ | 1.0 / 0.4 | 7.1 / 1.1 | 0.2 / 0.1 | 0.0 / 0.0 | 3.0 / 1.5 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 224.00 · 203.00 · 212.00 / 527.00 · 457.00 · 489.00 / 1490.00 · 1201.50 · 1404.00 | 0.58 / 0.61 / 0.69 |
| dragons r100 | 48.00 · 56.00 · 60.00 | 0.34 |
| length r100 | 118.00 · 142.50 · 156.00 | 0.28 |
| births by r100 | 220.00 · 199.00 · 212.00 | 0.59 |
| pearls /100 dt (r<100) | 14.28 · 13.15 · 13.16 | 0.63 |
| moves per pearl | 8.85 · 10.33 · 8.60 | 0.64 |
| newborn deaths /100 births | 53.93 · 49.24 · 48.85 | 0.34 |
| behind on length at r100 (share) | 0.72 · 0.49 · 0.36 | 0.39 |
| idle turns /1k dt | 39.35 · 32.28 · 34.96 | 0.34 |
| loop turns /1k dt (head back within 4) | 110.73 · 69.38 · 64.55 | 0.12 |
| portal transits per game | 61.00 · 35.00 · 35.00 | – |
| deaths /100 transits (≤2 rounds) | 28.97 · 16.39 · 15.44 | 0.16 |
| last split round | 480.00 · 498.00 · 497.00 | – |
| sonar rays per dragon-turn | 4.00 · 2.59 · 2.61 | – |
| TLE turns per game (mean) | 7.35 · 0.03 · 0.00 | 0.31 |
| first-behind round (median, games behind at r100) | 30.0 · 30.0 | |

Economy: pearls at r100 = **1.15× the field median** (top-10 1.07×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 34535 segments over 101 games; by signature: H2_bed_corridor +25982, _rest +3647, H4_portal_mouth +1187; top cells: (27,1) H2_bed_corridor 1387 vs 758, (28,1) H2_bed_corridor 1371 vs 762, (24,1) H2_bed_corridor 1370 vs 770, (31,1) H2_bed_corridor 1320 vs 765.

**What goes wrong here.** Not read. This is the biggest-dying map (length lost 107 against 83 per 1k: self +13, wall +10) and the best winning map (residual +0.29, pearls at r250 1,490 against 1,202). The excess sits in bed corridors (H2) and among length 4–7 dragons: wall 19.9 against 6.6, self 31.4 against 7.3 per 1k dt. It is churn: a fast economy that feeds on its own corpses (corpse share 0.47). TLE 7.3 turns per game on the Tyr/fenrir subs.

### Trauma

n = 94 side-games of ours (ranked 19), 904 field (166 top-10). Win share 0.35 (ranked 0.37); win-probability residual **-0.045 ± 0.043** (actual 0.35 vs 0.40 expected from ratings, n = 94).
Seat/spawn: spawn P 0.28 (n 47, field 0.52), spawn Q 0.43 (n 47, field 0.48).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 8.63 · 7.46 · 4.73 | +3.89 | 20.2 · 16.8 | 0.48 |
| self | 4.93 · 4.88 · 2.49 | +2.44 | 13.2 · 12.0 | 0.37 |
| ally_body | 2.17 · 1.43 · 1.12 | +1.05 | 4.9 · 3.4 | 0.32 |
| h2h_ally | 0.85 · 0.98 · 0.82 | +0.03 | 2.1 · 2.5 | 0.52 |
| enemy_body | 0.08 · 0.05 · 0.05 | +0.03 | 0.2 · 0.1 | 0.45 |
| h2h_enemy | 1.98 · 1.72 · 1.90 | +0.07 | 5.4 · 4.9 | 0.39 |
| invalid | 0.82 · 1.53 · 5.05 | -4.24 | 2.3 · 3.6 | 0.39 |
| all | 19.45 · 18.05 · 16.18 | +3.27 | 48.3 · 43.3 | 0.48 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 6.34 · 7.46 | 15.3 · 16.5 | 0.58 |
| trapped | 17.58 · 15.97 | 42.9 · 37.6 | 0.47 |
| portal | 2.40 · 2.50 | 6.0 · 6.3 | 0.51 |
| transit | 1.01 · 1.00 | 2.6 · 2.6 | 0.51 |
| crowd23 | 7.11 · 6.86 | 16.2 · 15.7 | 0.41 |
| fight | 3.68 · 3.34 | 9.0 · 8.3 | 0.39 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 2.0 / 6.8 | 0.5 / 2.2 | 0.0 / 0.4 | 0.0 / 0.5 | 0.0 / 0.0 |
| r50-99 | 7.0 / 8.5 | 1.2 / 2.7 | 0.5 / 0.5 | 0.3 / 0.7 | 0.0 / 0.1 |
| r100-249 | 9.5 / 7.6 | 3.7 / 3.5 | 2.0 / 1.4 | 1.0 / 1.1 | 2.2 / 1.8 |
| r250+ | 8.6 / 7.3 | 6.2 / 6.1 | 2.5 / 1.6 | 0.8 / 1.0 | 2.1 / 1.9 |
| L1-3 | 9.5 / 8.4 | 4.7 / 5.2 | 2.4 / 1.6 | 0.9 / 1.0 | 2.0 / 1.7 |
| L4-7 | 2.9 / 1.2 | 7.0 / 3.0 | 0.3 / 0.4 | 0.4 / 0.7 | 1.9 / 2.0 |
| L8-15 | 1.1 / 0.5 | 2.6 / 1.3 | 0.1 / 0.2 | 0.0 / 0.5 | 1.2 / 1.0 |
| L16+ | 1.1 / 0.0 | 1.1 / 0.1 | 0.0 / 0.1 | 0.0 / 0.2 | 1.1 / 0.2 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 2.00 · 9.00 · 18.00 / 15.00 · 34.50 · 61.00 / 150.50 · 223.50 · 314.00 | 0.26 / 0.34 / 0.40 |
| dragons r100 | 7.00 · 10.00 · 17.00 | 0.35 |
| length r100 | 16.00 · 25.00 · 41.00 | 0.33 |
| births by r100 | 7.00 · 16.00 · 28.00 | 0.34 |
| pearls /100 dt (r<100) | 3.35 · 5.99 · 7.26 | 0.34 |
| moves per pearl | 18.30 · 18.03 · 16.46 | 0.44 |
| newborn deaths /100 births | 32.58 · 33.33 · 35.61 | 0.53 |
| behind on length at r100 (share) | 0.62 · 0.49 · 0.37 | 0.43 |
| idle turns /1k dt | 19.06 · 20.14 · 22.82 | 0.58 |
| loop turns /1k dt (head back within 4) | 156.34 · 77.77 · 82.24 | 0.11 |
| portal transits per game | 63.00 · 87.50 · 144.50 | – |
| deaths /100 transits (≤2 rounds) | 8.92 · 8.60 · 10.06 | 0.50 |
| last split round | 461.00 · 492.00 · 494.00 | – |
| sonar rays per dragon-turn | 4.00 · 2.47 · 2.04 | – |
| TLE turns per game (mean) | 5.85 · 0.01 · 0.00 | 0.31 |
| first-behind round (median, games behind at r100) | 30.0 · 35.0 | |

Economy: pearls at r100 = **0.43× the field median** (top-10 1.77×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 3882 segments over 94 games; by signature: H3_bare_corridor +3664, _rest +474, H1_dead_end +179; top cells: (17,20) H3_bare_corridor 574 vs 168, (29,4) H3_bare_corridor 416 vs 128, (24,13) H3_bare_corridor 280 vs 87, (19,19) H3_bare_corridor 507 vs 121.

**What goes wrong here.** Read: ranked loss 629825 (vs 837), lost on longest at r500. Here we out-eat and out-split the opponent from r50 to r250 (103 against 44 pearls in r100–150) but die in corridors at 2–4× its rate (25–53 deaths per 50 rounds, mostly wall deaths in dead-ends and corridors: H1/H3), and we never build a crown (longest 3–4 against 5). This is the map where the literal ledger and the loss agree: corridor attrition plus no concentration. It also has the highest loop rate in the pool (156 against 78 per 1k). TLE: 5.9 turns per game (Tyr/fenrir submissions).

### Trophy

n = 74 side-games of ours (ranked 12), 854 field (133 top-10). Win share 0.26 (ranked 0.50); win-probability residual **-0.103 ± 0.051** (actual 0.26 vs 0.36 expected from ratings, n = 74).
Seat/spawn: spawn P 0.26 (n 39, field 0.49), spawn Q 0.26 (n 35, field 0.51).

| death class | deaths /1k dt: us · field · top-10 | excess over top-10 | length lost /1k: us · field | field pct (↑ = fewer) |
|---|---|---|---|---|
| wall | 1.76 · 1.18 · 0.70 | +1.07 | 4.2 · 2.9 | 0.45 |
| self | 1.84 · 1.74 · 0.53 | +1.31 | 4.8 · 4.6 | 0.45 |
| ally_body | 1.86 · 1.10 · 0.76 | +1.10 | 4.5 · 2.8 | 0.48 |
| h2h_ally | 1.05 · 0.98 · 0.40 | +0.65 | 2.6 · 2.6 | 0.51 |
| enemy_body | 0.16 · 0.14 · 0.05 | +0.12 | 0.4 · 0.4 | 0.50 |
| h2h_enemy | 11.70 · 10.77 · 10.15 | +1.55 | 30.7 · 30.0 | 0.38 |
| invalid | 0.00 · 0.33 · 0.57 | -0.57 | 0.0 · 0.9 | 0.54 |
| all | 18.38 · 16.24 · 13.14 | +5.23 | 47.3 · 44.1 | 0.36 |

| context (overlapping) | deaths /1k: us · field | length /1k: us · field | pct |
|---|---|---|---|
| newborn | 3.98 · 3.99 | 9.2 · 9.9 | 0.47 |
| trapped | 6.77 · 5.70 | 16.7 · 14.9 | 0.40 |
| portal | 4.06 · 3.04 | 10.3 · 8.2 | 0.50 |
| transit | 1.63 · 1.22 | 4.2 · 3.3 | 0.51 |
| crowd23 | 4.54 · 3.50 | 10.6 · 8.3 | 0.49 |
| fight | 11.39 · 11.17 | 29.3 · 30.3 | 0.41 |

Deaths per 1k dragon-turns spent in the band (us / field):

| band | wall | self | ally body | ally head-on | enemy head-on |
|---|---|---|---|---|---|
| r0-49 | 0.7 / 0.3 | 0.3 / 0.4 | 0.2 / 0.3 | 0.1 / 0.5 | 8.0 / 7.5 |
| r50-99 | 1.0 / 1.0 | 1.1 / 0.9 | 0.9 / 0.8 | 0.8 / 0.8 | 18.4 / 12.3 |
| r100-249 | 1.9 / 1.2 | 1.5 / 1.3 | 2.0 / 1.1 | 1.2 / 1.1 | 12.4 / 11.9 |
| r250+ | 2.3 / 1.4 | 3.2 / 3.5 | 2.6 / 1.5 | 1.1 / 1.0 | 7.6 / 8.2 |
| L1-3 | 1.9 / 1.3 | 1.8 / 1.7 | 1.9 / 1.1 | 1.1 / 1.0 | 11.4 / 10.4 |
| L4-7 | 0.2 / 0.4 | 1.4 / 1.9 | 0.9 / 0.8 | 1.0 / 1.2 | 20.2 / 16.7 |
| L8-15 | 0.0 / 0.1 | 5.9 / 1.9 | 1.6 / 0.7 | 0.5 / 0.4 | 4.3 / 5.1 |
| L16+ | 0.0 / 0.1 | 3.1 / 1.3 | 0.0 / 0.7 | 0.0 / 0.5 | 9.3 / 3.9 |

| general (medians; us · field · top-10) | value | field pct |
|---|---|---|
| pearls r50 / r100 / r250 | 21.50 · 28.00 · 38.00 / 58.50 · 85.50 · 112.00 / 87.00 · 190.50 · 211.00 | 0.35 / 0.31 / 0.34 |
| dragons r100 | 7.50 · 19.00 · 27.00 | 0.31 |
| length r100 | 18.50 · 45.00 · 65.00 | 0.30 |
| births by r100 | 24.00 · 34.00 · 44.00 | 0.31 |
| pearls /100 dt (r<100) | 7.70 · 8.18 · 8.74 | 0.45 |
| moves per pearl | 14.07 · 14.18 · 14.12 | 0.48 |
| newborn deaths /100 births | 19.90 · 17.74 · 11.58 | 0.45 |
| behind on length at r100 (share) | 0.68 · 0.50 · 0.31 | 0.41 |
| idle turns /1k dt | 26.31 · 25.78 · 26.76 | 0.51 |
| loop turns /1k dt (head back within 4) | 47.12 · 51.66 · 42.91 | 0.52 |
| portal transits per game | 2.00 · 7.00 · 10.00 | – |
| deaths /100 transits (≤2 rounds) | 45.45 · 25.00 · 16.22 | 0.31 |
| last split round | 149.50 · 183.00 · 159.00 | – |
| sonar rays per dragon-turn | 4.03 · 3.11 · 2.86 | – |
| TLE turns per game (mean) | 0.00 · 0.00 · 0.00 | 0.50 |
| first-behind round (median, games behind at r100) | 15.0 · 20.0 | |

Economy: pearls at r100 = **0.68× the field median** (top-10 1.31×).
Where (cells with ≥300 of our head-turns): our excess length lost on this map sums to 233 segments over 74 games; by signature: H3_bare_corridor +137, H7_dense_open_cluster +124, _rest +14; top cells: (2,12) H3_bare_corridor 274 vs 178, (12,22) H4_portal_mouth 286 vs 258, (23,10) _rest 61 vs 24, (1,7) H3_bare_corridor 216 vs 170.

**What goes wrong here.** Read: ranked losses 622389 (vs 838) and 518331 (vs 370). The opponent eats 26–42 pearls to our 17–18 in the first 40 rounds, almost all from beds, and splits 2–3× as often every 40 rounds after that (28–38 against 9–15). Enemy head-on deaths are traded one for one throughout (6–15 a side per 40 rounds), so fights neither win nor lose the game. The opponent simply has three times our units by r120. Our deaths are field-typical (length-lost percentile 0.39, avoidable 0.49). The damage is opening bed access plus the production gap: r100 economy 0.68×, dragons at r100 7.5 against 19, deaths per 100 transits 45 against 25.

## Ledger rows touched and proposed weights

| Row | Proposal | Evidence here |
|---|---|---|
| L05 (leaks live in the Tyr lineage and are fixable on Ares) | **keep 0.8** on "the leaks exist"; add to "what moves it": *a leak fix is not a win-rate lever on the losing maps* | Biggest leaks on Portals and Slithery (residual +0.23, +0.29); on the losing maps our death percentile is field-typical (0.39–0.56) |
| L17 (production pace can be forced) | **0.1 → 0.2**, revival trigger met in part | On every losing map we split less and stop earlier (last split r393 against r453; Autarky r319 against r416; Prisoners Dilemma r96 against r150) while the winning opponent splits 2–4× ours. Still unshown: whether we are pearl-bound (P1) or policy-bound; that needs the opening bed-intake test in the row below |
| L29 (`pearls@k` rewards churn) | keep 0.8; note | The winning opponents on Autarky, Queen Of Spades and Default show dead-end deaths as throughput (their H1/H2 wall and self deaths re-eaten), so churn is also how the field wins these maps, not only a gaming risk |
| **new K1-a** | **Losing-map games are lost to opening economy and production, not deaths**; the per-map win residual follows the r100 economy percentile (ρ = +0.90), not the death percentile (ρ = −0.40 for length lost, −0.66 for avoidable deaths) | This file; 0.7 |
| **new K1-b** | **Opening bed access on compact maps** (Trophy, Queen Of Spades, Prisoners Dilemma): our bed intake in r0–50 is 1.4–7× below the opponent's in the read losses | 10 decoded reads; 0.6 until the visualiser pass and a field-wide r0–50 bed-share number per map |
| **new K1-c** | **Looping:** our heads return to a cell within 4 rounds at 1.7× the field's rate (104 against 60 per 1k; 2× on Trauma, Devil and Queen Of Spades) | general ledger; 0.4; mechanism unknown (search tie-breaks? target thrash?); first check whether it is concentrated in newborns or near contested beds |
| **new K1-d** | Prisoners Dilemma opening: the three length-11 starters are split into 2–3-segment pieces within 20 rounds and traded away | 3 reads, last split r96 against r150, pearls r250 30 against 98; 0.5; this is a structure claim for M-1 ("few long starters on a small map"), not a map rule |

## Handoff (what is left of K-1, and for whom)

- **Visualiser pass** (Mac, 30 min): the three losses per map named in the card paragraphs, plus one each on Devil,
  Portals, Slithery and Schooltime. Confirm or correct K1-b, K1-c and the late cash-in reading (Summary, item 6).
- **Lanes' base** (`lune-r1-07-latecap8x-only` nodevil) on z1 seeds 1–2 and the gen panel (desktop, ~7 min). Then
  `python tools/sophie/k1_extract.py --set local:<panel dir> --out build/sophie/x2/local-base` and re-run
  `k1_aggregate.py` → `k1_cards.py` to add the base as a third column to every card.
- Parts 3–4 need the desktop: see `docs/findings/2026-09-30-sophie-K1-hazard-signatures.md` §Handoff.
