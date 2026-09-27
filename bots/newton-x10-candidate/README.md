# newton-x10-candidate — fast-bed contest + conversion stop (cycle-1 best composite)

- **Lineage:** Newton. Parent: `bots/newton-x02-mech` (master, all off) with
  `override.py`: `fast_edisc 0.9, fast_edisc_per 25, fast_edisc_nc 625,
  fast_edisc_nc_min 256, unit_stop_round 200`.
- **Hypothesis:** (1) stop ceding regenerating center beds on compact maps
  (maps 256-625 tiles; below 256 contesting feeds melees); (2) stop compact
  production at round 200 so the fleet converts to length for the r500
  tiebreak.
- **Measured (native, deterministic, paired per fixture vs newton-x01 = fafnir-v01):**

| Gate set | Record | x01 | Verdict |
|---|---|---|---|
| Compact panel 8 (v13+tew, devil+arena) | **3-5** | 0-8 | **PASS** (≥3-5): devil 3-1 (A both, B/tew) |
| Screen 32 (serre screen) | 25-7 | 25-7 | **FAIL** (+0 < +2): stop-200 cedes devil/B/leviathan grind game |
| Gauntlet 182 | **147-35 (+7, timeout-corrected)**: devil 9-5 [5-9], default_small 14-0 [11-3], trophy 11-3 [10-4], arena 6-8 held, big_empty/stronghold 14-0 held, Colosseum 12-2 [13-1] | 140-42 | informational (screen gate already failed) |
| Reserve 16 | 13-3 | 13-3 | **0/16 fixtures differ — mechanisms inactive (both maps >625 tiles): activation finding, not a pass** |
| Judge sandbox | **clean**: 4/4, 0 TLE, 0 faults (arena L/L r56-59, stronghold W/W r500) | clean | ✓ |

- **Not promoted** (screen gate failed). Retained as the measured best
  composite and the cycle-2 starting point. The two mechanisms are
  opponent-conditional in opposite directions: the contest wins the churn war
  vs swarm specialists, the conversion stop wins length races vs swarm
  survivors but loses grind games vs evaluators (leviathan devil/B: x01 held
  it to longest 10 by 383 splits; stop-200 let it reach 29).
