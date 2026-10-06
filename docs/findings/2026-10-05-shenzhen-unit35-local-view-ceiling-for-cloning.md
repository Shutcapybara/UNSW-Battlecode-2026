---
id: shenzhen-unit35-local-view-ceiling-for-cloning
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: log pass over existing simulator replays (no new games), a ceiling check for the BC battery (D-067)
title: Unit 35 — the carthage family disagrees with itself in identical local states. A lookup on the exact egocentric 7 × 7 state, trained on half the games, predicts held-out F/R/L at 0.80 where the state recurs (22–26 % of moves) and 0.73 on recurring 5 × 5 states; with backoff to smaller windows it reaches 0.666 over all moves (always-F 0.58). Roughly one move in five is not explained by the local view
evidence: tools/shenzhen/szbayes2.py over 36 sim games (units 17/18 arms: slx, slr; carthage-05 family both sides; open maps); 1.47 M single-step moves by dragons of length ≥ 2, split by game (odd/even) into train 736,185 / test 734,874; key = egocentric window rotated to heading (per cell: empty / own body / ally body / ally head / enemy body / enemy head × pearl), passability of F/R/L, length bucket
---

# 1. Result

Labels: F 0.58, R 0.20, L 0.22 (back moves excluded).

| key (min. 20 training rows) | held-out rows covered | held-out accuracy on covered rows |
|---|---|---|
| 3 × 3 window | 92.7 % | 0.672 |
| 5 × 5 window | 54.2 % | 0.733 |
| 7 × 7 window (the full legal view) | 22.2 % | **0.802** |
| backoff 7 → 5 → 3 → F, all rows | 100 % | 0.655 (min. 5 rows: 0.666) |

# 2. Reading

* Even when the exact 7 × 7 state (bodies, heads and pearls) recurs, the teacher's next move differs about one time in
  five. A model that sees only the view cannot beat about 0.80 on those states. The recurring states are the simple
  ones (open water, few pieces), and there the move depends on things outside the view: memory, radio messages,
  targets seen earlier, possibly tie-breaking.
* Hinata's battery is at 0.72 on dev120 oracle moves (A8b-A1-400 0.7224), with time and memory inputs already in the
  encoder. That set is ten field teachers on live maps, not carthage in self-play, so the numbers are not directly comparable.
  The order of magnitude still suggests the view part is largely learned and the remaining gap is non-local. That supports D-067's
  direction (time, trajectory and latent state) over more view capacity.
* Caveat: this is one teacher family. Recurring-state rows are a biased subset, and I did not score the 3 × 3 and 5 × 5 keys on
  exactly the same rows as the 7 × 7 key.

# 3. Hypotheses

* **H-SZ68 (measurement, 0.6): a local-view ceiling near 0.80 on recurring states** (this unit; replicate on live teachers
  as below).
* **H-SZ69 (0.4, new) — the clone's residual error sits on "empty-view" rows.** On rows with no ally, enemy or pearl in
  the 7 × 7 view, accuracy is lower, and the time and memory inputs (round, `mem_*`) carry at least twice the gain share
  they carry on busy rows. Falsifier: ratio < 1.2, or no accuracy gap. Size: an extra split of D-067 (1)'s breakdown, no
  fit. Suits Learner (Hinata).
* **H-SZ70 (0.3, new, blue sky) — part of the self-disagreement is arbitrary.** In recurring 7 × 7 states, the minority
  action is predicted by dragon-id parity, round parity or seat. That would point to tie-breaking or role-by-id rules, which
  no feature can learn and which set the true ceiling. Falsifier: none of the three moves the minority-action rate by
  ≥ 3 pp. Size: a sim log pass. Suits this lane next unit.

**RL translation.** The clone should be judged against a ceiling, not against 1.0. For view-only inputs that ceiling is
≈ 0.8 on recurring states. The gains left are in non-local state, which is D-067's trajectory block (Kageyama (7)
already lists unit count level / Δ20 / Δ100, matching H-SZ59/H-SZ64).
