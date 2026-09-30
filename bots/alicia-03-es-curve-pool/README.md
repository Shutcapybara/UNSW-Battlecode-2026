# alicia-03-es-curve-pool

Alicia (RL-1). stage 1 (curve only, pool, zoo): ES centre after generation 2 of run s1, the best-evaluated checkpoint (paired +0.019/+0.028/+0.021 reward over the parent in gens 1-3 on 20 fixtures each); 24 weights moved by at most 16 percent

Parent `alicia-02-tunable` behaviour is restored exactly by `ALICIA_PARAMS` = the parent values below (golden-checked by `tools/alicia/eval.py parity`).

| param | parent | this bot |
|---|---:|---:|
| `bed_value` | 8.0 | 7.23895 |
| `crowd_weight` | 0.6 | 0.554175 |
| `density_ally_weight` | 0.10 | 0.106194 |
| `density_enemy_weight` | 0.40 | 0.365224 |
| `dive_value` | 3.0 | 2.72452 |
| `enemy_target_discount` | 0.60 | 0.667698 |
| `goal_weight` | 1.2 | 1.08751 |
| `material_unit_value` | 3.0 | 2.76423 |
| `memory_value` | 6.0 | 5.29781 |
| `momentum_weight` | 0.6 | 0.686874 |
| `own_target_discount` | 0.15 | 0.150197 |
| `pearl_value` | 10.0 | 10.7392 |
| `search_cap` | 160 | 176 |
| `search_cap_late` | 384 | 395 |
| `split_value` | 8.0 | 8.24129 |
| `sprint_cost` | 1.0 | 0.863566 |
| `target_gamma` | 0.93 | 0.925612 |
| `target_hysteresis` | 1.25 | 1.28345 |
| `threat_weight` | 1.0 | 0.937716 |
| `trap_weight` | 30.0 | 33.0555 |
| `unseen_value` | 5.0 | 5.71532 |
| `visit_weight` | 0.15 | 0.151012 |
| `w_bed_block` | 0.5 | 0.43346 |
| `w_flank` | 3.0 | 3.12931 |
