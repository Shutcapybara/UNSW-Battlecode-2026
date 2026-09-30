# Ares V06 — expanded search and supported threat evaluation

V06 starts from the corrected Tyr V12 port in Ares V05. It uses the higher
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

On the seed-1 fixed panel V06 scored 122–38–0, up from V05's 118–41–1. Its
round-100 dragons improved from 1.071 to 1.200 field medians and its mean
normalized pearl curve rose +0.0133, below the +0.05 acceptance gate. Four
dense-map sandbox games had no timeout/crash errors (p99 max 7.4M points,
8.6M maximum). V06 remains experimental. Full results and limitations are in
[the V06 finding](../../docs/findings/2026-09-29-ares-v06-expanded-search-support.md).

Bifröst's wider route-ownership rule and Skadi's exit-only guard are excluded:
their documented comparisons regressed or failed fresh-holdout confirmation.
