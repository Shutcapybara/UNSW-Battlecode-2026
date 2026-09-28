# F1 features: definitions, units, sources, validation

Registry version 1, frame version 5 (29 Sep 2026, `claude/analysis/F1`). This file is generated: the header below by hand and
the tables by `python -m tools.analysis.features registry`. Code: `tools/analysis/features/`.

## Input contract and outputs

`python -m tools.analysis.features extract <replay|dir|glob …> --out DIR [--index index.jsonl] [--cache DIR] [--jobs N]`
takes replay paths only. It runs unchanged on local games and on `public_replays/corpus/replays/*.replay`. The optional index
adds seed and toolkit by game id. Outputs in `DIR`:

| file | unit | contents |
|---|---|---|
| `features.parquet` | side-game | every registered feature, plus context: map, map class, `map_hash` (orientation), side, bot, opponent, result, reason, rounds, seed, toolkit |
| `series.parquet` | side-round | per-round state (units, total, longest, concentration, newly seen cells, contact share, density ratio) and events (eats by origin, splits, deaths by class, rays by direction, aim and hit kind, sprint cost) |
| `samples.parquet` | side-round, every 5 rounds | territory, bed territory, contested bed share, EPG access for τ = 1, 2, 4, reach, enclosed share, bed eats in the next 10 rounds |
| `dragons.parquet` | dragon | born, died, cause, lifetime, max length, radius of gyration, density ratio, contact share, rays per turn, eats per 100 turns, sprint share |
| `deaths.parquet` | death | class, length, age, reach at the start of the death round (dynamic and terrain-only), enclosed flag, near-portal flag, killer team |
| `exposure.parquet` | side × reach | sampled dragon-turns per reach value (the denominator of the enclosure hazard) |
| `checks.parquet` | identity × side-game | V0 residuals (0 = pass) |

`python -m tools.analysis.features.report --run DIR --out REPORT` builds the aggregate tables and the interactive report:
`quantiles.csv` (feature × map or ALL × win, loss or all; 10/25/50/75/90 per map, 5/25/50/75/95 pooled),
`strength.csv`, `stability.csv`, `identity.csv`, `flags.csv`, `phases.parquet`, `hmm.json`, `validation.json`, `report.html`.

## Conventions

- Rounds are the replay's round index. The helper's `game.get_round_num()` reports the same number: the V1 splitter probe splits on
  replay rounds 0, 20, 40, and so on.
- "At round c" means the start-of-round snapshot. After the game ends, the terminal state is carried forward, so an eliminated
  side has 0 units at r499, and no survivor-only medians are taken.
- Rates are per dragon-turn (the sum over rounds of living dragons), so population size cancels.
- Shares against the opponent are ours / (ours + theirs). Map normalisation uses the nominal bed rate λ = 2/(minGap + maxGap) from
  `TILE x y minGap maxGap`. Capacity is Σλ.
- Distances are terrain BFS: kelp edges block, portals connect. Bodies are ignored for territory and block for reach.
- Death classes and credit:
  - `wall` and `invalid` have no killer.
  - `self` is a hit on the own body.
  - `ally_body` / `enemy_body` are credited to the owner of the body hit.
  - `h2h_*` is credited to the other head (both heads die when heads collide).
  - `suicide` is a deliberate suicide action, whatever cause the engine records.
- Sprint cost is measured, not assumed. The engine charges each extra step as it is taken, so a dragon that dies mid-sprint has
  paid only for the steps it completed. (V0 caught the naive `k − 1`.)
- Sonar direction is the physical direction of travel. A ray aimed into the sender's own neck exits through the tail and is
  recorded in the tail's direction, so compass shares count only rays that left the head, and `ray_refracted_share` counts the
  rest. (V1 caught this.) A sender that dies during its move casts nothing.

## Validation ladder

Each feature carries the most direct check that applies to it.

- **V0 bookkeeping.** These identities hold exactly on every side-game:
  - length conservation: end = start + pearls − sprint cost − length lost;
  - the decoded final state matches the engine result;
  - corpse drops equal ⌈L/2⌉;
  - territory sums to 1;
  - sprint payments stay within bounds.
- **V1 probe bots** (`tools/analysis/features/probes/`, `probe_check.py`). Two bots fix known values:
  - `probe-northsonar` sends one north ray per turn and never splits or sprints;
  - `probe-silent-splitter` sends no sonar and splits a 2-segment child on rounds divisible by 20.

  The features must return those values on four maps.
