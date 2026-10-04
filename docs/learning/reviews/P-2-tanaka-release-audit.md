# P-2 revision 2 — Tanaka release audit

2026-10-04, fourth wake. **AMEND / HOLD**, not a hash-specific release PASS. Audited scorer SHA256 `ea3b5ef748ac9cf498c48b3941dc3c3be1639456f3e3f283ab308e63d787897d`; approved D-052 spec SHA256 `15d79683518cf704a8cb7680ef1fa55acd8bdaef2bc97b694f40db742ea0d07d`. Archived source and receipts in `tanaka-round4/`.

## Repairs independently verified

The original non-finite and changed-claim defects are fixed. A valid synthetic control passes; all **18/18** injections (NaN, infinity or None in six binding metric fields) produce INCOMPLETE. 989 valid draws is INCOMPLETE; 990 passes the otherwise valid control. An r50 AUC below 0.66 but above Phi passes, as D-052 requires. The exact approved spec is accepted and PROPOSED refused.

Isolated temporary claims: changed claim, scorer, spec and predictions, and sub-95% declared coverage each give INCOMPLETE before evaluation; a valid control passes. A second score is refused in all six cases. These integrity tests stub the numerical evaluator; a separate independent numerical test used an invented 200-game/50-series cell. It produced 1,000 valid draws, AUC 0.7793469551282052 exactly matching an independent all-positive/negative pair comparison. NaN/Inf predictions are NONFINITE_INPUT, one-class is UNDEFINED, and positives confined to one series yield only 625 valid draws. No real confirmation call, claim or outcome read occurred.

## Remaining defect: frozen population not enforced in predictions

`cmd_counts` and `coverage` use **decoded AND store_in_scope**. `cmd_run` filters loaded games by **decoded only**, while the archived loader consults the mutable store's current in_scope flag. A store correction after counts can therefore silently reintroduce an excluded game. Conversely, lost or newly excluded rows can reduce actual scoring coverage while the claimed coverage remains unchanged. Scoring validates hashes of the predictions it receives, not whether those rows are the ones predeclared.

Reproduced with every data loader replaced by synthetic data and P2 redirected to a temporary directory: a 300-game population declares Autarky0 missing (store_in_scope=false; 99/100 usable Autarky games), but cmd_run seals a prediction for Autarky0. The synthetic loader intentionally returned only six rows, and no run-time membership/count assertion fired. This is a plumbing counterexample, not a claim that the real confirmation has changed or lost those rows. Real held-out data were never loaded by this test.

Before release, use the frozen usable IDs consistently; record the eligible checkpoint keys and verify actual prediction keys, regime/ranked/clean tags and coverage against that frozen projection. Explicitly account for permitted draw exclusions and ended rows; they must not silently change report-only cell roles or the coverage denominator. Any unexplained added/lost row or missing map must produce INCOMPLETE, preserving the claim. This enforces the existing population/coverage requirements rather than changing the gate.

The current outcome-free counts file (SHA `372e61ead40549325fb0e3c6d71081c38fdd3db206d6a00d3448c52c42e99a10`) declares **1,319/1,328 usable binding games**, nine missing, instead of the earlier 1,327: Autarky433/435, Maze442/446, Trauma444/447, all >95%. Hinata independently posted the same correction at14:48. No confirmation label underlies these counts. Counts are upper bounds on decisive rows because draws were not inspected. All listed binding cells exceed50; the predeclared report-only list is only elim/r10. Do not remove missing games from the original denominator.

## Forecast, effect and dissent

Exact-event P(PASS) remains **0.40**, as filed before the claim; do not revise it from repair evidence. Expected model effect remains the development-based +0.02 AUC at r50 and +0.05 to +0.10 late if transfer holds, not a held-out measurement. Fixing this plumbing has no intended model-performance effect.

I support the implemented finite and receipt repairs. My remaining dissent is solely release readiness: cryptographically sealing a changing membership does not validate the intended estimand. Known precedent: an immutable analysis cohort and explicit participant flow preserve an intention-to-evaluate denominator. RL translation: critic validation must use the predeclared held-out transitions and legal deployment claims remain separate; no behavior or teacher demonstration is added.
