# Robert V02 — trap pearl gate

Robert starts from Ares V06, which itself is the corrected Tyr V12 port in Ares V05. It uses the higher
bounded search profile shared by historical Bifröst and Skadi snapshots:
160 target nodes normally, 64 when the team is saturated, 60 for the first two
turns, and the existing late/sparse caps. It raises the room flood from 22/36
to 24/40 and restores Tyr's longer 12-length three-step candidate horizon
while keeping the saturated, late and sparse guards.

It also ports Fafnir's size-matched counter-threat support from Skadi: a threat
is discounted only when an observed ally at least as long as the attacker is
within three tiles. Support counts are cached per decision and applied through
the existing threat cost. This is a separate C++ snapshot; V05 and the active
V04 submission remain unchanged.

On the seed-1 fixed panel Ares V06 scored 122–38–0, up from V05's 118–41–1. Its
round-100 dragons improved from 1.071 to 1.200 field medians and its mean
normalized pearl curve rose +0.0133, below the +0.05 acceptance gate. Four
dense-map sandbox games had no timeout/crash errors (p99 max 7.4M points,
8.6M maximum).

Robert keeps the support-threat rule and all Ares V06 policy behavior, then
raises normal target search from 160 to 256 cells, saturated search from 64 to
96, newborn search from 60 to 80, and the target frontier cutoff from depth 4
to 6. Room flood limits rise from 24/40 to 32/48. The late-round and sparse
guards remain unchanged so the deeper profile cannot grow without bound.

This is an experimental Robert snapshot; CPU probes and matchup results are
recorded as measured. The original Ares and all prior snapshots remain
unchanged.

## V02 change

Robert V02 keeps the V01 search profile but makes the trapped-space rule hard:
when the reachable room after a move cannot fit the simulated dragon body, the
move is rejected unless that trapped room contains at least **three reachable
pearls**. The fallback path applies the same gate, so the default
facing direction cannot bypass it when normal candidates are exhausted. If
every local move is an enclosed low-yield trap, the bot retains a legal-action
last resort because the game protocol requires an action each turn.

The bounded native ten-map, both-seat comparison against Robert V01 finished
**7–13–0** for V02, with zero bot errors. The first broader interpretation of
"trapped" (room below the growth-area target) was rejected after a 2–18 result;
the shipped V02 uses the narrower body-fit definition above. Results are under
`build/robert-v02-vs-v01-narrow/`; direct sandbox probes also completed with
zero errors and observed maximum points below 8.7M.

## Measured result

The native ten-map, both-seat gate against Ares V06 finished **12–8–0** for
Robert, with zero bot errors. The seeded C1 run matched that result. The four
direct C++ sandbox arena probes on Schooltime and Portals also completed with
zero errors; Robert's observed maximum was 8.77M points. The sandbox probe
artifacts are under `build/cx/`, and the parent matchup is under
`build/robert-v01-vs-ares-v06/`.

Bifröst's wider route-ownership rule and Skadi's exit-only guard are excluded:
their documented comparisons regressed or failed fresh-holdout confirmation.
