---
id: A1-Q7-sonar
author: claude/analysis/session-01KHqE
kind: observation
title: Sonar volume is free in points and unidentifiable in outcomes — the live record cannot say whether rays buy anything
task: A1 statistics analysis (handoff §3.7)
supersedes: nothing
evidence: stage `sonar`/`turns` of 425 verified controlled A-side games and their opponents (LIVE/state/state.json 12:12Z); probe-log OLS (`build/a1_turns_*.csv.gz`, Q6); `tools/hub/analysis_a1.sonar_table`
---

**Units:** game (rays per dragon-turn = stage sonar / stage turns), dragon-turn for cost.

| source | n | rays per dragon-turn median (q10–q90) | r100 window | compact W / L | open W / L | opponent rays |
|---|---:|---|---:|---|---|---|
| 9508 | 143 | 3.92 (3.77–3.96) | 3.92 | 3.80 / 3.90 | 3.92 / 3.93 | 45: 0.54, 62: 3.95, 470: 1.10, 545: 3.83 (9571) / 1.27 (9371), 752: none, 306: 2.45 |
| 9663 | 70 | 3.94 (3.81–3.97) | 3.94 | 3.85 / 3.94 | 3.94 / 3.95 | |
| 8540 | 51 | 3.95 (3.83–3.98) | 3.95 | 3.89 / 3.96 | 3.95 / 3.97 | |
| 9573 / 9604 / 10013 | 20 each | 3.93–3.94 | 3.94 | | | |
| 9639 | 52 | 2.45 (1.06–3.22) | 1.60 | 3.81 / 1.64 | 2.37 / 1.33 | |
| 9980 | 49 | 2.38 (1.27–3.37) | 1.40 | 2.93 / 1.84 | 1.25 / 1.33 | |

1. **Cost.** In the judge sandbox a ray costs nothing measurable: the within-fixture regression coefficient is
   −0.6 to +1.2 M points with standard errors of that size against a 18–29 M per-turn baseline (Q6). The 4 k/byte
   write cost of ~26 bytes per SONAR line is ~0.1 M; the "2.5 M per write" in HANDOFF §1 does not show up per ray,
   so the lines are batched into one write. Cutting rays saves nothing on the runtime side.
2. **Identifiability.** The bifrost/yuna/fenrir lines send 3.9–4.0 rays every turn with no between-game variance
   (q10–q90 width < 0.2), so no within-source correlation with the outcome can be estimated for them. The two lines
   that vary (ein-dog, tidus) show a *positive* association with winning on compact maps (3.81 vs 1.64; 2.93 vs 1.84
   in the r100 window) — but their ray count is a function of the role/state machine (fewer rays when the swarm is
   small or scattered), so this is the swarm size reading through, not an effect of rays.
3. **Opponents.** The two strongest opponents on our record disagree: 62 (Heartbreaker) rays at 3.95 like us; 470 at
   1.1 and 45 at 0.54 win their share without volume; 752 sends none. Volume is not what separates the clusters
   (Q5).
4. **Message counts on receipt** are not in the probe logs (inputs are not echoed) and not in the record; only a
   tap build (Q8) would give `NUM_MSGS` per turn.

## Decision

The framework's "every packet kind names its consumer" rule is justified, but on *content* (what the 64-bit payload
carries and whether a consumer changes an action), not on cost: rays are free and the record cannot price their
benefit. The only valid test is an ablation on seeded live-pool fixtures (rays on/off per packet kind, exact pairs),
which the S1 prompt already asks for. Do not spend a live screen on a sonar-volume change.

## Falsifier

A seeded ablation in which removing a packet kind changes the paired outcome by ≥ 0.10 on ≥ 30 pairs, or a probe in
which per-ray cost exceeds 1 M points (then the batching assumption is wrong).
