# Ares V01 — safe launch routing

Ares V01 is a new C++ strategy snapshot built from the protocol-3 world model and cheap opening policy in anna-a02-chassis. Anna remains untouched; this copy has its own ares namespace and source tree.

## Changes in V01

- Routine 2-segment production waits for a known, reachable bed or pearl near the rear child. The gate also keeps the child and its first target clear of visible allied heads. When a new map is still poorly observed, the Anna production rule remains available.
- A boxed-in dragon sizes its emergency split from the tail side. It keeps the largest child that the room flood says can escape; when no size clears the room check, it chooses the size with the best measured escape margin.
- A tiny, positive-only ID lane bonus breaks opening target ties. One in three IDs gets a small preference for targets whose known route uses a paired portal. Neither bonus can beat a route that is at least one full step shorter.
- Re-entering the same portal pair shortly after a transit gets a small cost while the head remains near its remembered landing. This is a soft cost; it does not turn off portal use.
- Anna's exact one-step movement check, known portal landing simulation, time-aware room flood, and visible enemy sprint reach remain in place.

These choices use Tyr V12's positive-only lane tie-break as a weak opening nudge. V12's all-map screen was 50–42 versus Yuna V05 with a large seat split, so Ares does not treat that as an all-map promotion. Bifröst's broad identity-based route and net-growth experiments had repeated map regressions; Ares keeps the lane bonus below one route step and does not hard-code a dead-end pearl-value threshold. Its emergency sizing is only used when every immediate move is blocked. The newborn and portal targets come from the 29–30 September loss and efficiency reviews.

## Validation status

V01 completed a seed-1 fixed panel on unswbc 1.2.1: 160 games against the eight-bot roster and 20 direct games against Anna, across ten live maps and both seats. It remains experimental: the four-checkpoint economy mean rose by 0.030 field medians against the +0.05 gate, and ally-body deaths rose 44.3% against the 10% guardrail. Full metrics and limitations are recorded in [the Ares family notes](../../docs/ares-family.md) and [the V01 finding](../../docs/findings/2026-09-29-ares-v01-safe-launch-routing.md). A separate 20-game direct screen against Tyr V12 was 0–20 for Ares, with Tyr sweeping both seats on every live map.
