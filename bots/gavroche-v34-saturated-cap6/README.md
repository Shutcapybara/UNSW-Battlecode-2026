# Gavroche v34: dense-phase sprint cap at six

Parent: Gavroche v33 (V31 with half-strength support-weighted trades).

V33 scored 74–34 on its 108-game, nine-opponent native panel. It reached a
99.6M judge-sandbox peak on Big Empty and 95.5M on Trauma, so it lacks CPU
headroom. This version changes only the dense-phase three-step cutoff: dragons
of length 4–5 retain three-step moves, while length 6 and above use at most
two steps once allied population reaches the existing 70% saturation gate.
Sparse-team behavior and all trade weights remain the same.

The six-map panel uses a stable seed per opponent and map, shared across both
sides and candidate versions. CPU safety still requires sandbox measurement.

The completed 108-game native panel scored 73–35 with zero errors/runtime
faults: 4–8 vs V33, 6–6 vs V31, 10–2 vs V23, 11–1 vs V17, 9–3 vs Sinbad, 7–5
vs tf05, 9–3 vs grad1, 9–3 vs x04, and 8–4 vs Monte. Its record against
Sinbad/tf05/grad1/x04 was 34–14.

Judge-sandbox validation completed four 500-round games on Big Empty and
Trauma, both sides vs V31, with no invalid actions or timeouts. V34's maximum
was 90.9–95.9M on Big Empty (p99 73.2–74.4M) and 84.7–88.1M on Trauma (p99
58.1–61.2M). It stays below the 100M hard ceiling in this sample, but misses
the conservative p99 <60M / max <80M promotion gate. Search work under
saturation remains the next CPU target.
