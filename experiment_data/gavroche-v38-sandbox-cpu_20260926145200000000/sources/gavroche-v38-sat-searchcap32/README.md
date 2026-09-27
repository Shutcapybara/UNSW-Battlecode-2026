# Gavroche v38: saturated target-search cap 32

Parent: Gavroche v36 (V35 with a saturated target-search cap of 64).

This version lowers the saturated target-search cap from 64 to 32 nodes once
the density-policy population reaches the existing 70% saturation gate. The
normal 160-node cap remains active while sparse, the first two turns of a new
dragon retain the 60-node birth cap, and the dense-phase sprint cutoff remains
6. It targets the rare peaks that stayed above 80M after V36 brought p99 below
60M.

The six-map, nine-opponent panel uses `fixture_hash_v1` seeds, shared for both
sides and candidate versions. This experiment checks whether reducing the
side assignments and candidate versions. A seeded native panel and sandbox
CPU screen are required before any promotion decision.
