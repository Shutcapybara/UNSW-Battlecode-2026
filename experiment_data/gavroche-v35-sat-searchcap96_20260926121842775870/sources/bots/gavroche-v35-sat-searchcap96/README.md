# Gavroche v35: saturated target-search cap

Parent: Gavroche v34 (V31 with half-strength support-weighted trades and the
dense-phase length-6 sprint cutoff).

This version caps target-search expansion at 96 nodes once the density-policy
population reaches the existing 70% saturation gate. The normal 160-node cap
remains active while sparse, and the first two turns of a new dragon still use
the 60-node birth cap. The intent is to reduce high-population per-turn CPU
while preserving the established low-density search range.

The six-map, nine-opponent panel uses `fixture_hash_v1` seeds, shared for both
sides and candidate versions. Judge-sandbox CPU measurement is required before
any promotion decision.
