---
id: S1-Q4-portals-own-goals
author: s1
kind: observation
question: Portals and own goals, by cohort and map — transits, per-transit survival, exit-side deaths, same-pair doubles, blind landings
evidence: s1 corpus store, 40,593 games; transits 0–150: top-10 719k, r11–30 821k, r31–50 273k, us 28k; local renoir-00-base (Ares V06 base, pool) 3.9k
queries: python3 tools/s1/q4.py tables | figs   → build/s1/out/q4/*_r150.csv, *_r500.csv; docs/findings/s1-figs/q4/q4-portals-owngoals-r{150,500}.png
---

## Answer

- **Our portal leak is exits into our own traffic, not blind landings.** In rounds 0–150:
  - A transit of ours ends in death within 3 rounds **27.9 %** of the time, against the top ten's 20.1 %.
  - It ends in death on the transit move itself **13.2 %** vs 6.9 %, twice the rate.
  - We are worse on 8 of 10 maps.
- **Where the excess sits:**
  - **Landings into cells our own dragons can see:** died-3 0.329 vs 0.209.
  - **Same-pair doubles:** 0.374 vs 0.284.
  - **Newborn transits:** 0.414 vs 0.251.
  - **Blind landings are *not* worse** (0.207 vs 0.189).
- **Ally head-on deaths are a portal phenomenon for everyone.** 93–99 % of them happen within 2 steps of a portal, and
  ~46 % within 3 rounds of a transit. Ours run at **2.09 per 1k dragon-turns vs 1.05** (Portals map: 12.5 vs 4.5).
- **Own goals as a whole are 1.75× the top ten's** (24.3 vs 13.8 per 1k by r150). Part of the top ten's advantage is
  **choosing** deaths: 4.6 suicides + 2.1 invalid-action deaths per 1k, against our 0.0 and 0.4. Their chosen deaths are
  counted outside the wall/self/ally classes.
- **The current submission (`us_now`, since 29 Sep 06:00 UTC) has the same leak:**
  - died-3 0.299, seen-landing died-3 0.344, doubles 0.401, ally head-on 2.13 per 1k.
  - The local Ares V06 base matches our live profile: died-3 0.278, same-move 0.137, seen 0.309, doubles 0.328, ally
    head-on 1.79.

## Per transit (rounds 0–150, pooled maps)

| | top10 | r11–30 | r31–50 | us | us_now | local V06 base |
|---|---|---|---|---|---|---|
| transits | 719,133 | 820,522 | 273,075 | 28,264 | 9,047 | 3,914 |
| died on the transit move | **0.069** | 0.106 | 0.135 | **0.132** | 0.134 | 0.137 |
| died within 3 rounds | **0.201** | 0.249 | 0.254 | **0.279** | 0.299 | 0.278 |
| died within 10 rounds | 0.307 | 0.376 | 0.379 | 0.422 | | 0.417 |
| blind landing share | 0.394 | 0.376 | 0.383 | 0.407 | | 0.352 |
| died-3, blind landing | 0.189 | 0.193 | 0.176 | 0.207 | 0.229 | 0.222 |
| died-3, **seen** landing | **0.209** | 0.282 | 0.302 | **0.329** | 0.344 | 0.309 |
| same-pair double share | 0.182 | 0.218 | 0.203 | 0.232 | | 0.233 |
| died-3, double | 0.284 | 0.334 | 0.369 | 0.374 | 0.401 | 0.328 |
| died-3, single | 0.182 | 0.225 | 0.224 | 0.250 | | 0.263 |
| died-3, newborn (age ≤ 10) | **0.251** | 0.314 | 0.312 | **0.414** | | 0.393 |
| contested (enemy on the pair ±2 rounds) | 0.014 | 0.014 | 0.018 | 0.015 | | 0.016 |

- Whole game (0–500), top ten vs us: same-move 0.092 vs 0.163, died-3 0.257 vs 0.330, seen 0.255 vs 0.360, doubles
  0.347 vs 0.400, newborn 0.323 vs 0.468. Blind is still equal (0.262 vs 0.271).
- **Definitions:**
  - A *seen* landing's exit cell was inside some 7×7 view of the side at round start, i.e. near our own dragons.
  - A *double* is another of our dragons through the same pair within ±2 rounds.

**Died within 3 rounds of a transit, by map (0–150):**

| map | top10 | us |
|---|---|---|
| Autarky | 0.063 | 0.096 |
| Default | 0.095 | 0.140 |
| Portals | 0.418 | 0.436 |
| PD | 0.039 | 0.066 |
| PD 10 | 0.051 | 0.094 |
| QoS | 0.262 | 0.341 |
| Schooltime | 0.094 | 0.162 |
| Slithery | 0.202 | 0.289 |
| Trauma | 0.042 | **0.040** |
| Trophy | 0.231 | 0.354 |

Trauma is the only map where we are level or better.

## Per side-game rates (rounds 0–150, per 1k dragon-turns)

| | top10 | r11–30 | r31–50 | us | local V06 base |
|---|---|---|---|---|---|
| transits | 14.0 | 13.4 | 9.5 | 13.5 | 11.6 |
| post-transit deaths (≤ 3 rounds) | 2.63 | 2.95 | 1.98 | **3.47** | 3.07 |
| near-portal deaths (≤ 2 steps) | 4.94 | 5.60 | 4.05 | **6.50** | 5.68 |
| **own goals** | **13.8** | 21.6 | 20.0 | **24.3** | 21.9 |
| wall | 5.3 | 12.5 | 10.2 | 11.9 | 11.2 |
| self | 3.8 | 4.8 | 5.9 | 6.8 | 5.6 |
| ally body | 1.6 | 3.0 | 2.7 | 3.1 | 3.3 |
| ally head-on | **1.05** | 1.27 | 1.18 | **2.09** | 1.79 |
| invalid action | 2.1 | 0.0 | 0.0 | 0.4 | 0.0 |
| deliberate suicide | **4.6** | 0.0 | 3.1 | **0.0** | 0.0 |
| enemy-inflicted | 5.7 | 5.9 | 6.0 | 6.4 | 4.6 |
| all deaths | 24.1 | 27.5 | 29.0 | 30.6 | 26.4 |

Per map, the transit volume is similar: we transit *more* on Portals (61 vs 42 per 1k) and less on Schooltime. **Own goals
per 1k, top10 / us:**

- Portals 23.9 / **49.6**, Slithery 21.9 / **40.6**, Autarky 9.0 / 13.2, QoS 8.2 / 13.2, Schooltime 6.0 / 9.4.
- Lower for us: PD 23.3 / 18.2, PD 10 14.3 / 10.9. On those two maps our dragons die to enemies instead (Q3).
- **Ally head-on per 1k:** Portals 4.5 / **12.5**, QoS 1.2 / 2.6, Default 1.6 / 2.4, Slithery 0.5 / 1.1.

## What own goals are

The context shares are the same for every cohort:

- **Wall and self deaths** are 92–99 % *enclosed* (5-step reach ≤ 15) and 86–97 % at reach ≤ 8.
  - The median length is 2 (57–74 % at length ≤ 2), and the median age is 6–8 rounds.
  - These are small, young dragons that run out of room: recycling, by accident or design.
  - Q4 cannot tell intent. The top ten's invalid-action deaths share the same profile (99 % enclosed, 76 % length ≤ 2, age 8), which suggests the top ten *choose* those deaths instead of walking into walls.
- **Ally head-on deaths** are the exception: 93–99 % near a portal, 45–49 % within 3 rounds of a transit, only 43–46 %
  at reach ≤ 8, and older (median age 13–17). They are traffic accidents at portal exits.
- **Post-transit deaths by class (0–150):**
  - Top ten: suicide 32 %, wall 19 %, ally head-on 18 %, ally body 12 %, enemy 11 %.
  - Us: wall 39 %, ally head-on 28 %, ally body 14 %, self 10 %, enemy 9 %.
  - The top ten's post-transit deaths are mostly chosen. Ours are mostly collisions and dead ends.
- **Our 835 invalid-action deaths are all newborns at age 0.** Children die the round they are born; the field's invalid
  deaths are old. Worth checking as a split-placement bug.

## Reading

1. The fix target is **exit traffic**: landings into our own swarm, doubles through the same pair, and newborns sent
   through portals. Blindness (not knowing what is on the other side) is not the differentiator.
2. The top ten transit *more* early (Q3) and die *less* per transit. So "fewer transits" is the wrong fix: it throttles
   economy, which C1-F and R-3 already found.
3. Own goals: the wall/self volume gap (18.7 vs 9.1 per 1k) is mostly enclosed length-2 dragons.
   - A controlled recycle (an explicit suicide or chosen dead end where a corpse is wanted) is how the top ten do it.
   - Whether that is better than our accidental version depends on where the corpse lands and who eats it.
   - `corpse_recovered_share` and `pearls_ally_corpse_share` in `sides` answer that and are the next query.

## Ledger rows touched and suggested weights

- **L05 (ranked leaks live in the Tyr lineage and are fixable on Ares), 0.8, unchanged; sharpened.** The local V06 base
  carries the live leak at the same size: per-transit died-3 0.278, same-move 0.137, ally head-on 1.79/1k. The leak
  is exit traffic.
- **L06 (portal-exit knowledge halves near-portal deaths), 0.2 → 0.15.** Blind landings die no more often than the
  field's. Knowing the exit is not the missing piece; the collision with our own traffic is.
- **L23 (HOLD packet: treat a landing as occupied for two rounds), 0.3 → 0.45.** It targets the measured mechanism:
  seen-landing and double deaths, and ally head-on at exits. Its V07 result (ally head-on −13 %, economy flat) fits.
  Re-test with a trigger on "an ally within k of the pair".
- **L24 (enclosure hazard at reach ≤ 8), 0.5, unchanged.** Enclosure is the context of nearly all wall/self deaths for
  everyone. The difference is volume (our wall rate is 2.2× the top ten's), not kind.
- **L29 (pearls@k rewards churn), 0.8, informed.** The top ten recycle *deliberately* (suicide 4.6 + invalid 2.1 per 1k;
  32 % of their post-transit deaths are suicides).
- **New row (proposed): portal exit traffic control, 0.55.** At most one of our dragons per pair per 2 rounds; no newborn
  transits in the first 10 rounds; yield when an ally is on the exit side. Target: per-transit died-3 from 0.28 → 0.20
  with transits unchanged. Measure seen-landing died-3, doubles died-3 and ally head-on per 1k.
- **New row (proposed): chosen recycling (explicit suicide of enclosed length-2 dragons where the corpse feeds an ally),
  0.35.** The next query (corpse recovery) sets its weight.
