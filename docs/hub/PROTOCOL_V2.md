# Protocol v2 (prospective; applies to experiments opened by the hub actuator after cutover)

A candidate is an immutable source (fingerprint) with a hypothesis, a mechanism and an activation contract. It must
pass two metered local probes on the pinned toolkit (Schooltime as A, Portals as B, against `bots/sinbad-v07-divecap`;
zero faults, zero caught `MC_ERROR`, max < 80 M, p99 < 60 M, metering reconciled), its activation contract, upload
with `-ai`, and all-map live dev coverage (runtime only: zero faults, `cpu_recorded == turns`, max < 95 M). Against
the current control it then plays a selecting screen (three frozen opponents, ten exact-layout pairs each, order
randomized per block, futility stop at net ≤ −4 after block 1 or cumulatively after block 2, pass iff net > 0 with
zero faults) and, if selected, one fresh confirmation: twelve distinct new opponents, ten pairs each, futility-only
looks at 6 (mean ≤ 0) and 9 (mean ≤ +0.01) blocks, efficacy once at 12: mean paired delta ≥ +0.03, one-sided block
sign-randomization p ≤ 0.025, no map worse than −0.25, twelve distinct opponents, zero faults, at least eight
opponent submissions unchanged within their blocks. One confirmation per (code fingerprint, control). A lineage with
two `strategy_lost_*` verdicts in seven days needs a published finding describing the changed mechanism before a
third screen. Promotion is A-side evidence, followed by probation: automatic rollback on any runtime fault or caught
error; review (not rollback) on a ≥ 25 pp band-matched deficit over the first 20 incoming games. External activations
freeze running comparisons; candidates are re-compared against the new control, never orphaned. Dev games, local
ratings and screens never promote.

Experiments opened under the legacy protocol keep protocol v1 to completion (`tools/hub/stats.py::decision_v1`:
three-block screen, twelve-block fixed confirmation, α = 0.05/[(n+1)(n+2)] with n = prior experiments, six fills,
twelve exclusions). The hub stores `protocol` per experiment and never evaluates a v1 experiment with v2 or the
reverse (`tools/hub/stats.py::decision_v2`).

Cost of one full v2 pass: ≈ 20 dev + ≤ 60 screen + ≤ 240 confirmation games + fills ≈ 320 games, ≈ 7 executor-hours
at 45 field games per hour. Power: with the observed block SD ≈ 0.18, twelve blocks detect ≈ +15 pp at 80 % power;
a true +3 pp is detected rarely. The screen and local evidence must do the selecting.
