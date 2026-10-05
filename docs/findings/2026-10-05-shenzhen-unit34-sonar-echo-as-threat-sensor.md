---
id: shenzhen-unit34-sonar-echo-as-threat-sensor
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: log pass over existing simulator replays (no new games) — H-SZ65, a feature check for the Learner
title: Unit 34 — the 4-ray sonar echo (kind counts only, as the rules give it) adds almost nothing to the 7 × 7 view for predicting a dragon's death in the next 10 rounds (AUC 0.6325 → 0.6359 any cause, 0.6902 → 0.6912 contact). It matters only when no enemy head is in view; there an enemy-head echo raises the contact-death rate 1.66× (3.9 % → 6.5 %), but that covers 6 % of those rows
evidence: tools/shenzhen/szsonarthreat.py over 72 sim games (units 17, 18, 22 arms: slq, slr, slx; carthage-05 family; open maps); every alive dragon every 5 rounds from r30, 638,791 rows; virtual N/E/S/W cast from the head over the round snapshot (stops at kelp or a dragon cell, as the sonar page describes); logistic, 60/40 split by game order
---

# 1. Result

Label: the dragon dies within the next 10 rounds (rate 11.9 %), or dies by head-on or body collision (7.4 %).

| features | AUC, any cause | AUC, contact death |
|---|---|---|
| own length | 0.555 | 0.491 |
| 7 × 7 view (enemy heads, enemy body cells) + length | 0.633 | 0.690 |
| view + echo counts (kelp, ally, enemy, enemy_head) | **0.636** | **0.691** |
| echo counts + length only | 0.572 | 0.594 |

Rows with **no enemy head in view** (58 % of all rows):

| enemy-head echoes | rows | death in 10 r | contact death |
|---|---|---|---|
| 0 | 370,280 | 9.1 % | 3.9 % |
| 1 | 22,348 | 8.2 % | **6.5 %** |
| 2+ | 989 | 7.5 % | 5.2 % |

# 2. Reading

* As a threat sensor, the echo is nearly redundant with the view: +0.003 / +0.001 AUC. An enemy-head echo on a blind
  dragon does mean more contact deaths (1.66×), but such rows are rare, so the effect barely moves the pooled AUC.
* Carthage-family bots already cast all four sonars every turn (one sample game: 176,816 sonar events over 499 rounds).
  **67 % of rays end in kelp**, 21 % on allies and 12 % on enemies. The rays are short and mostly hit terrain. The
  echo is therefore mainly a cheap reading of nearby terrain, not of enemies.
* The encoder already carries the echo columns (`tools/learn/encode.py`: echo_kelp … echo_enemy_head). So nothing needs
  adding. The prediction for the Learner is that those columns rank low overall, and higher on blind rows.
* **H-SZ65 (echo as a threat sensor beyond the view, gain ≥ +0.005 AUC): refuted at 0.15.**

# 3. Hypotheses

* **H-SZ65 refuted (→ 0.15).**
* **H-SZ66 (0.3, new) — the echo's value is concentrated in blind states.** In the BC/value model, on rows with no enemy
  head in view, echo_enemy_head ranks above own length in permutation importance for the action label (F/R/L). Falsifier: its
  importance there is below length's, or no higher than on all rows. Size: existing dev120 rows and fitted trees, no new data.
  Suits Learner (Hinata).
* **H-SZ67 (0.25, new, blue sky) — on kelp-dense maps the radio barely reaches, which caps coordination there.** A team's
  share of sonars ending in kelp (legal: echo_kelp / casts) measures radio reach per map. Prediction: across live maps, the per-map
  kelp-echo share correlates with how far we trail the top-10 on that map (ρ ≥ 0.4, more kelp → larger gap), because
  better bots there must rely on local play we already do, or on relays we lack. Falsifier: |ρ| < 0.2 over the ~17 live
  maps. Size: one store pass (echo lines are in the logs; rank gaps are in TARGETS). Suits Data.

**RL translation.** Observation: keep the echo columns (they are cheap), and add a "no enemy head in view" flag so a model
can use the echo where it carries signal. Do not expect an echo-based threat feature to move the overall value AUC.

# 4. Process note

My 00:25Z BOARD line and the unit-33 log entry were stamped 00:25Z, but the unit ended at about 23:54Z. The content is
unchanged.
