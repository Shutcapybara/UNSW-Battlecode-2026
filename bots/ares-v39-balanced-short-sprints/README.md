# Ares V39 — balanced short-sprint payoff

V39 branches from V38 after its 4.0 payoff proved too generous in a ten-map
seed-1 comparison: V38 lost 7–13 to V37 and used length-3 dashes on 3.9% of
length-3 turns, versus 1.1% for V37. Each length-3 dash still pays an extra
1.5 score cost, but its payoff is now 2.5, equal to that premium plus the
existing 1.0 sprint cost. Escape-plan arrivals do not receive the payoff;
their normal tactical safety score remains active.

V39 also lost **7–13** to V37 on the same seed-1 ten-map panel. The reduced
reimbursement and removed escape refund did not improve the result. V40 tests
length-based accounting instead; see the [V39 finding](../../docs/findings/2026-09-30-ares-v39-balanced-short-sprints.md).

Longer dragons keep V37 sprint scoring. Fresh pearl and bed targets, the crown
threat model, newborn portal handoff, 40-round memory limit, and age-3 portal
gate are unchanged.

The focused regression checks the three visible nearby heads from match
686866, a dense-threat stress case against the V37 control, and retained dashes
for second-step pearl and bed rewards. Replay data omits persistent bot and
radio inputs, so the fixture does not exactly reproduce the recorded move.
