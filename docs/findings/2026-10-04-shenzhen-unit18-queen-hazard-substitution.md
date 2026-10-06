---
id: shenzhen-unit18-queen-hazard-substitution
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator screen (analysis copies only)
title: Unit 18 — H-SZ40 removes the queen's invalid-command deaths (4 → 0) but she still dies, now by walls and her own body; queen hazards substitute in order strike → invalid → sealed
evidence: unswbc 1.2.9, carthage-05 + C+D (`c05d`) vs `c05r` = probe Q (H-KZ26, m = 0) + probe R (H-SZ40); Around UNSW, Islands, Australia (maps/live), seeds 1–3, both seats, 18 games; tools/shenzhen/szqdeath.py, szleak.py
---

# 1. Probe R (H-SZ40)

The queen (id 0/1) never issues a split when units ≥ limit − 4. It takes the first safe single step instead, or keeps
its facing. It fires about 18 times in a game, stacked on probe Q (unit 17, the queen reach veto at m = 0).

# 2. Result (18 games; queen deaths of our side, by cause)

| arm | enemy head-on | invalid | wall | self | ally body | other | mean death round | alive at end | wins | pool total |
|---|---|---|---|---|---|---|---|---|---|---|
| c05d (this set) | 13 | 2 | 0 | 2 | 0 | 1 | 137 | 0 | 11 | 2,638 |
| Q (unit 17) | 6 | 4 | 3 | 2 | 2 | 1 | 223 | 0 | 12 | 2,709 |
| **Q + R** | **6** | **0** | **6** | **4** | 2 | 0 | 197 | **0** | 7 | 2,547 (−3 %) |

Per map total, Q + R vs c05d: Around UNSW +2 %, Islands +19 %, Australia −21 %. Enemy share of our corpse pearls is
unchanged (0.33).

# 3. Reading

* H-SZ40 does what it says: queen `invalid` deaths go 4 → 0 under the veto, and the strike reduction replicates (6/18
  again). Total is within noise (−3 %).
* **Hazard substitution is now the main fact.** Each queen rule removes one cause of death, and the next cause takes its
  place: strikes (c05d) → invalid (Q) → walls and her own body (Q + R; 10 of 18). Queen alive at the end stays 0/18 on
  all three arms. The queen dies of something by about round 200 on these maps, whatever the rule.
* The win column swung from 12 vs 6 (unit 17) to 7 vs 11 here with the same Q component. With the queen never alive at
  the end, the result is the longest/total tiebreak, so win counts at n = 18 are noise. Read the queen column and per-map
  total.

# 4. Hypotheses

* **H-SZ40 supported (mechanism)**, 0.5 → 0.6: it removes its target hazard at no measurable cost. It is not sufficient on
  its own.
* **H-SZ42 (0.45, new) — queen room veto.** The remaining hazard is being sealed in: walls and her own body (10 of 18
  deaths). Rule: the queen never ends a move where the flood-fill room from her head (other bodies block, her own tail
  frees with time) is below 2 × her length. Falsifier: queen wall + self deaths not halved in a Q + R + room-veto stack
  (18 sim games), or total below −5 %. This is the sim form of Kanazawa's H-KZ12 pocket veto, generalised from baited
  pockets to any seal.
* **H-SZ43 (0.35, blue-sky) — the queen in the crowd.** Live, field queens on contact maps survive 0.18–0.29 against our
  0.00. In self-play this parent's queen survives 0/~100. A rule-by-rule fix keeps losing to substitution, so the field's
  edge may be positional: the queen stays where ally heads screen her. Prediction: in ranked post-m2 Around UNSW,
  Australia and Islands games, top-ten queens spend more of their rounds with at least 2 ally heads within 3 than ours do.
  Falsifier: the share is equal or lower. Size: about 200 games, store query. It suits Data (Kageyama) or Himeji.
* **H-SZ41** (stack before reading the tiebreak) holds, and is extended: the stack needs a seal rule (H-SZ42) as its third
  piece.

# 5. Caveats

Self-play against one parent. 18 games. The c05d baselines differ between unit 17 and this set because the opponent
changed (strikes 13 in both, wins 6 vs 11), so per-set comparisons are the honest reading.

**RL translation.** Observation: unit headroom (units vs limit), flood-fill room from the head, and ally heads near the
queen. Action: the queen's split and step choices. Value: queen survival time, with total as a guard. Demonstration: field queens on contact maps
survive 0.18–0.29 live (Chongqing unit 5); their positional context is the H-SZ43 query.
