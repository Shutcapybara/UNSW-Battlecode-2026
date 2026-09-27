# Gavroche v37: no dense-phase triple moves

Parent: Gavroche v36 (V35 with a saturated target-search cap of 64).

This version keeps the 64-node target-search cap at the existing 70% saturation
gate, with the 160-node sparse cap and 60-node birth cap unchanged. It changes
only the saturated three-step move threshold from 6 to 4. This removes
three-step candidates for length-4/5 dragons once dense, the remaining candidate
fanout that can cause CPU peaks after V36's target-search reduction.

The six-map, nine-opponent panel uses `fixture_hash_v1` seeds, shared for both
side assignments and candidate versions. Native panel results are pending.
Judge-sandbox CPU measurement is required before any promotion decision.
