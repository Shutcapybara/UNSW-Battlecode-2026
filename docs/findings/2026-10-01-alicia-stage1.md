# Alicia stage 1 — ES on Ares's weights, curve reward then gate-shaped reward (03, 04)

**Date:** 2026-10-01 · **Author:** Claude Opus 5.5 (lineage Alicia, RL-1) · Design:
`docs/findings/2026-09-30-alicia-rl-design.md`

## Summary

1. **`alicia-03-es-curve-pool` is a REJECT (D-032).**
   - The curve reward gives units@100 and length@100 half its weight, and it learned *less churn*.
   - On the pool: material and win were unchanged and every death rate fell (ally head-on −14 %), while pearls fell
     10 % and births 12 %.
   - The gate's economy mean is 38 % ally corpses (L29). It reads this as −0.097 economy.
2. **The curve reward's surface near V06 is a bowl.** Its floor is flat, and the bowl is in the material term.
   - The run `s1` surrogate (119 members) has no significant slope, and a curvature of −0.053 per unit |u|²
     (t ≈ −6.6).
   - σ 0.2 in 24 dimensions, with Adam, drifted the centre out of the floor from generation 4.
3. **`alicia-04-es-gate-pool` is a REJECT, and it has learned the pool.**
   - It is the first version in this lane with a positive pool economy lower bound: +0.046 [+0.022, +0.066].
   - It loses the generalisation panel: economy −0.018 [−0.034, −0.001], win **−0.066 [−0.099, −0.031]**.
   - It also fails the pool units@100 bound (−0.029, lb −0.062), the length bound (lb −0.031) and the win bound
     (lb −0.042).
   - This is the generalisation gap stage 2 starts from.
4. **The gate-shaped reward finds a direction.**
   - Run `s1c`: the economy percentile is the objective, units/length@100 and death rates are hinge guards, with σ 0.1
     and SGD.
   - The centre beats the parent on the economy objective by **+0.016 ± 0.007 per generation** (15 paired generations,
     t ≈ 2.3).
   - The surrogate (272 members) has six economy slopes at |t| 2.9–4.2 and no curvature on economy.
   - The material guard is what bites (generations 10, 11, 13).
   - The trained vector is `alicia-04-es-gate-pool`; it is on the D-032 panels (§ 04).

## Run `s1` — curve reward

- **Configuration.** σ 0.2, Adam lr 0.05, 8 antithetic pairs. 20 pool fixtures a generation: 10 maps × 2 seats, a zoo
  opponent per fixture, seed 1000 + generation.
- **Rows.** `game_stats/runs/alicia-train-s1.jsonl`.

Centre minus parent, paired, in field-percentile points:

| gen | ΔR | Δ p@50 | p@100 | p@150 | p@250 | units@100 | length@100 | Δwin |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | +0.019 | −0.020 | −0.018 | +0.016 | +0.007 | +0.043 | +0.042 | +0.05 |
| 2 | +0.028 | +0.019 | +0.045 | +0.001 | −0.057 | +0.055 | +0.052 | 0 |
| 3 | +0.021 | −0.024 | −0.015 | +0.013 | +0.040 | +0.040 | +0.037 | +0.05 |
| 4 | −0.010 | −0.017 | −0.004 | −0.051 | −0.111 | +0.028 | +0.025 | −0.15 |
| 5 | −0.014 | −0.045 | +0.004 | −0.056 | −0.094 | +0.009 | +0.030 | +0.05 |
| 6 | −0.115 | −0.094 | −0.112 | −0.100 | −0.103 | −0.131 | −0.124 | −0.10 |

- **Stopped in generation 7.** It was interrupted at 100 of 360 games and is not scored.
- **Surrogate fit** (ridge, linear + |u|²).
  - The largest slope is `unseen_value` +0.046 (se 0.031); none is significant.
  - Curvature is −0.053 (se 0.008).
  - Mean ΔR by member distance from the parent:

    | \|u\| band | mean ΔR |
    |---|---:|
    | < 0.4 | +0.016 |
    | 0.7–0.9 | −0.028 |
    | > 0.9 | −0.037 |

### `alicia-03-es-curve-pool`

- **What it is.** The `s1` centre after generation 2, with 24 weights all within ±16 %. The largest moves:
  `sprint_cost` −14 %, `w_bed_block` −13 %, `momentum_weight` +15 %, `unseen_value` +14 %.
- **Parity.** With the learned part off, 0 of 30,558 turns diverge.
- **CPU.** Not probed (rejected). Its caps are within R-1's L1 range.

D-032 scorecard against `alicia-01-nodevil`, seeds 1–3:

| Panel | n | Δecon~ [90 % CI] | p@50 | p@100 | p@150 | p@250 | units@100 | length@100 | births@100 | Δwin |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pool | 480 | **−0.097 [−0.131, −0.060]** | −0.119 | −0.100 | −0.103 | −0.066 | −0.002 [−0.057, +0.025] | −0.009 [−0.037, +0.040] | −0.117 | +0.004 [−0.033, +0.044] |
| Generalisation (**interrupted, 572 / 744**) | 572 | −0.030 [−0.049, −0.011] | −0.027 | −0.015 | −0.060 | −0.020 | +0.038 [−0.018, +0.071] | **+0.036 [+0.004, +0.064]** | −0.023 | +0.010 [−0.031, +0.051] |

