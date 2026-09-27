# Gavroche V66 supported sparse-room guard

Parent: V54. Preserve V54's CPU-safe round-40 search guard and late sparse
movement room, then raise the nearby-allied-head strike bonus from 0.5 to
0.75. This carries V65's grad1 combat hypothesis onto a lower-workload base.
The bonus applies per visible allied head within torus radius 3, capped at two
heads; this was the only policy change from V54.


Results: CPU screen 2–2 vs V31; all four samples passed (p99 42.2–43.5M, max 52.5–63.9M, zero faults/timeouts). The seeded panel stopped at 88/108 (54–34) with zero runtime faults. It scored 25/40 against Sinbad/tf05/grad1/x04 (8–4, 8–4, 6–6, 3–1). Its priority-family ceiling was 33, below the 38 needed to beat V36's 37; overall score could still have reached 74. On the same 88 fixtures, V54 scored 56 wins and 28/40 priority-family wins. See `experiment_data/gavroche-v66-supported-safe_20260927092910847262` and `experiment_data/gavroche-v66-sandbox-cpu_20260927091721000000`.
