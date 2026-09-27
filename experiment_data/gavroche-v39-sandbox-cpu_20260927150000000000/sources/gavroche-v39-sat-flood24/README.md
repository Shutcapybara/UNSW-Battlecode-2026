# Gavroche v39: saturated long-body flood cap 24

Parent: Gavroche v38, with the saturated target-search cap of 32.

The CPU review of V38 found late saturated turns where length-10/11 dragons
used most of the per-turn budget. Their safety flood evaluates candidate moves
up to 40 reachable cells. This version retains that 40-cell bound in sparse
play but caps the flood at 24 cells for long bodies once allied population
reaches the existing 70% saturation gate. Targeting and move candidates are
unchanged.

This is a CPU probe: first measure Big Empty and Trauma with the judge sandbox.
If it reduces peaks while preserving the <60M p99 / <80M max gate, run the
seeded strategic panel before considering it further. No candidate is
submitted without a new explicit request.
