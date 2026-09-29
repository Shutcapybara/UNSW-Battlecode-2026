# Ares V05 — Tyr V12 separation bug fixes

Ares V05 builds on the behaviorally matched Ares V04 C++ port and repairs its two confirmed separation exception paths:

- With Tyr's active `bed_wait = 0` override, a separation waypoint scores a bed only when it is due this round; future beds receive zero value instead of causing division by zero.
- A constrained newborn can use the existing six-use budget to follow a nearby fresh pearl's normal route before resuming separation. The route distances and first-step mask are preserved, rather than falling into Tyr V12's `RESOURCE_PAUSE_USED` `UnboundLocalError` path.

These are intentional policy changes from Tyr V12's current Python implementation. V05 is a separate snapshot; V04 and active contest submission v83 remain unchanged.

The seed-1 BENCHMARKS.md panel completed on unswbc 1.2.2: 160 games against
the current eight-opponent roster across ten maps and both seats, with all
replays extracted and no runner errors. V05 scored 118–41–1. Against V04's
same-panel 117–43–0, the four-checkpoint field-normalized pearl mean rose by
0.007, r100 units fell by 0.047, r100 length rose by 0.009, and no tier-2
self-inflicted death rate rose more than 10%. This seed-1 result does not meet
the economy or no-drop-in-units acceptance gates; V05 remains experimental and
was not submitted. See [the V05 finding](../../docs/findings/2026-09-29-ares-v05-separation-bugfix.md).
