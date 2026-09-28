---
id: 2026-09-28-analysis-loss-anatomy
author: glm/analysis/a1
kind: observation
title: "Live losses are decided by r250: compact-map eliminations dominate, and the eventual loser already trails on total length at the first checkpoint"
task: "A1 §3.1 — loss anatomy on the live record"
supersedes: []
evidence: "LIVE state.json 2026-09-28T21:40 local (486 games); verified controlled field games only; unit = game; all arms side A. Sources with ≥20 field games: 9508 n=123, 9663 n=50, 9639 n=32, 8540 n=31, 9980 n=29. Script: tools/analysis/a1_loss_anatomy.py."
---

# What losses are made of

Per source (share = win share; elim = elimination losses; RL = round-limit losses):

| submission | n | share | losses elim/RL | elim round med (compact/open) | RL margin med | units r100 loss (ours/opp) | total r250 loss (ours/opp) |
|---|---|---|---|---|---|---|---|
| 9508 (incumbent) | 123 | 0.43 | 43/27 | 138/372 | −11 | 6/17 | 4/86 |
| 9663 (yuna-v02) | 50 | 0.40 | 16/14 | 122/196 | −12 | 8/17 | 5.5/74.5 |
| 9639 (eindog-v02) | 32 | 0.31 | 15/7 | 122/292 | −9 | 4.5/19 | 2.5/74.5 |
| 8540 (bifrost-v01) | 31 | 0.42 | 10/8 | 94/279 | −8 | 6.5/15 | 13.5/84 |
| 9980 (tidus-t02) | 29 | 0.34 | 12/7 | 158/184 | −10 | 6/17 | 2/79 |

Two-line diagnosis per source:

- **9508**: compact maps are the leak (n=51, share 0.29, 28 elimination losses, units r100 6 vs 19); open maps are fine (0.53). RL losses are close (−11 median) — late conversion is not the problem; opening production under pressure is.
- **9663**: the best opener of the family (units r100 11.5 vs 19 compact, 23 vs 21 in wins) but converts nothing extra; loses open maps by elimination late (196 median).
- **9639**: worst compact performer (0.21, 10 of 14 compact games lost by elimination, units r100 4.5 vs 21.5) — an opening-production failure, not a late-game one.
- **8540**: same compact signature as 9508 with smaller n; open-map total r250 gap (40 vs 81) says mid-game economy also leaks.
- **9980**: balanced loser profile; wall deaths per 1k turns are the family's worst (7.8 vs 5.5 for 9508).

Cross-cutting facts (n = all 265 verified controlled field games):

- The eventual loser **already trails on total length at r100** (the earliest checkpoint) in most games: median first-trailing stage = r100 for every source and both map classes; 94–100% of losers trail by r250 (compact 98%/96% for 9508; per-source range 0.88–1.00).
- Deaths per 1k turns are dominated by h2h (8.0–9.5) over wall (5.3–7.8) across all sources; newborn deaths ≤10 rounds have a median of 19–26 per game — churn, not sniping, eats us.
- Opponent split (pooling each opponent's submissions, stated): team 62 is the wall (our share 0.22–0.36; for 9508, 25 of 43 eliminations), team 45 the beatable one (0.40–0.65), 470 wins on economy (their total r250 = 89, the highest; they eliminate us late, r221 median; our share 0.32), 306 neutral on n=10.
- Opponent fingerprints (from opponent_stages, verified field games): 62 = fast strong opener (units r100 19, eliminates us r120, sonar 3.95/turn — the same rate we run); 45 = portal-heavy (86 steps), low sonar (0.54); 470 = low sonar (1.10) economy scaler.

**Decision fed**: next candidates should target opening production / early survival on compact maps (units r100 ≥ 12 while holding deaths), not late longest-margin conversion. The r100-trailing fact sets the measurement: any mechanism that does not move units r100 or total r250 by r250 is unlikely to move live share.

**Falsifier**: a source that reaches live share ≥ 0.55 while keeping units r100 ≤ 8 on compact maps; or a future month of games where losers' median first-trailing stage moves past r250.
