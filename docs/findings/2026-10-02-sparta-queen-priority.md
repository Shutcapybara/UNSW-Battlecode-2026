# Sparta 01 — queen priority (experimental)

Sparta 01 forks `carthage-05-free-sprint` into a new family line. It keeps the
parent's 1.2.3 sprint rules and free on-route sprints, then combines a direct
queen survival guard with priority hunting of the opponent's original queen.
This document records the code hypothesis; no result is available yet.

## Mechanism

- Identify the original queen by team and starting ID: A's queen is 0 and B's
  is 1.
- For our queen, score simulated death and head-on choices below all normal
  moves. Also veto a valid landing cell marked reachable by a visible enemy
  head. This uses Carthage's movement simulation and danger map, and does not
  suppress ordinary production splits or portal actions.
- When a dragon sees the opposing queen, store its cell as the priority prey
  and transmit it using the existing type-4 sonar packet. Preserve that target
  for 60 rounds and prefer it to generic prey reports while fresh.
- Route every non-queen dragon toward the remembered queen cell, even when
  that dragon would otherwise forage, feed, or hold the crown role. Give a
  non-queen head-on against a currently visible enemy queen a dominant score,
  without the normal team-size, relative-length, or material-gain gates.
  A large route-progress bonus makes pursuit outrank ordinary move goals.
  Existing constrained-newborn escape logic can temporarily take precedence.

The target is last-known information, not a confirmed living-queen track. A
fresh report can already be stale if the queen moved or died. An aggressive
trade removes the hunter too and does not necessarily end the game. Our queen
guard addresses only reachable head-on threats; it does not solve walls,
allied-body trapping, or long-term survival.

## Evidence and interpretation

Carthage 05's full sprint bundle improved paired win share against Carthage
00 on both recorded panels, while the direct 05-versus-04 free-sprint
increment was inconclusive on the pool. Preserve those scopes when choosing
the baseline for Sparta. Previous Carthage queen interventions changed queen
survival but often paid for it in production or moved deaths to other causes.
Kyoto's queen guard is a useful design reference, not evidence that this
particular hybrid wins. See the [Carthage queen findings](2026-10-01-carthage-base-and-queen.md),
[Carthage sprint findings](2026-10-02-carthage-sprint-rules.md), and
[Kyoto queen findings](2026-10-01-kyoto-base-and-queen.md).

## Proposed evaluation

Compare Sparta 01 directly with Carthage 05 on the same fixtures. Use both
pool and generated panels, seeds 1–3, both seats, and serial execution. Keep
the existing 1.2.3 win-led gate and report paired overall score, economy,
units and total length at round 100, errors and timeouts. For the queen
mechanism, also report actual reach to round 490, queen alive among reached
games, the joint alive-and-reached rate, queen death cause, and enemy queen
deaths. Keep pocket maps in overall results and label structural map splits
as diagnostics. Treat the queen survival threshold as a mechanism falsifier,
not a substitute for overall wins.

No build, test, runtime check, or tournament has been run for this snapshot.