- **Pool tier 2.** Every rate falls: wall 8.60 → 8.18, self 5.99 → 5.63, ally body 2.99 → 2.82, ally head-on
  2.72 → 2.34, newborn deaths 35.6 → 35.1.
- **Generalisation pairs.** Length better/worse 312/243 (p = 0.004); units 301/231 (p = 0.003).
- **Verdict: REJECT.** The panel was stopped at 572 of 744 games because the pool decides it.

**Reading.** The curve reward with a material half trades pearls for retention; the gate's corpse-counting economy
penalises that trade. Off-pool, the same policy gains real length. The two curves are two measurements of one quantity
with opposite signs on churn. So the reward was changed to the gate's own objective, with material held as a guard.
Also, the +0.02 seen in training (3 × 20 fixtures) did not survive 1,052 games. That is winner's-curse selection on a
noisy curve.

## Run `s1c` — gate-shaped reward

- **Configuration.** σ 0.1, SGD lr 0.01, 8 pairs × 20 pool fixtures, seeds 3000+.
- **Reward.** R = mean pct(p@50..p@250) − hinge guards:
  - 2 × (pct drop > 0.01) on units@100 and on length@100;
  - +10 % on the pooled death rates.
- **Run.** 16 generations, about 5.5 h of wall time on the shared host.
- **Rows.** `game_stats/runs/alicia-train-s1c.jsonl`.

| gen | ΔR | ΔC (economy) | Δ p@50 | p@100 | p@150 | p@250 | units | length | guard P | Δwin |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | +0.021 | +0.021 | +0.023 | +0.010 | +0.010 | +0.042 | +0.045 | +0.021 | 0 | +0.05 |
| 2 | −0.005 | −0.004 | +0.008 | −0.000 | −0.007 | −0.017 | −0.010 | −0.010 | 0 | +0.05 |
| 3 | −0.002 | −0.002 | +0.008 | +0.007 | −0.017 | −0.004 | +0.026 | +0.020 | 0 | −0.075 |
| 4 | −0.012 | −0.012 | +0.010 | −0.042 | −0.020 | +0.003 | +0.010 | +0.005 | 0 | 0 |
| 5 | +0.031 | +0.031 | +0.042 | +0.045 | +0.011 | +0.027 | +0.026 | +0.019 | 0 | +0.20 |
| 6 | +0.039 | +0.039 | +0.019 | +0.045 | +0.065 | +0.027 | +0.035 | +0.036 | 0 | 0 |
| 7 | −0.004 | −0.004 | +0.018 | +0.007 | −0.016 | −0.025 | −0.010 | −0.007 | 0 | 0 |
| 8 | −0.014 | −0.014 | +0.026 | −0.020 | −0.011 | −0.052 | +0.005 | +0.007 | 0 | −0.10 |
| 9 | +0.037 | +0.037 | +0.002 | +0.039 | +0.051 | +0.057 | +0.013 | +0.029 | 0 | +0.05 |
| 10 | −0.031 | +0.024 | −0.028 | +0.027 | +0.055 | +0.043 | +0.054 | +0.032 | 0.055 | +0.10 |
| 11 | −0.253 | −0.027 | −0.007 | −0.002 | −0.037 | −0.063 | −0.064 | −0.069 | 0.225 | −0.15 |
| 12 | +0.055 | +0.055 | +0.005 | +0.065 | +0.070 | +0.079 | +0.050 | +0.041 | 0 | +0.15 |
| 13 | −0.348 | +0.002 | +0.032 | −0.023 | +0.000 | −0.003 | −0.106 | −0.089 | 0.350 | +0.10 |
| 14 | +0.042 | +0.042 | +0.010 | +0.045 | +0.039 | +0.073 | +0.010 | +0.044 | 0 | +0.10 |
| 15 | +0.045 | +0.045 | +0.089 | +0.064 | +0.047 | −0.021 | +0.042 | +0.073 | 0 | +0.20 |

- **Economy objective.** ΔC is +0.0155 over generations 1–15 (se 0.0066) and +0.020 over the last 8.
- **Guard.** The material guard fired in generations 10, 11 and 13 (units/length −0.06 to −0.11). In those
  generations ΔR is dominated by the hinge (×2 weight).
- **Surrogate on the economy term C** (272 members). Slopes are per unit log-multiplier:

  | weight | slope | t |
  |---|---:|---:|
  | `dive_value` | +0.078 | +4.2 |
  | `unseen_value` | −0.072 | −4.0 |
  | `trap_weight` | −0.067 | −3.7 |
  | `enemy_target_discount` | +0.062 | +3.4 |
  | `target_gamma` (horizon) | −0.056 | −3.0 |
  | `pearl_value` | +0.053 | +2.9 |

  Curvature is −0.003 (t −0.3). The economy has slopes and no bowl.
