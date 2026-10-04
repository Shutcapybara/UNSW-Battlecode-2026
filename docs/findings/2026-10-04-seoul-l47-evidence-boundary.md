# Seoul — L47 split-restraint evidence boundary

**Date:** 4 October 2026  
**Type:** tester reading / next-test specification; not a bot experiment  
**Sources:** `claude/obscur-status.md` (ranked ten, L47); `claude/expedition-status.md` (Pass 19, food-hold v1 closeout); `docs/hub/HYPOTHESES.md` (L47); `docs/hub/PHASE2-PROTOCOL.md`.

## What is established

L47 proposes that declining some splits when food is near can improve opening intake and newborn survival. The currently published full test is Expedition's narrow food-hold-v1 rule: before r150, keep the parent's already-selected move if it eats an observed pearl and passes the existing known-state simulation and room requirement; defer only ordinary splits, preserving partial-body rescue and emergency escape splits.

Expedition's final audit validates 160 records across 80 paired fixtures. Discovery was 23.5 parent / 23 candidate expected-score points; confirmation was 17 parent / 14 candidate. It failed the predeclared positive-confirmation, opponent-nonharm, and per-map checks: HB17 was 9–6 in confirmation, g01 was 8–8, and QoS was 3–1. Confirmation tempo was 1.035 rounds faster, with r150/r250 material changes of +7.55/+1.85, but end longest/total margins changed −2.20/−5.875 and the candidate had three fewer wins. These are a direct warning against accepting an opening proxy in place of outcomes.

The exposure audit did not show a uniform newborn-death repair: newborn deaths per split changed .402→.382 in discovery and .384→.382 in confirmation. Ally head-ons per 1,000 opening dragon-turns changed 1.223→2.240 and 2.063→2.170, respectively. This test's negative result is stronger than a first-seed screen, but remains bounded to its fixed opponent and mechanism contract.

## What is not established

The test does not show that every food-aware split restraint rule fails. It only rejects the immediate-meal guard above. Nor does the observed top-ten 48% split-decline rate identify a causal target: eligibility, food visibility, parent/child role, map geometry, escape need and opponent pressure can all differ. L47 should remain distinct from a blanket “split less” policy.

## Cheapest useful follow-up before another panel

Use the exact immutable parent source and existing paired replays to build an eligible-decision table, grouped by map × phase × parent length/room. For each ordinary split opportunity record:

- whether the parent or proposed child could eat a known pearl within five rounds;
- realized parent and child food intake, and survival through the window;
- whether the split was needed for emergency escape, partial-body rescue, or corridor access;
- the action chosen by the parent, without conditioning eligibility on the candidate's later survival.

This diagnostic can show whether the failed rule missed a child-opportunity or geometry interaction, or whether the apparent split restraint association is selection/composition. It does not itself establish causal benefit. Only if it yields a simple, predeclared decision boundary should a new one-mechanism arm be built and compared on both panels with the configured gate, per-map deltas, and an opponent likely to convert. The next version should name an outcome metric and expected sign before any games; tempo, newborn survival and gross pearls stay diagnostics/guards unless the stated target is specifically one of them.

## Resource and scope record

No CPU/GPU work, bot build, replay batch, or panel was started for this note. This is an information-first handoff for the Seoul tester lane; the scheduled check-in is every 30 minutes and remains quiet if no material board/status change appears.
