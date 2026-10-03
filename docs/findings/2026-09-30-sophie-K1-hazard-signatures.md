# K-1 Part 2 — hazard signatures: which local structure kills, for everyone and for us

Lineage **sophie** (Opus 5.5), 30 Sep 2026. Code: `tools/sophie/hazard.py` (cell features, `SIGNATURES`, `profile`),
`k1_cells.py` (cell rows), `k1_hazard_fit.py` (Poisson GLMs with leave-one-terrain-out; Poisson trees),
`k1_signatures.py` (signature table and 39-map profiles), `k1_extras.py` (gen transfer, where-vs-how decomposition, hot cells).
Data files are in `docs/findings/data/sophie-K1-*`. The cell rows (`build/sophie/agg2/cellrows.parquet`) are not committed.

## Summary

- **Unit:** a cell of a map, per cohort. The outcome is deaths of a class whose head was on that cell; the exposure is
  the head-turns on the cell.
  - Field: 4,563 A2 games, top-10 included.
  - Ours: 881 team-7 side-games.
  - Our lanes' V06 base: 345 local games on pool and gen maps.
  - That makes 21.6k pool cells per cohort, 62.7 M field head-turns and 6.8 M ours.
- **Structure predicts where deaths happen, and it transfers across maps.** A structure-plus-map-scalars Poisson model
  fitted on nine pool terrains explains, on the held-out tenth (median over the ten folds), this share of within-map
  deviance for the field:

  | class | field D² | ours D² |
  |---|---|---|
  | wall | 0.84 | 0.73 |
  | trapped | 0.79 | 0.73 |
  | newborn | 0.70 | 0.56 |
  | self | 0.67 | 0.37 |
  | crowd23 | 0.60 | 0.39 |
  | h2h_ally | 0.46 | 0.47 |
  | transit | 0.44 | 0.42 |
  | fight | 0.37 | 0.36 |
  | ally_body | 0.34 | 0.32 |
  | enemy head-on | 0.04 | 0.04 |

  Enemy head-on is contact, not structure. Trained on the field's pool cells, the structure-only model also places
  the V06 base's deaths on the unseen gen maps (within-map D², median): wall 0.62, transit 0.51, h2h_ally 0.44,
  trapped 0.25, others 0.08–0.22. The gen maps are open, so there is less structure to find.
- **Seven signatures** (one null) cover the hazard. Four carry an excess that is specific to us, from comparing our
  rate with the field's in the same cells:
  - **H2 bed corridor:** own body ×1.64, ally body ×1.60, ally head-on ×1.64, fights ×1.45.
  - **H4 portal mouth:** ally head-on ×1.50, newborn ×1.59, crowd23 ×1.42.
  - **H5 portal approach inside a bed cluster:** ally head-on ×1.92.
  - **H6 bed pocket:** own body ×1.78, ally head-on ×1.69, crowd23 ×1.57.

  The common part (hazardous for everyone) is dominated by **H1 dead-end tips**. They hold 1 % of head-turns and 44 %
  of the field's wall deaths, 29 % of newborn deaths and 28 % of trapped deaths, at ×25–46 the pool rate. We are
  *better* than the field there on own body (×0.57) and crowd deaths (×0.56), and worse on walls (×1.37).
- **Where we go, and how we die there:** 15–50 % of our excess per class comes from *exposure* (wall 15 %, newborn 51 %). We spend more
  head-turns in hazard cells than the field (bed corridors 7.5 % against 6.6 %, portal mouths 4.9 % against 4.0 %,
  dense bed clusters 9.1 % against 6.3 %): bed pull. The rest comes from dying at a higher rate inside the same cells.
  A fix has to choose which half it targets.
