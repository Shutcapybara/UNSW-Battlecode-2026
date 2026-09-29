# Ares V04 — Tyr V12 behavioral parity port

Ares V04 is a C++ translation of Tyr V12's active policy on the Anna A02 protocol-3 runtime scaffold. Anna contributes the process and protocol adapter; Tyr supplies the policy and state semantics.

The port was compared against Tyr V12 on the same ordered input transcripts from all ten live maps and both seats. It matched every move, split, and sonar output across 168,123 turns (5,089 dragons), with zero divergences. The replay set and scope are recorded in the [V04 parity finding](../../docs/findings/2026-09-29-ares-v04-behavior-parity.md). This checks observable policy behavior on those transcripts; it does not prove equivalence on every possible state.

The contest upload is submission v83 (ID 11244), currently listed active by the platform. Ares V04 remains experimental and is not admitted to the local frontier. Its fixed-panel benchmark and field-reference scorecard are documented in the finding; the port is not promoted by behavioral parity alone.
