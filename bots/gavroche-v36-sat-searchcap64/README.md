# Gavroche v36: saturated target-search cap 64

Parent: Gavroche v35 (V34 with a saturated target-search cap of 96).

This version caps target-search expansion at 64 nodes once the density-policy
population reaches the existing 70% saturation gate. V35's Big Empty p99 fell
to 56.4–57.9M, but peaks were still 82.6–91.0M. The normal 160-node cap
remains active while sparse, and the first two turns of a new dragon still use
the 60-node birth cap. The intent is to reduce high-population per-turn CPU
while preserving the established low-density search range.

The six-map, nine-opponent panel uses `fixture_hash_v1` seeds, shared for both
sides and candidate versions. This experiment checks whether reducing the
saturated cap further lowers CPU peaks without giving up the broader matchup
strength. Judge-sandbox CPU measurement is required before any promotion
decision.

The seeded 108-game native panel completed 73–35 with zero errors/runtime
faults: 6–6 vs V33, 6–6 vs V31, 10–2 vs V23, 6–6 vs V17, 10–2 vs Sinbad, 7–5
vs tf05, 10–2 vs grad1, 10–2 vs x04, and 8–4 vs Monte. The
Sinbad/tf05/grad1/x04 aggregate was 37–11. Map totals were Autarky 16–2, Big
Empty 11–7, Queen 14–4, Schooltime 12–6, Stronghold 13–5, Trauma 7–11.

The four-game judge-sandbox screen completed 500 rounds each against V31,
with 3–1 wins and no invalid actions or timeouts. Candidate p99 was below 60M
in all four games: 52.9–54.4M on Big Empty and 57.6–59.3M on Trauma. Peaks were
83.0–91.6M and 75.7–89.8M respectively, so three of four games exceed the
conservative max <80M gate. The dense-phase triple-move enumeration for
length-4/5 dragons is the next targeted CPU reduction.
