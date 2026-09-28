---
id: 2026-09-28-analysis-runtime-sonar
author: glm/analysis/a1
kind: observation
title: "The incumbent 9508 runs chronically at the 100M point cap in 47% of its field games; sonar volume (3.9 rays/turn) shows no win benefit within any line"
task: "A1 §3.6 runtime + §3.7 sonar audit"
supersedes: []
evidence: "Verified controlled games (field+dev), unit = game, side A: 9508 n=143, 9663 n=70, 9639 n=52, 8540 n=51, 9980 n=49, plus 9573/9604/10013 n=20 each (dev only). cpu_recorded == turns in 100% of games (coverage complete). Script: tools/analysis/a6_a7_runtime_sonar.py; hub tables: tools/hub/analysis.py::runtime_table/sonar_table."
---

# Runtime (§3.6)

| submission | pool | n | cpu med | cpu p95 | cpu max | games ≥100M | games >90M |
|---|---|---|---|---|---|---|---|
| 9508 (incumbent) | field | 123 | 92.9M | 100.0M | 100.0M | 58 | 69 |
| 9508 | dev | 20 | 100.0M | 100.0M | 100.0M | 11 | 12 |
| 9663 | field | 50 | 69.7M | 86.6M | 97.5M | 0 | 2 |
| 9663 | dev | 20 | 68.7M | 84.4M | 92.6M | 0 | 1 |
| all others (8540/9573/9604/9639/9980/10013) | both | 222 | 61–72M | 70–81M | <83M | 0 | 0 |

- 9508's overload is **chronic, not spiky**: its stage cpu median is 85M already at r100 and climbs monotonically to 94M by r360+. Of its 81 games that cross 90M, the median first crossing is r100. Context at the stage before crossing: units median 13.5, sonar 3826 — ordinary mid-game states, all ten maps represented.
- 9663 is the only other arm above 90M (3 games, all on Slithery Fight — the 14-dragon map; watch it, but it is not chronic).
- Cross-reference to the self-audit's public numbers (loki 100M every game, gavroche-v32 96.6M, 9663 97.46M): consistent with this table; none of those were re-derived here beyond 9663.

**Decision fed**: the local gates (80M/60M) are correctly strict — every non-incumbent arm passes with ≥15M headroom, so the gate is not what blocks good candidates. But the incumbent itself would FAIL its own gate; until a runtime-fixed descendant takes over, any local→live inference about "our" runtime is about a cap-saturated bot. A Python-host degradation mode (e.g. sonar cap under load) is justified before S1 ships, on the evidence that 3 of 8 arms already sit within 10M of the live 95M gate when they dev-probe.

**Falsifier**: a 9508 game whose cpu_max < 80M on a full-length field game (would mean the overload is state-dependent, not chronic); or a non-incumbent arm crossing 95M on the live server.

# Sonar (§3.7)

| submission | field sonar/turn med | wins vs losses | cpu med |
|---|---|---|---|
| 8540 / 9508 / 9663 / 10013 / 9573 / 9604 (bifrost & yuna lines) | 3.89–3.95 | ~equal (3.9 vs 3.92–3.97) | 61–93M |
| 9639 (eindog) | 1.88–3.06 | wins 3.06 / losses 1.88 | 61M |
| 9980 (tidus) | 1.98–2.74 | wins 2.74 / losses 1.98 | 65M |

- Within every 3.9-ray line, a game-above-median-split shows **equal or lower** win share than below-median games (e.g. 8540 field compact: 0.17 vs 0.57, n=6/7; 9508 field compact: 0.20 vs 0.38, n=25/26; 9663 field compact 0.20 vs 0.40). The two low-sonar lines (9639, 9980) show the opposite sign on open maps — sonar rate is line-confounded, so only within-line splits count, and those lean negative or null.
- Runtime cost per ray is **not measurable cross-sectionally**: 8540 (3.9 rays) and 9639 (2.7 rays) both run at ~61M medians, so rays do not show up in cpu_max at these rates; 9508's overload is its own compute, not its sonar.
- Opponents for scale: 62 runs 3.95 rays/turn (same as us, and is the strongest opponent); 45 runs 0.54 and still beats us half the time; 470 runs 1.10 and out-economies us. Ray volume does not separate strong from weak opponents.

**Decision fed**: the framework's "every packet kind names its consumer" rule has no observational counter-evidence protecting 3.9 rays/turn. A designed cut (arm with sonar halved) is the cheap next test; the audit alone does not justify forcing a cut on the evidence, because within-line splits are n≤26 per cell.

**Falsifier**: a designed halving arm that loses ≥5 pp of live share (sonar was buying something); or a within-line split with n≥50 showing share ≥0.15 higher for above-median sonar games.