- **The generalisation panel barely contains these hazards.** Across the 20 `maps/new` maps:
  - dead-end tips: 0 cells on every map;
  - bed corridors: at most 1.1 % of cells;
  - portal mouths: at most 1.8 %, on 3 of 20 maps.

  The pool medians are 1.3 %, 2.4 % and 2.0 %, with maxima of 9.8 %, 19.9 % and 15.6 %. Only H7 (dense open bed
  cluster) is richer on gen (median 7.2 % against 1.6 %). So a D-032 "gen panel" pass says little about the pool's
  hazard structure. The synthetic families of Part 3 are the missing test, not a nice-to-have. (The `maps/var/*_tr`
  transposes carry their parents' profiles exactly.)

## The signatures

| id | rule (cell features in `hazard.cell_features`) | what it is | pool share of cells: median · max | gen maps with any | headline effect (field · ours · ours÷field) |
|---|---|---|---|---|---|
| H1 dead_end | `deg <= 1` | tip of a cul-de-sac (one open side) | 0.013 · 0.098 (Portals) | 0/20 | wall ×46 · ×51 · 1.37; newborn ×30 · ×27 · 1.00; self ×25 · ×12 · 0.57 |
| H2 bed_corridor | `deg == 2 and bed6 > 0.36` | two-sided corridor cell with beds within 6 steps | 0.024 · 0.199 (Devil) | 4/20 (≤ 0.011) | self ×4.2 · ×5.7 · **1.64**; ally body ×4.9 · ×5.4 · **1.60**; ally head-on ×4.8 · ×5.0 · **1.64** |
| H3 bare_corridor | `deg == 2 and bed6 <= 0.36` | corridor without nearby beds | 0.068 · 0.276 (Trauma) | 19/20 (≤ 0.020) | wall ×2.1 · ×2.0 · 1.18; trapped ×1.9 · ×1.8 · 1.10 |
| H4 portal_mouth | `portal_d == 0` | cell with a portal edge | 0.020 · 0.156 (Portals) | 3/20 | ally head-on ×15 · ×15 · **1.50** (61 %/71 % of all ally head-on deaths); transit ×24 · ×20 · 1.12; newborn ×3.0 · ×4.2 · **1.59** |
| H5 portal_approach_beds | `portal_d == 1 and cluster >= 3` | one step from a portal mouth inside a bed cluster | 0.010 · 0.137 (Portals) | 3/20 | ally head-on ×4.1 · ×5.0 · **1.92** |
| H6 bed_pocket | `deg == 3 and bed3 > 0.28` | bed-rich cell with one kelp side | 0.005 · 0.141 (Portals) | 10/20 | self ×1.7 · ×2.5 · **1.78**; ally head-on ×5.0 · ×5.4 · **1.69**; crowd23 ×2.5 · ×3.3 · **1.57** |
| H7 dense_open_cluster | `deg == 4 and bed3 > 0.44 and bed6 > 0.63` | open ground inside a dense bed cluster | 0.016 · 0.089 (Slithery) | 20/20 | ally body ×1.7 · ×1.5 · 1.26; on gen maps (V06) ×3.2, 59 % of ally-body deaths |
| H8 small_room | `deg >= 3 and reach5 <= 25` | open cell in a small room | 0.064 · 0.172 | 2/20 | **null**: no class above ×1.3. Kept as a negative control for Part 3 |

"Maps > 1" (below) counts the pool terrains where the signature's rate beats that map's own average, among terrains
with ≥ 2,000 head-turns in the signature. The rules were read off Poisson trees (depth 3, ≥ 150 cells per leaf) fitted
on the field's cells (`sophie-K1-trees.json`). The cut points are rounded tree splits, so they were selected on all
ten terrains. The honest out-of-sample number for each class is the leave-one-terrain-out tree check in that file
(`lomo_top_leaf`): the top leaf, refitted without a terrain, has a held-out ratio above 1 on every terrain where it
has exposure. `bed6`/`bed3` are nominal bed rates (pearls per round, 2/(minGap+maxGap)) summed within 6 or 3 terrain
steps. `cluster` is the size of the nearest bed cluster (beds within 2 steps chained) when a bed is within 2 steps.

#### Signature effects (rate in signature cells ÷ the cohort's pool-wide rate)

| signature | class | field × (maps >1) | ours × (maps >1) | ours ÷ field in the cells | exposure share field · ours | share of the class's deaths field · ours | V06 base on gen maps × (maps >1) |
|---|---|---|---|---|---|---|---|
| H1_dead_end | wall | 46.1 (8/8) | 50.8 (4/4) | **1.37** | 0.010 · 0.009 | 0.44 · 0.47 | – |
| H1_dead_end | self | 25.4 (8/8) | 11.9 (4/4) | **0.57** | 0.010 · 0.009 | 0.24 · 0.11 | – |
| H1_dead_end | trapped | 29.3 (8/8) | 26.0 (4/4) | **1.05** | 0.010 · 0.009 | 0.28 · 0.24 | – |
| H1_dead_end | newborn | 30.4 (8/8) | 26.8 (4/4) | **1.00** | 0.010 · 0.009 | 0.29 · 0.25 | – |
| H1_dead_end | transit | 37.6 (2/8) | 37.5 (1/4) | **1.33** | 0.010 · 0.009 | 0.36 · 0.35 | – |
| H1_dead_end | crowd23 | 16.7 (8/8) | 7.8 (3/4) | **0.56** | 0.010 · 0.009 | 0.16 · 0.07 | – |
| H1_dead_end | fight | 23.6 (8/8) | 20.2 (4/4) | **1.01** | 0.010 · 0.009 | 0.23 · 0.19 | – |
| H2_bed_corridor | wall | 5.1 (8/10) | 4.6 (5/7) | **1.13** | 0.066 · 0.075 | 0.34 · 0.35 | 12.8 (2/3) |
| H2_bed_corridor | self | 4.2 (8/10) | 5.7 (6/7) | **1.64** | 0.066 · 0.075 | 0.28 · 0.43 | 3.7 (1/3) |
| H2_bed_corridor | ally_body | 4.9 (10/10) | 5.4 (6/7) | **1.60** | 0.066 · 0.075 | 0.32 · 0.41 | 3.7 (1/3) |
| H2_bed_corridor | h2h_ally | 4.8 (5/10) | 5.0 (4/7) | **1.64** | 0.066 · 0.075 | 0.32 · 0.38 | 13.4 (1/2) |
| H2_bed_corridor | trapped | 4.8 (8/10) | 5.5 (7/7) | **1.35** | 0.066 · 0.075 | 0.32 · 0.41 | 7.5 (2/3) |
| H2_bed_corridor | newborn | 5.0 (9/10) | 5.5 (6/7) | **1.25** | 0.066 · 0.075 | 0.33 · 0.41 | 4.8 (2/3) |
| H2_bed_corridor | transit | 3.5 (3/9) | 3.1 (3/6) | **1.21** | 0.066 · 0.075 | 0.23 · 0.24 | 9.1 (1/2) |
| H2_bed_corridor | crowd23 | 4.3 (8/10) | 5.2 (6/7) | **1.45** | 0.066 · 0.075 | 0.28 · 0.39 | 5.1 (1/3) |
| H2_bed_corridor | fight | 3.7 (6/10) | 4.5 (6/7) | **1.45** | 0.066 · 0.075 | 0.25 · 0.34 | 4.1 (2/3) |
| H3_bare_corridor | wall | 2.1 (10/11) | 2.0 (8/9) | **1.18** | 0.052 · 0.055 | 0.11 · 0.11 | 5.6 (1/1) |
| H3_bare_corridor | self | 1.4 (8/11) | 1.3 (7/9) | **1.11** | 0.052 · 0.055 | 0.07 · 0.07 | 2.3 (1/1) |
| H3_bare_corridor | ally_body | 1.5 (8/11) | 1.4 (5/9) | **1.31** | 0.052 · 0.055 | 0.08 · 0.08 | 1.5 (1/1) |
| H3_bare_corridor | trapped | 1.9 (10/11) | 1.8 (8/9) | **1.10** | 0.052 · 0.055 | 0.10 · 0.10 | 3.0 (1/1) |
| H3_bare_corridor | crowd23 | 1.5 (7/11) | 1.3 (6/9) | **1.10** | 0.052 · 0.055 | 0.08 · 0.07 | 1.9 (1/1) |
| H4_portal_mouth | wall | 3.0 (4/10) | 3.0 (4/10) | **1.28** | 0.040 · 0.049 | 0.12 · 0.15 | 6.3 (1/4) |
| H4_portal_mouth | self | 2.3 (5/10) | 2.6 (6/10) | **1.37** | 0.040 · 0.049 | 0.09 · 0.13 | 7.8 (3/4) |
| H4_portal_mouth | ally_body | 6.0 (10/10) | 4.4 (10/10) | **1.04** | 0.040 · 0.049 | 0.24 · 0.21 | 6.7 (4/4) |
| H4_portal_mouth | h2h_ally | 15.3 (10/10) | 14.7 (10/10) | **1.50** | 0.040 · 0.049 | 0.61 · 0.71 | 24.6 (4/4) |
| H4_portal_mouth | trapped | 3.4 (8/10) | 3.3 (8/10) | **1.15** | 0.040 · 0.049 | 0.14 · 0.16 | 7.1 (4/4) |
| H4_portal_mouth | newborn | 3.0 (7/10) | 4.2 (7/10) | **1.59** | 0.040 · 0.049 | 0.12 · 0.20 | 7.7 (4/4) |
| H4_portal_mouth | transit | 23.8 (10/10) | 19.9 (10/10) | **1.12** | 0.040 · 0.049 | 0.95 · 0.97 | 32.6 (4/4) |
| H4_portal_mouth | crowd23 | 4.9 (10/10) | 5.8 (10/10) | **1.42** | 0.040 · 0.049 | 0.20 · 0.28 | 11.0 (4/4) |
| H4_portal_mouth | fight | 4.9 (8/10) | 5.1 (7/10) | **1.25** | 0.040 · 0.049 | 0.19 · 0.25 | 5.0 (4/4) |
| H4_portal_mouth | h2h_enemy | 1.6 (5/9) | 1.2 (5/9) | **0.79** | 0.040 · 0.049 | 0.06 · 0.06 | 1.1 (3/3) |
| H5_portal_approach_beds | h2h_ally | 4.1 (7/7) | 5.0 (7/7) | **1.92** | 0.043 · 0.047 | 0.18 · 0.24 | 6.5 (3/4) |
| H6_bed_pocket | self | 1.7 (4/6) | 2.5 (4/6) | **1.78** | 0.042 · 0.050 | 0.07 · 0.12 | 5.2 (4/4) |
| H6_bed_pocket | ally_body | 2.6 (5/6) | 2.0 (4/6) | **1.10** | 0.042 · 0.050 | 0.11 · 0.10 | 3.2 (4/4) |
| H6_bed_pocket | h2h_ally | 5.0 (4/6) | 5.4 (2/6) | **1.69** | 0.042 · 0.050 | 0.21 · 0.27 | 6.5 (1/2) |
| H6_bed_pocket | trapped | 1.8 (4/6) | 1.6 (4/6) | **1.08** | 0.042 · 0.050 | 0.07 · 0.08 | 3.8 (3/4) |
| H6_bed_pocket | newborn | 2.0 (5/6) | 2.5 (5/6) | **1.39** | 0.042 · 0.050 | 0.09 · 0.12 | 4.4 (4/4) |
| H6_bed_pocket | transit | 2.1 (1/5) | 2.9 (1/5) | **1.83** | 0.042 · 0.050 | 0.09 · 0.15 | 3.1 (0/2) |
| H6_bed_pocket | crowd23 | 2.5 (5/6) | 3.3 (5/6) | **1.57** | 0.042 · 0.050 | 0.11 · 0.16 | 5.1 (4/4) |
| H6_bed_pocket | fight | 1.4 (2/6) | 1.6 (2/6) | **1.32** | 0.042 · 0.050 | 0.06 · 0.08 | 1.9 (3/4) |
| H7_dense_open_cluster | ally_body | 1.7 (6/9) | 1.5 (4/9) | **1.26** | 0.063 · 0.091 | 0.11 · 0.14 | 3.2 (20/22) |
| H7_dense_open_cluster | h2h_enemy | 1.4 (6/8) | 1.3 (7/8) | **0.97** | 0.063 · 0.091 | 0.09 · 0.12 | 2.2 (20/22) |

#### Cell-level Poisson models: leave-one-terrain-out deviance explained (median over the 10 held-out terrains)

| class | field: within-map D² | field: across-map D² | ours: within | ours: across | structure-only field model on the V06 base's gen-map deaths: within-map D² (median, maps) |
|---|---|---|---|---|---|
| wall | 0.84 | 0.86 | 0.72 | 0.75 | 0.62 (10) |
| self | 0.67 | 0.75 | 0.37 | 0.51 | 0.13 (20) |
| ally_body | 0.34 | 0.38 | 0.32 | 0.38 | 0.22 (24) |
| h2h_ally | 0.46 | 0.51 | 0.47 | 0.61 | 0.44 (8) |
| h2h_enemy | 0.04 | 0.18 | 0.04 | 0.21 | – |
| trapped | 0.79 | 0.79 | 0.73 | 0.73 | 0.25 (28) |
| newborn | 0.70 | 0.70 | 0.56 | 0.62 | 0.17 (28) |
| transit | 0.44 | 0.55 | 0.42 | 0.58 | 0.51 (8) |
| crowd23 | 0.60 | 0.67 | 0.39 | 0.51 | 0.22 (26) |
| fight | 0.37 | 0.06 | 0.35 | 0.37 | 0.07 (29) |

#### Our excess per class, split into where we go and how we die there (pool, per 1k head-turns)

| class | ours | field | excess | from exposure mix (where we go) | from rate inside each signature (how we die there) | largest rate term |
|---|---|---|---|---|---|---|
| wall | 9.63 | 7.75 | +1.88 | +0.28 | +1.60 | H1_dead_end +1.22 |
| self | 7.49 | 6.19 | +1.30 | +0.32 | +0.97 | H2_bed_corridor +1.26 |
| ally_body | 3.45 | 2.42 | +1.03 | +0.28 | +0.75 | H2_bed_corridor +0.53 |
| h2h_ally | 2.21 | 1.41 | +0.80 | +0.19 | +0.61 | H2_bed_corridor +0.33 |
| trapped | 22.25 | 18.76 | +3.49 | +1.13 | +2.36 | H2_bed_corridor +2.37 |
| newborn | 12.71 | 11.16 | +1.56 | +0.79 | +0.76 | H2_bed_corridor +1.04 |
| transit | 3.74 | 2.80 | +0.95 | +0.24 | +0.71 | H1_dead_end +0.33 |
| crowd23 | 10.69 | 8.91 | +1.78 | +0.69 | +1.08 | H2_bed_corridor +1.30 |
| fight | 12.21 | 10.30 | +1.91 | +0.41 | +1.50 | H2_bed_corridor +1.29 |

#### Field rate ratios per standard deviation of each structural feature (full-pool Poisson fit, field)

| class | deg1 | deg2 | deg3 | kelp0 | portal2 | bed3 | bed6 | is_bed | cluster_log | spawn_log | region_small | reach5 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| wall | 1.66 | 1.51 | 1.15 | 1.71 | 0.98 | 1.04 | 1.14 | 1.16 | 1.04 | 1.11 | 1.28 | 1.07 |
| self | 1.42 | 1.21 | 0.96 | 1.19 | 1.00 | 1.11 | 1.10 | 1.08 | 1.02 | 1.04 | 1.15 | 1.08 |
| ally_body | 0.90 | 1.26 | 1.04 | 1.19 | 1.23 | 1.16 | 1.28 | 1.14 | 1.08 | 1.06 | 1.16 | 1.20 |
| h2h_ally | 0.94 | 1.22 | 1.02 | 1.16 | 1.83 | 1.24 | 0.94 | 1.11 | 1.12 | 1.03 | 1.12 | 1.15 |
| h2h_enemy | 0.96 | 1.04 | 1.01 | 1.03 | 1.15 | 1.03 | 1.16 | 0.95 | 1.02 | 0.95 | 0.98 | 1.21 |
| trapped | 1.64 | 1.40 | 1.11 | 1.57 | 1.10 | 1.07 | 1.22 | 1.10 | 1.10 | 1.10 | 1.15 | 1.13 |
| newborn | 1.51 | 1.23 | 1.03 | 1.31 | 1.07 | 1.18 | 1.26 | 1.14 | 1.16 | 1.10 | 1.19 | 1.11 |
| transit | 1.38 | 1.29 | 0.98 | 1.26 | 2.44 | 0.99 | 0.80 | 1.37 | 1.05 | 1.04 | 1.26 | 1.53 |
| crowd23 | 1.38 | 1.22 | 1.02 | 1.27 | 1.24 | 1.13 | 1.17 | 1.06 | 1.13 | 1.07 | 1.16 | 1.19 |
| fight | 1.50 | 1.30 | 0.93 | 1.23 | 1.16 | 1.01 | 1.18 | 1.12 | 1.07 | 1.04 | 1.21 | 1.20 |

#### Per-map hazard profile (share of cells carrying each signature; index = expected rate at uniform exposure ÷ the field pool average)

| map | tiles | kelp share | portal cells | contact | H1 | H2 | H3 | H4 | H5 | H6 | H7 | H8 | idx wall | idx self | idx h2h_ally | idx newborn |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| autarky.map | 972 | 0.11 | 32 | 7 | 0.004 | 0.025 | 0.045 | 0.033 | 0.033 | 0.000 | 0.017 | 0.012 | 0.59 | 0.69 | 0.93 | 0.60 |
| default.map | 1024 | 0.11 | 48 | 2 | 0.000 | 0.000 | 0.043 | 0.047 | 0.103 | 0.000 | 0.000 | 0.062 | 0.36 | 0.53 | 1.28 | 0.42 |
| devil.map | 512 | 0.24 | 0 | 31 | 0.000 | 0.199 | 0.070 | 0.000 | 0.000 | 0.039 | 0.016 | 0.172 | 1.29 | 1.28 | 1.35 | 1.34 |
| dilemma.map | 512 | 0.12 | 16 | 14 | 0.008 | 0.023 | 0.055 | 0.031 | 0.000 | 0.000 | 0.031 | 0.027 | 0.76 | 0.78 | 0.79 | 0.71 |
| dilemma_10.map | 512 | 0.12 | 16 | 7 | 0.008 | 0.023 | 0.055 | 0.031 | 0.000 | 0.000 | 0.031 | 0.027 | 0.76 | 0.78 | 0.79 | 0.71 |
| new/mc26_archipelago.map | 1008 | 0.07 | 0 | 29 | 0.000 | 0.000 | 0.020 | 0.000 | 0.000 | 0.008 | 0.064 | 0.054 | 0.13 | 0.43 | 0.23 | 0.30 |
| new/mc26_crossroads.map | 1024 | 0.08 | 0 | 25 | 0.000 | 0.004 | 0.016 | 0.000 | 0.000 | 0.004 | 0.037 | 0.000 | 0.13 | 0.41 | 0.20 | 0.27 |
| new/mc26_delayed_commons.map | 528 | 0.06 | 0 | 17 | 0.000 | 0.000 | 0.008 | 0.000 | 0.000 | 0.008 | 0.068 | 0.000 | 0.09 | 0.41 | 0.21 | 0.28 |
| new/mc26_equatorial_belt.map | 800 | 0.04 | 0 | 7 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.300 | 0.000 | 0.05 | 0.53 | 0.28 | 0.44 |
| new/mc26_far_harbors.map | 1728 | 0.03 | 0 | 39 | 0.000 | 0.000 | 0.002 | 0.000 | 0.000 | 0.000 | 0.051 | 0.000 | 0.08 | 0.39 | 0.16 | 0.25 |
| new/mc26_nursery_bays.map | 768 | 0.08 | 0 | 22 | 0.000 | 0.000 | 0.016 | 0.000 | 0.000 | 0.016 | 0.052 | 0.102 | 0.14 | 0.43 | 0.27 | 0.31 |
| new/mc26_pinwheel.map | 1020 | 0.06 | 0 | 27 | 0.000 | 0.000 | 0.014 | 0.000 | 0.000 | 0.000 | 0.069 | 0.000 | 0.10 | 0.41 | 0.18 | 0.27 |
| new/mc26_portal_quartet.map | 896 | 0.07 | 16 | 15 | 0.000 | 0.000 | 0.018 | 0.018 | 0.042 | 0.000 | 0.094 | 0.000 | 0.18 | 0.47 | 0.61 | 0.34 |
| new/mc26_pulse_farms.map | 396 | 0.07 | 0 | 15 | 0.000 | 0.000 | 0.010 | 0.000 | 0.000 | 0.015 | 0.081 | 0.000 | 0.11 | 0.43 | 0.25 | 0.30 |
| new/mc26_relay_depots.map | 1536 | 0.03 | 16 | 20 | 0.000 | 0.000 | 0.003 | 0.010 | 0.019 | 0.000 | 0.088 | 0.000 | 0.12 | 0.43 | 0.40 | 0.31 |
| new/mc26_scattered_fleets.map | 1260 | 0.04 | 0 | 12 | 0.000 | 0.000 | 0.003 | 0.000 | 0.000 | 0.000 | 0.016 | 0.000 | 0.08 | 0.37 | 0.14 | 0.22 |
| new/mc26_seam_market.map | 1056 | 0.03 | 0 | 7 | 0.000 | 0.000 | 0.004 | 0.000 | 0.000 | 0.000 | 0.061 | 0.000 | 0.08 | 0.40 | 0.16 | 0.26 |
| new/mc26_spring_wells.map | 572 | 0.05 | 0 | 19 | 0.000 | 0.000 | 0.007 | 0.000 | 0.000 | 0.014 | 0.098 | 0.000 | 0.10 | 0.44 | 0.25 | 0.31 |
| new/md26_causeway_detour_s0.map | 768 | 0.06 | 0 | 33 | 0.000 | 0.000 | 0.005 | 0.000 | 0.000 | 0.000 | 0.065 | 0.000 | 0.08 | 0.40 | 0.17 | 0.26 |
| new/md26_causeway_portal_s0.map | 768 | 0.06 | 8 | 12 | 0.000 | 0.000 | 0.005 | 0.010 | 0.031 | 0.000 | 0.088 | 0.000 | 0.13 | 0.43 | 0.44 | 0.30 |
| new/md26_commons_shared_s0.map | 480 | 0.06 | 0 | 17 | 0.000 | 0.008 | 0.008 | 0.000 | 0.000 | 0.042 | 0.192 | 0.000 | 0.16 | 0.56 | 0.48 | 0.48 |
| new/md26_commons_spread_s0.map | 480 | 0.06 | 0 | 17 | 0.000 | 0.000 | 0.017 | 0.000 | 0.000 | 0.000 | 0.283 | 0.000 | 0.09 | 0.53 | 0.29 | 0.44 |
| new/md26_orchard_narrow_s0.map | 720 | 0.07 | 0 | 27 | 0.000 | 0.011 | 0.006 | 0.000 | 0.000 | 0.050 | 0.075 | 0.000 | 0.19 | 0.51 | 0.47 | 0.41 |
| new/md26_orchard_wide_s0.map | 720 | 0.07 | 0 | 27 | 0.000 | 0.011 | 0.006 | 0.000 | 0.000 | 0.039 | 0.086 | 0.000 | 0.18 | 0.51 | 0.42 | 0.40 |
| new/md26_promenade_ring_s0.map | 952 | 0.06 | 0 | 27 | 0.000 | 0.000 | 0.008 | 0.000 | 0.000 | 0.008 | 0.052 | 0.000 | 0.10 | 0.41 | 0.20 | 0.27 |
| portals.map | 512 | 0.28 | 80 | 999 | 0.098 | 0.172 | 0.008 | 0.156 | 0.137 | 0.141 | 0.016 | 0.066 | 5.80 | 3.77 | 3.81 | 4.41 |
| queen_of_spades.map | 875 | 0.17 | 8 | 24 | 0.018 | 0.011 | 0.139 | 0.009 | 0.014 | 0.018 | 0.005 | 0.087 | 1.31 | 1.05 | 0.59 | 0.97 |
| schooltime.map | 2400 | 0.19 | 48 | 7 | 0.033 | 0.026 | 0.154 | 0.020 | 0.004 | 0.009 | 0.018 | 0.077 | 2.13 | 1.52 | 0.80 | 1.55 |
| slithery_fight.map | 1701 | 0.15 | 8 | 4 | 0.020 | 0.088 | 0.065 | 0.005 | 0.007 | 0.034 | 0.089 | 0.020 | 1.61 | 1.36 | 0.89 | 1.41 |
| trauma.map | 1152 | 0.24 | 24 | 98 | 0.033 | 0.023 | 0.276 | 0.021 | 0.000 | 0.002 | 0.000 | 0.092 | 2.33 | 1.61 | 0.84 | 1.57 |
| trophy.map | 625 | 0.07 | 4 | 9 | 0.002 | 0.003 | 0.070 | 0.006 | 0.018 | 0.000 | 0.022 | 0.005 | 0.34 | 0.52 | 0.39 | 0.36 |
| var/autarky_tr.map | 972 | 0.11 | 32 | 7 | 0.004 | 0.025 | 0.045 | 0.033 | 0.033 | 0.000 | 0.017 | 0.012 | 0.59 | 0.69 | 0.93 | 0.60 |
| var/crossroads_tr.map | 1024 | 0.08 | 0 | 25 | 0.000 | 0.004 | 0.016 | 0.000 | 0.000 | 0.004 | 0.037 | 0.000 | 0.13 | 0.41 | 0.20 | 0.27 |
| var/default_tr.map | 1024 | 0.11 | 48 | 2 | 0.000 | 0.000 | 0.043 | 0.047 | 0.103 | 0.000 | 0.000 | 0.062 | 0.36 | 0.53 | 1.28 | 0.42 |
| var/devil_tr.map | 512 | 0.24 | 0 | 31 | 0.000 | 0.199 | 0.070 | 0.000 | 0.000 | 0.039 | 0.016 | 0.172 | 1.29 | 1.28 | 1.35 | 1.34 |
| var/dilemma_tr.map | 512 | 0.12 | 16 | 14 | 0.008 | 0.023 | 0.055 | 0.031 | 0.000 | 0.000 | 0.031 | 0.027 | 0.76 | 0.78 | 0.79 | 0.71 |
| var/portals_tr.map | 512 | 0.28 | 80 | 999 | 0.098 | 0.172 | 0.008 | 0.156 | 0.137 | 0.141 | 0.016 | 0.066 | 5.80 | 3.77 | 3.81 | 4.41 |
| var/queen_of_spades_tr.map | 875 | 0.17 | 8 | 24 | 0.018 | 0.011 | 0.139 | 0.009 | 0.014 | 0.018 | 0.005 | 0.087 | 1.31 | 1.05 | 0.59 | 0.97 |
| var/trauma_tr.map | 1152 | 0.24 | 24 | 98 | 0.033 | 0.023 | 0.276 | 0.021 | 0.000 | 0.002 | 0.000 | 0.092 | 2.33 | 1.61 | 0.84 | 1.57 |
| var/trophy_tr.map | 625 | 0.07 | 4 | 9 | 0.002 | 0.003 | 0.070 | 0.006 | 0.018 | 0.000 | 0.022 | 0.005 | 0.34 | 0.52 | 0.39 | 0.36 |

## Readings

- **What is specific to us** is our ÷ field ≥ 1.4 in the same cells, stable across terrains:
  - own-side collisions (own body, ally body, ally head-on, crowd23) in **bed corridors (H2)** and **bed pockets (H6)**;
  - ally head-on and newborn deaths at **portal mouths (H4)** and **one step before them inside bed clusters (H5)**.

  All four are the places where several of our dragons want the same bed through a one- or two-wide opening. This is
  the structural form of the C1-C "crowd" and "portal-exit" leaks (L05, L06, L23). It adds one fact the ledger did
  not have: about a quarter to a half of the excess is that we *go there more* (see the decomposition table).
- **What is hazardous for everyone** is dead-end tips (H1) and, far less, bare corridors (H3). A newborn or a trapped
  dragon in a cul-de-sac dies there at 25–46× the pool rate whoever controls it. Our wall rate at the tips is
  1.37× the field's, and it is the literal Autarky leak (Part 1). Everything else about H1 we already do better than
  the field.
- **No signature explains the losing maps.** Part 1's losing maps (Prisoners Dilemma, Autarky, Trophy, Queen Of Spades)
  are losses of opening economy, and their hazard indices are unremarkable (see the profile table). The signatures are
  the right object for length retention and for the leak lanes. They are not the lever for the residual on those
  maps. That is a claim for M-1 to test against its brick list: bricks by *economy* percentile should not cluster on
  these signature profiles, but bricks by *hygiene* percentile should.

## Proposed ledger rows (one per signature; weights are first estimates)

| Row | Claim | Weight |
|---|---|---|
| K1-H1 | Dead-end tips kill everyone (×25–46); our wall excess there (×1.37) is a hygiene leak, not a strategy gap | 0.7 (measured; fixing it is a hygiene gain, win value low) |
| K1-H2 | Own-side collisions in bed corridors are our specific leak (×1.45–1.64 over the field in the same cells); part of it is exposure (we are in them 14 % more) | 0.7 |
| K1-H4/H5 | Ally head-on at portal mouths and their bed-cluster approach is ours ×1.5–1.9; a "one dragon per mouth" claim rule is the candidate mechanism (L23 is its nearest ancestor) | 0.6 |
| K1-H6 | Bed pockets (a bed-rich cell with a kelp side) raise our own-body and crowd deaths ×1.6–1.8 over the field | 0.5 (6 terrains only) |
| K1-H7 | Dense open bed clusters are the gen maps' main crowding hazard (V06: ally body ×3.2, 59 % of those deaths) | 0.4 (V06 only; no field data on gen) |
| K1-H8 | Small rooms are not a hazard once corridors and dead ends are accounted for | 0.6 (null, a control) |
| K1-gen | The generalisation panel lacks the pool's corridor, dead-end and portal hazards (H1 0/20, H2 ≤ 1.1 %, H4 3/20); gen-panel passes do not test them | 0.9 (a count) |

## Handoff — Parts 3 and 4 (not started; they need the desktop and a Claude Code session)

- **Targets for the isolation families** (real-map intensity = pool median share of cells; heavy = pool max):

  | signature | light | real | heavy |
  |---|---|---|---|
  | H1 | 0.005 | 0.013 | 0.10 |
  | H2 | 0.01 | 0.024 | 0.20 |
  | H4 | 0.01 | 0.02 | 0.16 |
  | H5 | 0.005 | 0.01 | 0.14 |
  | H6 | 0.003 | 0.005–0.03 | 0.14 |
  | H7 | 0.01 | 0.016 | 0.09 on the pool; the gen maps already reach 0.30 |

  Score candidates with `python tools/sophie/hazard.py profile <map>`. It prints the share per signature and a
  per-class hazard index from `docs/findings/data/sophie-K1-signature-ratios.json`.
- **Validation target per family:** the base's death rate for the targeted class inside the signature cells should
  match the ratios in the table above (field and ours columns) within ±30 %, and the untargeted classes should stay
  near `_rest` levels (`sophie-K1-signatures.json`, key `_rest`).
- **Composition families named in the brief:** Slithery = H2 + H7 (0.088 + 0.089); Portals = H1 + H2 + H4 + H5 + H6 (all at
  pool max); Schooltime = H3 + H1 at moderate density with large open regions. Missing from the pool: H4 without H1 (portals on open
  ground), and H2 at Devil density without H8.
- **Part 4 demonstration pick:** the most damaging signature *specific to us* is H2 (the largest our-÷-field on the
  own-side classes, with the largest share of our deaths: 35–43 %). The mechanism the ledger already points at is the
  crowd rule on beds reached through corridors (L10's refuse-contact and L23's claim packet). The single weight to tune
  on the H2 isolation family is whichever ally-proximity or crowding weight on corridor bed targets Ares exposes
  (check SF-1's feature interface for the exact parameter; none was verified from here). The real-map test is D-032 plus the
  per-signature delta.
