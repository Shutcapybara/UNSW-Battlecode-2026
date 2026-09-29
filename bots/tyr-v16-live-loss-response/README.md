# Tyr V16 — live loss response

**Base:** frozen Tyr V01, `tyr-v01-yuna-momentum`.

**Changes from the 28 September replay review:**

- Raise the value of unpaired portal discovery for foragers through round 59,
  and add a weak positive-only ID lane cue through round 47 to spread opening
  scouts without penalizing moves toward resources.
- Forecast enemy sprint paths that eat a currently visible pearl. This catches
  the extra step a short dragon can fund before a head collision, and raises
  the estimated risk for that specific attack path.
- When every movement leaves less room than the dragon's body needs, consider
  an escape split. Check the escaping child’s reachable area and select the
  largest safe tail group, preserving a two-segment parent when possible.

**Screen:** 7–11 against `tyr-v12-devil-scout-tiebreak` over 18 games on the
nine maps from the loss review, both starting sides. V16 went 1–1 on seven
maps and 0–2 on Devil and Trauma. The native `unswbc 1.2.2` run had no runner
errors; it was one unseeded game per map and side, without sandbox limits.
Results and logs are in `build/tyr-v16-vs-v12-loss-review-20260929/` (run ID
`7d8b117e3b824f1fa699cc5e2421bf90`).

This is a focused screen, not an all-map estimate. Keep V01 as the all-map
baseline and V12 as the Devil specialist. Before considering promotion, compare
both sides against a wider opponent panel and report portal/center arrival,
pearl lead by round 30, dead-end segment loss, largest-dragon survival, wall
deaths, and runtime faults separately.
