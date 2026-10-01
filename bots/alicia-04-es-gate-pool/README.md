# alicia-04-es-gate-pool

Alicia (RL-1). stage 1, gate-shaped reward (economy percentile objective, units/length@100 and death-rate hinge guards): ES run s1c centre after generation 14 (evaluated in gen 15); sigma 0.1, SGD; 24 weights within +/-16 percent

Parent `alicia-02-tunable` behaviour is restored exactly by `ALICIA_PARAMS` = the parent values below (golden-checked by `tools/alicia/eval.py parity`).

| param | parent | this bot |
|---|---:|---:|
| `bed_value` | 8.0 | 7.60259 |
| `crowd_weight` | 0.6 | 0.561662 |
| `density_ally_weight` | 0.10 | 0.101999 |
| `density_enemy_weight` | 0.40 | 0.419084 |
| `dive_value` | 3.0 | 3.03438 |
| `enemy_target_discount` | 0.60 | 0.689722 |
| `goal_weight` | 1.2 | 1.39677 |
| `material_unit_value` | 3.0 | 3.05332 |
| `memory_value` | 6.0 | 5.78204 |
| `momentum_weight` | 0.6 | 0.587039 |
| `own_target_discount` | 0.15 | 0.151825 |
| `pearl_value` | 10.0 | 10.8825 |
| `search_cap` | 160 | 143 |
| `search_cap_late` | 384 | 355 |
| `split_value` | 8.0 | 7.50879 |
| `sprint_cost` | 1.0 | 0.967357 |
| `target_gamma` | 0.93 | 0.920474 |
| `target_hysteresis` | 1.25 | 1.2621 |
| `threat_weight` | 1.0 | 1.03721 |
| `trap_weight` | 30.0 | 28.9078 |
| `unseen_value` | 5.0 | 5.17016 |
| `visit_weight` | 0.15 | 0.150175 |
| `w_bed_block` | 0.5 | 0.517744 |
| `w_flank` | 3.0 | 2.89889 |
