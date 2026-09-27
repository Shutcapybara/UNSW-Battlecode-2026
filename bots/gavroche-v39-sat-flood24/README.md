# Gavroche v39: saturated long-body flood cap 24

Parent: Gavroche v38, with the saturated target-search cap of 32.

The CPU review of V38 found late saturated turns where length-10/11 dragons
used most of the per-turn budget. Their safety flood evaluates candidate moves
up to 40 reachable cells. This version retains that 40-cell bound in sparse
play but caps the flood at 24 cells for long bodies once allied population
reaches the existing 70% saturation gate. Targeting and move candidates are
unchanged.

The four-game sandbox screen completed 500 rounds each against V31, 4–0 with
no invalid actions or timeouts. Candidate p99/max was 53.3–53.5M / 81.3–95.2M
on Big Empty and 61.1–62.6M / 85.0–89.4M on Trauma. The dense long-body flood
cap did not reduce the Big Empty peaks and raised Trauma p99 above 60M, so the
variant does not qualify for a strategic panel. See
`experiment_data/gavroche-v39-sandbox-cpu_20260927150000000000`.