- **V2 reliability.** ICC over seeds 1–3 of the same fixture (four pairs × ten maps × two seats). Seeded games are byte-identical
  across machines: the same replay md5 came from the cloud workspace and the Mac VM.
- **V3 proximal targets.**
  - EPG access → bed eats in the next 10 rounds.
  - Bed territory and contested share → our share of the next bed pearls.
  - Reach → death hazard.
  - Density ratio → a dragon's pearls per 100 turns.
- **V4 own-bot logs.** Not yet used: the z1 panel was mostly run with `--no-logs`.
- **V5 toggle tests.** Not yet run.
- **V6 outcome, Elo and field gap.** Within-map AUC for winning (`strength.csv`) now; Elo and the field comparison come with A2.

## Phases

`phases.py` gives three views of each side-game. Signals are per living dragon, in 5-round bins, standardised over the corpus:
`explore` (new cells seen / 49 per dragon), `produce`, `eat`, `contact`, `die` and `concentrate` (longest / total).

1. **Rule markers.**
   - t1 is when the 10-round mean discovery rate falls below 25% of its peak.
   - t2 is when 90% of the side's splits are done and concentration is above its median for the rest of the game.
2. **Exact least-squares changepoints.** A K = 2 fit, plus a BIC-selected K from 0 to 3.
3. **The primary detector: a pooled left-to-right 3-state Gaussian HMM.**
   - It is fitted by EM over all seed-1 side-games, initialised from the rule markers, and decoded by Viterbi.
   - States are named by their fitted signature (`hmm.json`).
   - `phase_t1` and `phase_t2` come from it, and per-phase rates (`opening_*`, `economy_*`, `crown_*`) are computed inside its
     segments.

## Known limitations

- EPG, territory and density use the nominal bed rate. Realised spawns are suppressed while a bed is occupied or already holds a
  pearl.
- The seen share assumes a square 7×7 view that ignores walls.
- Kills are not credited for wall deaths caused by pressure.
- Aim relative to the allied centre is ambiguous for single dragons (counted as neither toward nor away).
- `first_contact` is map-locked: the start layout decides it on most maps.
- Raw counts at checkpoints are map-dominated by construction; compare the share or rate versions across maps.

### compute

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `tle` | turns | turns over the time limit | events | V2,V6 |  |

### concentration

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `top1_share@{c}` | share | longest / total at c (crown concentration) | snapshots | V2,V6 |  |
| `len_gini@{c}` | gini | Gini of dragon lengths at c (0 for one dragon) | snapshots | V2,V6 |  |
| `small_share@{c}` | share | share of dragons with length <= 3 (c in 100, 250) | snapshots | V2,V6 |  |
| `big_share@{c}` | share | share of dragons with length >= 10 (c in 100, 250) | snapshots | V2,V6 |  |

### context

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `dragon_turns` | dragon-turns | sum over rounds of living dragons | events | V2,V6 |  |

