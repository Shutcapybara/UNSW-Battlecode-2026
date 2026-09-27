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

The seeded 108-game native panel completed 68–40 with zero errors or runtime
faults. Records were 3–9 vs V33, 5–7 vs V31, 9–3 vs V23, 9–3 vs V17, 6–6 vs
Sinbad, 9–3 vs tf05, 8–4 vs grad1, 10–2 vs x04, and 9–3 vs Monte. The
Sinbad/tf05/grad1/x04 aggregate was 33–15. Map totals were Autarky 16–2, Big
Empty 10–8, Queen 14–4, Schooltime 11–7, Stronghold 11–7, Trauma 6–12.

The four-game sandbox screen completed 500 rounds per game without invalid
actions or timeouts. V35 p99 was 56.4–57.9M on Big Empty (max 82.6–91.0M) and
59.8–60.7M on Trauma (max 85.2–88.2M). Big Empty p99 improved substantially
over V34; the sample still misses the conservative p99 <60M / max <80M gate.
See `build/leviathan/20260926-221020-gavroche-v35-sat-searchcap96/report.md`.
