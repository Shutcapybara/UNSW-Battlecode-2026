# Sparta 01 — queen priority

Sparta 01 starts from Carthage 05 (`carthage-05-free-sprint`), keeping its
1.2.3 sprint pricing, free on-route sprints, bounded search, threat scoring,
and HB-1 direction prior. The parent also carries the higher target-search
bounds from Bifröst and Skadi and Fafnir's size-matched counter-threat support.
It adds a queen-first strategy in both directions.

When any dragon sees the opponent's original queen, it records and shares that
position through Carthage's existing prey sonar packet. The report stays live
for 60 rounds. Every non-queen dragon routes toward the freshest reported
position, including dragons that would otherwise forage, feed, or hold the
crown role. A large route bonus makes that pursuit outrank ordinary goals. If
a non-queen dragon can trade heads with the enemy queen, the policy takes the
trade regardless of relative length or team size.

Our original queen is identified by team and starting ID. It rejects moves
that die in simulation, move onto a cell an enemy head can reach, or enter a
head-on trade. If every available move is unsafe, the ordinary fallback still
chooses a move. Existing constrained-newborn escape can also temporarily
override a queen hunt. The guard does not forecast multi-turn entrapment or
enemy threats outside the visible danger map.

The enemy-queen hunt starts after a teammate has seen the queen; it cannot
infer an unseen location. A remembered position can become stale within its
60-round lifetime, and the queen may have already died. These cases, queen
survival, head-on trade value, and overall results need a serial paired panel.

In the first focused serial screen, Sparta 01 scored 17–23 against Carthage
05 and four frontier controls over Devil, Queen of Spades, Schooltime, and
Trauma (40 games, zero runner errors). It went 4–4 against Carthage 05. This
is exploratory evidence on one screen and does not establish a general
ranking. The outcome and queen-death breakdown are in the
[Sparta 01 screen finding](../../docs/findings/2026-10-02-sparta01-focused-screen.md).