- **Surrogate on R** (with the guards). The strongest slope is `search_cap` −0.118 (t −2.2), and curvature is −0.15
  (t −4.6): the bowl lives in the material guard.
- **Centre movement.** SGD at lr 0.01 moved the centre ≤ 0.15 in u, mostly along the guarded directions
  (`goal_weight` +16 %, `enemy_target_discount` +15 %, horizon −12 %, `search_cap` 160 → 143). It moved only slightly
  along the strongest economy slopes (`dive_value` +1 %, `unseen_value` +3 %).

**Reading.** On the gate's objective the weight surface is *not* flat. It has a measurable slope towards dives,
fewer unseen-cell targets, a lower trap penalty, more contest of enemy targets, a shorter horizon and a higher pearl
value. `ra` saw the trap and threat direction with single knobs (+0.017 for trap 30 → 20). The joint slope is
three to four times stronger than any of them. The cost lies along the material guard, and its curvature is what
ES has to stay inside.

## 04 — `alicia-04-es-gate-pool`

- **What it is.** The `s1c` centre after generation 14, evaluated in generation 15 at ΔR +0.045, baked in.
- **Parity.** With the learned part off, 0 of 30,558 turns diverge.
- **D-032 scorecard** against `alicia-01-nodevil`, paired, seeds 1–3, complete:

| Panel | n | Δecon~ [90 % CI] | p@50 | p@100 | p@150 | p@250 | units@100 | length@100 | births@100 | Δwin |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Pool | 480 | **+0.046 [+0.022, +0.066]** | +0.024 | +0.068 | +0.056 | +0.037 | −0.029 [−0.062, +0.002] | −0.007 [−0.031, +0.032] | +0.060 | −0.002 [−0.042, +0.037] |
| Generalisation | 744 | −0.018 [−0.034, −0.001] | +0.000 | −0.003 | −0.037 | −0.032 | +0.000 [−0.034, +0.042] | +0.007 [−0.021, +0.038] | −0.002 | **−0.066 [−0.099, −0.031]** |

- **Pool tier 2.** All rates are within ±4 %: wall +4 %, self −3 %, ally body −4 %, ally head-on −1 %, newborn deaths
  equal.
- **Pool pairs.** p@100 better/worse 262/204 (p = 0.008).
- **Pool map economy.**
  - Gains: Schooltime +0.24, Portals +0.16, Autarky +0.09, Slithery +0.04.
  - Losses: Devil −0.24; the rest are within ±0.03.
- **Generalisation.** Win better/worse 105/153 (p = 0.003).
  - Economy losses concentrate on seam_market −0.54, pulse_farms −0.29, pinwheel −0.21, trauma_tr −0.21 and
    crossroads(_tr) −0.12/−0.18.
  - The transposed pool maps mostly gain (devil_tr +0.51, trophy_tr +0.28, queen_tr +0.15).
- **Verdict: REJECT.**
  - It fails units@100 (lb −0.062), length@100 (lb −0.031), pool win (lb −0.042) and generalisation economy
    (lb −0.034).
  - Under the lane's own rule (pool up, generalisation down) it is also rejected as a pool fit.
- **Generalisation gap of stage 1 (stage 2's first number).** Pool vs generalisation is +0.046 vs −0.018 on economy
  and 0.00 vs −0.066 on win. A 20-fixture-a-generation pool optimiser found real pool slopes (t 3–4) that do not
  carry to unseen maps.
- **CPU.** Not probed (rejected). Its caps are lower than the parent's (`search_cap` 143, `search_cap_late` 355).

## Ledger rows touched (proposed weights)

- **L16** (offline-learned weight table), 0.5 → **0.5**, unchanged.
  - For: the gate-shaped reward finds pool slopes, and 04 is the first lower bound > 0 on pool economy in this lane.
  - Against: 04 is a pool fit (generalisation win −0.066).
  - The pre-stated trigger (pool-economy failure → 0.4) did not fire, and the off-pool failure is what stage 2
    tests.
- **L04** (fitted weights beat hand weights), 0.6 → **0.6**. Same reading: fitted weights beat hand weights on the
  maps they were fitted to and lose off them.
- **L28** (V06's pool edge is partly map identity), 0.9. A global weight vector with no map input reproduces the same
  pool-vs-generalisation split (pool econ +0.046, generalisation win −0.066). Ten maps are enough for a 24-dimensional
  optimiser to learn their geometry, so the OOS rule binds on training data, not only on map-keyed code. No weight
  change; noted as evidence.
- **L29** (the metric rewards churn), 0.8 → **0.9**. This is an independent second mechanism: a less-churning policy
  loses 0.10 economy at equal material and win rate. Recommend that the corpse-share diagnostic become a scorecard
  column.
- **L21** (the +0.05 gate is the right shape), 0.3, unchanged. 03 is direct evidence for the retention clause: +0.036
  length off-pool at −0.030 economy.
- **L14** (exploration value). The joint economy slope is *against* more unseen value (−0.072, t −4.0) and *for* dive
  value. This is the opposite of `ra`'s single-knob pool finding, and the two disagree. No weight change until 04
  reads.
