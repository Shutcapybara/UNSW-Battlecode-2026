# Gavroche v37: no dense-phase triple moves

Parent: Gavroche v36 (V35 with a saturated target-search cap of 64).

This version keeps the 64-node target-search cap at the existing 70% saturation
gate, with the 160-node sparse cap and 60-node birth cap unchanged. It changes
only the saturated three-step move threshold from 6 to 4. This removes
three-step candidates for length-4/5 dragons once dense, the remaining candidate
fanout that can cause CPU peaks after V36's target-search reduction.

The six-map, nine-opponent panel uses `fixture_hash_v1` seeds, shared across
both sides and candidate versions.

The 108-game native panel scored 70–38 with zero errors/runtime faults: 7–5 vs
V33, 5–7 vs V31, 9–3 vs V23, 7–5 vs V17, 8–4 vs Sinbad, 8–4 vs tf05, 9–3 vs
grad1, 8–4 vs x04, and 9–3 vs Monte. The Sinbad/tf05/grad1/x04 aggregate was
32–16. Map totals were Autarky 16–2, Big Empty 10–8, Queen 14–4, Schooltime
10–8, Stronghold 13–5, and Trauma 7–11.

The four-game sandbox screen completed 500 rounds each without faults. V37
p99/max was 54.4–57.4M / 88.8–88.8M on Big Empty and 59.2–61.3M /
87.9–90.6M on Trauma. Removing dense-phase triples did not materially improve
the worst peak and one Trauma p99 exceeds 60M; it misses the conservative
max <80M gate. See `experiment_data/gavroche-v37-sandbox-cpu_20260926133000000000`.
