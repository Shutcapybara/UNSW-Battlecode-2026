# Seoul — P2-T tester (Claude Opus 5.5)

Worktree `../wt-Seoul`, branch `r/Seoul`; findings `docs/findings/<date>-seoul-*.md`.

## Unit 1 — evidence boundary for H-1 ranked item L47

**Scope:** information-first handoff, no bot version, CPU probe, replay batch, training, or panel run. This respects the lead's resource allocation: Luna is the compute workhorse; Seoul should contribute higher-quality test selection and interpretation. The 30-minute check-in is informational and quiet when the board is unchanged.

**Read:** protocol, Phase 1 summary, hypotheses, baselines, benchmarks, targets, board, taxonomy, and the relevant tester/analyst status tops on `origin/main`. At launch, the board had no Seoul entry or fresh analyst request. Obscur's ranked ten puts L47 split restraint at #3; L47 is weight 0.5. Expedition has already closed a narrow food-hold screen, so I am not claiming or repeating that arm.

**Published evidence reviewed:** Expedition's food-hold v1 used 80 paired fixtures / 160 games on fixed maps, controls, seats and seeds 3–4. Its complete audit says discovery was 23.5 parent / 23 candidate expected-score points, then confirmation was 17 parent / 14 candidate. The frozen opponent-nonharm and per-map checks failed (HB17 confirmation 9/6; g01 8/8; QoS 3/1). Confirmation tempo improved by 1.035 rounds and r150/r250 material rose +7.55/+1.85, while end longest/total margins fell 2.20/5.875 and the candidate won three fewer games. The exposure audit reports newborn deaths per split of .402→.382 in discovery and .384→.382 in confirmation; ally head-ons per 1,000 opening dragon-turns rose 1.223→2.240 and 2.063→2.170. The record therefore rejects that exact parent-move-retention rule; it does not settle all food-aware split restraint.

**Seoul disposition:** L47 remains open at the broader hypothesis level, but the visible-pearl immediate-meal guard is closed negative. Do not infer causality from the field's 48% decline rate or equate a faster opening with an outcome gain. The highest-value next information step is an exact-source, existing-replay decomposition of eligible split decisions by map and phase: parent food taken in the next five rounds, child food taken, parent/child survival, and whether the split was required for rescue or escape. This separates “decline because the parent can eat” from expansion/corridor/safety splits before spending panel capacity on a new version. If a new mechanism is later chosen, freeze one counterfactual rule and one expected outcome sign in advance; retain the opposing-architecture and per-map confirmation guards.

Full evidence boundary and next-test specification: `docs/findings/2026-10-04-seoul-l47-evidence-boundary.md`.

| Unit | Work | Status |
|---|---|---|
| 1 | L47 evidence boundary and next-test design | Complete; analysis only, no bot/panel run |

## Unit 2 — L39/L49 cross-lane evidence boundary (4 October)

Rome completed `rome-03-queen-state-convert` on pool + gen, seeds 1–3, both seats, and rejected its own-team-count ≤5 proxy pinned to the original queen. Pool win share fell 2.40pp (cluster 90% CI [−4.17,−0.83]); gen fell 0.79pp ([−1.65,+0.07]), RL conversion −8.45pp ([−13.13,−4.00]); queen survival among reached target maps was unchanged/down; gen wall deaths +15.9%. This does not test TT's original opponent-unit-count trigger. Rome marks H-H1 `rome-04-queen-head-tie` in progress, so Seoul did not overlap it. Next information gap: can enemy count be estimated from locally visible enemy bodies plus ally sonar at r250–350 with useful precision/recall and acceptable staleness? Evidence and design: `docs/findings/2026-10-04-seoul-L39-rome-reading.md`.

## Unit 3 — H-KZ12 screen contract audit (4 October)

Rome's D-043 live zero is complete and the D-043 priority-a cage dose screen has run. I reviewed the newer Kanazawa/Himeji pocket analyses and Rome's screen. H-KZ12 is the next direct Seoul request, but its implementation contract is not yet coherent: Kanazawa's inclusive `C ≤ k` terrain-edge dial (`k=0/5/8/16`) differs from Himeji's strict `C < k` body-conditioned dial (`k=0/4/8/16`), and their death-label horizons differ. Himeji's audit shows why static terrain-only capacity alone misses own-body neck seals. Asked both analysts to reconcile this before a weakhold seed-1 paired dose screen; no test or bot arm was started. Full source-grounded audit and proposed screen: `docs/findings/2026-10-04-seoul-hkz12-screen-contract.md`.

| Unit | Work | Status |
|---|---|---|
| 3 | H-KZ12 feature/dose/label contract audit | Complete; awaiting analyst reconciliation before screen |

## Unit 4 — H-KZ12 contract re-read (4 October)

Kanazawa unit10 plus Himeji H29 resolve Unit 3's blocker on Rome's branch: use the candidate-specific, body-conditioned inclusive capacity `Cb`, doses 0/4/8/16, strict `Cb < k`, and a cycle exemption when the reachable set plus prior head contains a simple cycle at least the projected queen length + 1. Known bodies are projected per action; unknown frontier assigns capacity 16; ordinary simulator legality remains separate; if every legal one-step direction is vetoed, choose maximum `Cb` with parent ranking as tie-break. The earlier terrain-only k=5 pool pilot is historical/nonconforming. Rome's corrected four-dose panel has begun; Seoul will not duplicate it. The contract and next evidence needs are recorded on the board.


## Unit 5 — closeout summary (4 October 10:29 UTC)

Evidence-only closeout: consolidated Units 1–4 and D-044/H-KZ26 next-test design in `docs/findings/2026-10-04-seoul-wrap-up.md`. No Seoul bot, panel, replay, simulator, CPU-probe, or training run was made; Rome’s D-043 zero remains shared evidence, not a Seoul rerun. At last workload inspection Rome was running the corrected H-KZ12 dose panel with high shared load, so Seoul did not overlap it. H-KZ26 remains the next assigned Seoul screen after capacity clears. No candidate or verdict.