### economy

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `pearls@{c}` | pearls | cumulative pearls eaten by round c (any origin) | TileChange | V2,V6 |  |
| `bed_pearls@{c}` | pearls | cumulative bed pearls eaten by round c | TileChange + origin | V2,V6 |  |
| `bed_expected_share@{c}` | share of capacity | sum over beds of rate x logistic(distance advantage), / capacity | snapshots + TILE | V3 | bed pearl share next |
| `density_ratio@{c}` | ratio | mean over our heads of bed rate in the 7x7 view / map-average view rate | snapshots + TILE | V1,V3 | eats per dragon-turn |
| `first_pearl` | round | first pearl eaten | events | V2,V6 |  |
| `pearls_per100dt_0_100` | per 100 dragon-turns | pearls eaten per 100 dragon-turns, rounds 0-99 | events | V2,V6 |  |
| `pearls_per100dt_100_250` | per 100 dragon-turns | same, rounds 100-249 | events | V2,V6 |  |
| `pearls_per100dt_250_500` | per 100 dragon-turns | same, rounds 250-499 | events | V2,V6 |  |
| `pearls` | pearls | pearls eaten, whole game | events | V0,V2,V6 |  |
| `pearls_bed_share` | share | share of our pearls from beds | events | V2,V6 |  |
| `pearls_ally_corpse_share` | share | share from our own corpses | events | V2,V6 |  |
| `pearls_enemy_corpse_share` | share | share from enemy corpses | events | V2,V6 |  |
| `bed_capture_share` | share of spawns | our bed eats / all bed spawns in the game | events | V2,V6 |  |
| `bed_capacity_yield` | share of capacity | our bed eats / (nominal capacity x rounds) | events | V2,V6 |  |
| `corpse_recovered_share` | share of drops | pearls from our corpses eaten by us / ceil(L/2) dropped | events | V0,V2,V6 |  |
| `corpse_lost_share` | share of drops | pearls from our corpses eaten by them / dropped | events | V0,V2,V6 |  |
| `density_ratio_mean` | ratio | mean over rounds of density_ratio | events | V2,V6 |  |
| `epg_tau1` | pearls | expected pearl gain: sum_r sum_beds rate x exp(-d/1), d = our nearest head, sampled every 5 rounds x5 | events | V2,V6 |  |
| `epg_tau2` | pearls | EPG with tau 2 | events | V2,V6 |  |
| `epg_tau4` | pearls | EPG with tau 4 | events | V2,V6 |  |
| `epg_conversion` | ratio | bed pearls eaten / epg_tau2 (positioning vs conversion) | events | V2,V6 |  |
| `bed_expected_share_mean` | share | mean contested bed share | events | V2,V6 |  |

### endgame

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `first_len10` | round | first round our longest >= 10 | events | V2,V6 |  |
| `first_len20` | round | first round our longest >= 20 (crown) | events | V2,V6 |  |
| `first_len30` | round | first round our longest >= 30 | events | V2,V6 |  |
| `leader_changes` | count | times our longest dragon changed identity | events | V2,V6 |  |
| `crown20` | round | alias of first_len20 | events | V2,V6 |  |
| `longest_margin_end` | segments | our longest - theirs at the end | events | V2,V6 |  |
| `total_margin_end` | segments | our total - theirs at the end | events | V2,V6 |  |
| `close_end` | flag | round-limit game with |longest margin| <= 3 | events | V2,V6 |  |

### fighting

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `kills@{c}` | dragons | cumulative enemy deaths credited to us by round c (they hit our body / h2h with us) | DragonDeath + mover | V2,V6 |  |
| `first_contact` | round | first round an enemy body is in any of our 7x7 views | events | V2,V6 |  |
| `kills_per1k` | per 1k own dragon-turns | enemy deaths credited to us | events | V2,V6 |  |
| `kill_length` | segments | enemy length destroyed by our credit | events | V2,V6 |  |
| `kill_length_ratio` | share | kill_length / (kill_length + length_lost) | events | V2,V6 |  |
| `contact_share_mean` | share | mean share of our dragons with an enemy in view | events | V2,V6 |  |

### material

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `units@{c}` | dragons | living dragons of this side at the start of round c (terminal state carried forward) | snapshots | V0,V2,V6 |  |
| `total@{c}` | segments | summed length of this side at round c | snapshots | V0,V2,V6 |  |
| `longest@{c}` | segments | longest dragon of this side at round c | snapshots | V0,V2,V6 |  |
| `units_share@{c}` | share | ours / (ours + theirs) living dragons at c | snapshots | V2,V6 |  |
| `total_share@{c}` | share | ours / (ours + theirs) total length at c | snapshots | V2,V6 |  |
| `longest_share@{c}` | share | ours / (ours + theirs) longest length at c | snapshots | V2,V6 |  |
| `first_lead_total` | round | first round our total exceeds theirs | events | V2,V6 |  |
| `lead_changes_total` | count | sign changes of total-length difference | events | V2,V6 |  |
| `lead_changes_longest` | count | sign changes of longest-length difference | events | V2,V6 |  |
| `max_drawdown_total` | segments | largest fall of total length from its running peak | events | V2,V6 |  |

### movement

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `sprint_cost_per_pearl` | segments per pearl | segments paid for sprints / pearls eaten | events | V0,V2,V6 |  |
| `sprint_share` | share of moves | moves with 2+ steps | events | V1,V2,V6 |  |

