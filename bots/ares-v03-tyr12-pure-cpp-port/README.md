# Ares V03 — pure Tyr V12 C++ port

Ares V03 ports Tyr V12's strategy to C++ on the Anna A02 protocol-3 runtime scaffold. Anna supplies the controller adapter and persistent world model; the decision policy follows Tyr's discounted target search, scalar movement scoring, threat valuation, split scoring, sprint candidates, Devil bonuses, radio roles, and newborn separation.

The active policy has no Anna action tiers, nearby-enemy split veto, hard parent-room split gate, or atlas-based map knowledge. The C++ world tracker still reconstructs visible and remembered body state, so this is a policy port on the Anna runtime rather than a bit-for-bit replay of Tyr's Python observations.

The native seed-1 screen against Tyr V12 covered the same ten live maps and both seats: Tyr won 12–8. Replay extraction succeeded for all 20 games. The match is a direct comparison, not the 140-side-game fixed-panel acceptance run in [BENCHMARKS.md](../../docs/analysis/BENCHMARKS.md). Results and benchmark-aligned metrics are in the [V03 finding](../../docs/findings/2026-09-29-ares-v03-vs-tyr-v12.md). Ares V03 remains experimental; no post-screen policy tuning was done.
