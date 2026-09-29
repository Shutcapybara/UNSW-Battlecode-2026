# Ares V02 — Tyr V12 policy in the Anna C++ chassis

Ares V02 is a standalone C++ strategy snapshot copied from the Anna A02
protocol-3 scaffold. Its local decision policy translates Tyr V12's resource
routing and action scoring into the Anna world model; it has no Python runtime
dependency.

The translated policy includes discounted pearl/bed/exploration targets,
target hysteresis, Yuna direction-momentum EWMA, length-aware endgame value,
production and trapped-tail splits, enemy head trade valuation, threat and room
scoring, bounded sprints, and Tyr V12's Devil center/lane/friendly-body terms.
It also ports Tyr's sonar food gossip, remote density reports, crown and prey
beacons, paired-portal sharing, and crown inheritance on large-child splits.
Anna's C++ protocol handling, map atlas, portal model, and time-aware room flood
provide the runtime substrate.

The port retains Anna's hard safety tiers and room-valid split checks, so its
action ordering is an adaptation rather than a behavior-identical replay of
Tyr V12. In a native one-seed direct screen against Tyr V12, it lost 20–0 over
ten maps and both seats. This is a narrow matchup result, not the fixed-panel
benchmark in [BENCHMARKS.md](../../docs/analysis/BENCHMARKS.md); Ares V02 remains
experimental. See the [matchup report](../../docs/findings/2026-09-29-ares-v02-vs-tyr-v12.md).