### phase

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `phase_t1` | round | opening -> economy transition, pooled left-to-right HMM (phases.py) | events | V2,V6 |  |
| `phase_t2` | round | economy -> crown transition, HMM (NaN = never reached) | events | V2,V6 |  |
| `opening_rounds` | rounds | duration of the opening phase (HMM) | events | V2,V6 |  |
| `opening_pearls_per100dt` | per 100 dragon-turns | pearls eaten inside the opening phase | events | V2,V6 |  |
| `opening_deaths_per1k` | per 1k dragon-turns | own deaths inside the opening phase | events | V2,V6 |  |
| `opening_splits_per100dt` | per 100 dragon-turns | splits inside the opening phase | events | V2,V6 |  |
| `opening_rays_per_dt` | rays per dragon-turn | sonar rays inside the opening phase | events | V2,V6 |  |
| `economy_rounds` | rounds | duration of the economy phase (HMM) | events | V2,V6 |  |
| `economy_pearls_per100dt` | per 100 dragon-turns | pearls eaten inside the economy phase | events | V2,V6 |  |
| `economy_deaths_per1k` | per 1k dragon-turns | own deaths inside the economy phase | events | V2,V6 |  |
| `economy_splits_per100dt` | per 100 dragon-turns | splits inside the economy phase | events | V2,V6 |  |
| `economy_rays_per_dt` | rays per dragon-turn | sonar rays inside the economy phase | events | V2,V6 |  |
| `crown_rounds` | rounds | duration of the crown phase (HMM) | events | V2,V6 |  |
| `crown_pearls_per100dt` | per 100 dragon-turns | pearls eaten inside the crown phase | events | V2,V6 |  |
| `crown_deaths_per1k` | per 1k dragon-turns | own deaths inside the crown phase | events | V2,V6 |  |
| `crown_splits_per100dt` | per 100 dragon-turns | splits inside the crown phase | events | V2,V6 |  |
| `crown_rays_per_dt` | rays per dragon-turn | sonar rays inside the crown phase | events | V2,V6 |  |

### production

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `births@{c}` | dragons | cumulative splits (children born) by round c | DragonSplit | V2,V6 |  |
| `first_split` | round | first split | events | V2,V6 |  |
| `last_split` | round | last split (production stop) | events | V2,V6 |  |
| `peak_units` | dragons | max living dragons | events | V2,V6 |  |
| `peak_units_round` | round | round of peak living dragons | events | V2,V6 |  |
| `splits_0_50` | splits | splits in rounds 0-49 | events | V1,V2,V6 |  |
| `splits_50_100` | splits | splits in rounds 50-99 | events | V1,V2,V6 |  |
| `splits_100_250` | splits | splits in rounds 100-249 | events | V1,V2,V6 |  |
| `splits_250_500` | splits | splits in rounds 250-499 (NaN if game ended) | events | V2,V6 |  |
| `births` | dragons | children born | events | V1,V2,V6 |  |
| `newborn_deaths10_per100` | per 100 births | children dying within 10 rounds of birth | events | V2,V6 |  |
| `child_len_median` | segments | median child length at split | events | V1,V2,V6 |  |
| `child_len_le3_share` | share | share of children of length <= 3 | events | V1,V2,V6 |  |

### risk

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `enclosed_share@{c}` | share of dragons | share of our dragons with <= 15 cells reachable in 5 steps (bodies block) | snapshots + terrain | V3 | death within 3 rounds |
| `reach_mean@{c}` | cells | mean cells reachable in 5 steps from our heads (max 61 on open ground) | snapshots + terrain | V3 | death within 3 rounds |
| `enclosed_share_mean` | share | mean enclosed share over samples | events | V2,V6 |  |
| `enclosed_death_share` | share of deaths | share of non-suicide deaths with reach5 <= 15 at round start | events | V2,V6 |  |
| `death_rate_enclosed_per1k` | per 1k enclosed dragon-turns | deaths while enclosed / enclosed exposure | events | V2,V6 |  |
| `death_rate_open_per1k` | per 1k open dragon-turns | deaths while open / open exposure | events | V2,V6 |  |
| `portal_death_share` | share of deaths | deaths within 2 steps of a portal cell | events | V2,V6 |  |

