# Gavroche v38: saturated target-search cap 32

Parent: Gavroche v36, which uses a saturated target-search cap of 64.

This version lowers the saturated target-search cap from 64 to 32 nodes once
the density-policy population reaches the existing 70% saturation gate. The
normal 160-node cap remains active while sparse, the first two turns of a new
dragon retain the 60-node birth cap, and the dense-phase sprint cutoff remains
6. It targets the rare peaks that stayed above 80M after V36 brought p99 below
60M.

The six-map, nine-opponent panel uses `fixture_hash_v1` seeds, shared across
both side assignments and candidate versions.

The seeded 108-game native panel scored 72–36 with zero errors/runtime faults:
7–5 vs V33, 5–7 vs V31, 10–2 vs V23, 9–3 vs V17, 9–3 vs Sinbad, 8–4 vs tf05,
8–4 vs grad1, 9–3 vs x04, and 7–5 vs Monte. Its Sinbad/tf05/grad1/x04 aggregate
was 34–14. Map totals were Autarky 16–2, Big Empty 13–5, Queen 14–4,
Schooltime 11–7, Stronghold 10–8, and Trauma 8–10.

Judge-sandbox CPU measurement is running in
`experiment_data/gavroche-v38-sandbox-cpu_20260926145200000000`.
