# Ares V38 — purposeful short sprints

V38 lost **7–13** to V37 in a seed-1, ten-map comparison. Replay action counts
showed length-3 dragons dashed on 3.9% of their turns, versus 1.1% for V37.
The 4.0 payoff over-reimburses the dash cost. V39 and V40 test different
accounting changes; see their findings for results.

V38 branches from V37 to stop length-3 dragons spending a third of their body
on routine two-step moves. Each such dash pays an extra 1.5 score cost. It gets
a 4.0 payoff only if its second step collects an additional pearl or lands on
the selected pearl, bed, portal, prey, escape, or crown target. The existing
threat model can still justify a dash when its safety advantage outweighs
this added cost.

Longer dragons keep V37 sprint scoring. Fresh pearl and bed targets, the crown
threat model, newborn portal handoff, 40-round memory limit, and age-3 portal
gate are unchanged.

The motivating replay is match 686866: at UI round 16, dragon 25 was length 3
and dashed EN without collecting a pearl. The focused fixture uses its three
nearby visible enemy heads and checks that enemy proximity alone does not make
a routine exploratory dash worthwhile. Replay data omits persistent bot and
radio inputs, so this fixture is not an exact reproduction of the recorded
decision. It also checks that second-step pearl pickups and selected high-value
targets can still justify a dash. A separate dense-threat stress fixture adds
two hypothetical nearby heads; its V37 control chooses EN while V38 chooses
one-step E. See the
[V38 finding](../../docs/findings/2026-09-30-ares-v38-purposeful-sprints.md).