### sonar

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `rays_per_dt` | rays per dragon-turn | sonar rays sent | events | V1,V2,V6 |  |
| `rays_per_dt_0_100` | rays per dragon-turn | rounds 0-99 | events | V2,V6 |  |
| `rays_per_dt_100_250` | rays per dragon-turn | rounds 100-249 | events | V2,V6 |  |
| `rays_per_dt_250_500` | rays per dragon-turn | rounds 250-499 | events | V2,V6 |  |
| `rays_toward_com_share` | share of rays | ray direction points toward the circular mean of other allied heads | events | V2,V6 |  |
| `rays_away_com_share` | share of rays | points away from allied centre | events | V2,V6 |  |
| `rays_side_com_share` | share of rays | perpendicular to allied centre | events | V2,V6 |  |
| `rays_toward_enemy_share` | share of rays | points toward the nearest enemy head (analyst knowledge) | events | V2,V6 |  |
| `rays_away_enemy_share` | share of rays | points away from nearest enemy head | events | V2,V6 |  |
| `ray_hit_kelp_share` | share of rays | ray stopped on kelp | events | V2,V6 |  |
| `ray_hit_ally_share` | share of rays | stopped on ally body | events | V2,V6 |  |
| `ray_hit_ally_head_share` | share of rays | stopped on ally head | events | V2,V6 |  |
| `ray_hit_enemy_share` | share of rays | stopped on enemy body | events | V2,V6 |  |
| `ray_hit_enemy_head_share` | share of rays | stopped on enemy head | events | V2,V6 |  |
| `ray_hit_empty_share` | share of rays | reached nothing | events | V2,V6 |  |
| `ray_leak_share` | share of rays | rays received by an enemy dragon | events | V2,V6 |  |
| `ray_refracted_share` | share of rays | rays aimed into the own neck that left through the tail | events | V1,V2,V6 |  |
| `rays_N_share` | share of head rays | north, among rays that left the head | events | V1,V2,V6 |  |
| `rays_E_share` | share of rays | east | events | V1,V2,V6 |  |
| `rays_S_share` | share of rays | south | events | V1,V2,V6 |  |
| `rays_W_share` | share of rays | west | events | V1,V2,V6 |  |

### space

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `seen_share@{c}` | share of cells | share of map cells that were inside some 7x7 view of ours by round c | snapshots | V1,V2,V6 |  |
| `visited_share@{c}` | share of cells | share of map cells our heads stood on by round c | snapshots | V1,V2,V6 |  |
| `territory@{c}` | share of cells | cells strictly nearer (terrain BFS, portals, kelp) to our heads than theirs, ties half (c in 50,100,250) | snapshots + terrain | V0,V3 | share of pearls eaten next |
| `bed_territory@{c}` | share of capacity | territory weighted by nominal bed rate 2/(min+max) | snapshots + TILE | V3 | bed pearl share next |
| `seen50` | round | round we had seen 50% of cells | events | V2,V6 |  |
| `seen90` | round | round we had seen 90% of cells | events | V2,V6 |  |
| `territory_mean` | share of cells | mean territory over samples | events | V0,V2,V6 |  |

### survival

| feature | unit | definition | source | validation | proximal target |
|---|---|---|---|---|---|
| `deaths@{c}` | dragons | cumulative deaths by round c | DragonDeath | V2,V6 |  |
| `first_death` | round | first own death | events | V2,V6 |  |
| `deaths_per1k` | per 1k dragon-turns | own deaths | events | V2,V6 |  |
| `death_wall_per1k` | per 1k dragon-turns | moved into kelp/wall | events | V2,V6 |  |
| `death_self_per1k` | per 1k dragon-turns | hit own body | events | V2,V6 |  |
| `death_ally_body_per1k` | per 1k dragon-turns | hit an ally body | events | V2,V6 |  |
| `death_enemy_body_per1k` | per 1k dragon-turns | hit an enemy body | events | V2,V6 |  |
| `death_h2h_enemy_per1k` | per 1k dragon-turns | head-to-head with enemy | events | V2,V6 |  |
| `death_h2h_ally_per1k` | per 1k dragon-turns | head-to-head with ally | events | V2,V6 |  |
| `death_suicide_per1k` | per 1k dragon-turns | deliberate suicide action | events | V2,V6 |  |
| `death_invalid_per1k` | per 1k dragon-turns | no valid action | events | V2,V6 |  |
| `length_lost` | segments | own length lost to deaths | events | V0,V2,V6 |  |
| `alive_end` | dragons | living dragons at the end | events | V2,V6 |  |
| `lifetime_median` | rounds | median dragon lifetime (censored at end) | events | V2,V6 |  |
