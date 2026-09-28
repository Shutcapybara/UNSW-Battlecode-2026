# ouroboros-s02-econ (the "all mechanisms" arm; a benchmark, not a candidate)

Claude, Ouroboros lineage, S2. The code is the same as `ouroboros-s02-portal`, with the economy and exploration
switches on:

- **Atlas beds.** A never-seen bed is worth max(v_unseen, v_bed × P(first countdown ≤ arrival)), with the countdown
  ~U[min_gap, max_gap] from the map file.
- **Atlas far target.** When nothing is in the search, go to the best expected bed: the top 3 rotate by id, with
  hysteresis.
- **Fast-bed pre-wait.** A bed with mean gap ≤ 10 that is due within 3 rounds of arrival keeps its value.
- **Contested sprints.** 2-step sprints to confirmed pearls that are contested (an enemy head within 2) or that eat
  two pearls. `v_contest` 2.0 per contested pearl eaten.
- **Contested appetite.** `enemy_disc` 0.6 → 0.85.
- **Portal exploration.** A stale paired-portal landing is a `v_explore` 3.0 target on maps with ≥ 6 pairs.

Markers: `ACT:bed`, `ACT:far`, `ACT:sprint`, `ACT:dive` and `ACT:probe`. `ACT:bed` fires only when the bed odds,
not plain exploration, set the value.

## Result

Seed 1, unswbc 1.2.2, 120 fixtures vs fenrir-v18: **−0.013** (17 better / 19 worse, p = 0.87). Median Δ total r250
is −2 and Δ units r100 is −1, so the **H-econ falsifier fires**.

The economy did move pearls:

- **Pearls eaten in r0–100** (seeded replays of the portal-risk dev variant, which is equivalent): Portals 144 vs
  94, Queen of Spades 40 vs 24, Default 36 vs 27.
- **Opponents' intake fell** on the same maps: Portals 73 vs 83, Queen of Spades 15 vs 25.

The extra intake was lost to churn. On Queen of Spades, deaths rose from 68 to 101 per game: forced wall deaths
22 → 35, ally-body deaths 6 → 12. Economy without portal safety (`ouroboros-s02-arm-econ`) is **−0.196** (9/32,
p < 0.001). The atlas-driven intake then turns into portal-step and crowding deaths.

The first cut (`ouroboros-s02x-firstcut`) valued never-seen beds by their bed odds alone. That collapsed
exploration on maps where most tiles are slow beds: Trophy and Queen of Spades, −0.46 on 24 pairs there.
