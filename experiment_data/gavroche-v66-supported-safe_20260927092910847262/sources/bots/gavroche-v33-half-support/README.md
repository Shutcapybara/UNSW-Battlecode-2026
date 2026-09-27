# Gavroche v33: half-strength support trades

Parent: Gavroche v31 (v17 policy with the saturated sprint cap and
`v_dive = 3`).

V32 added one point of strike gain per nearby allied head, within three torus
steps and capped at two heads. Its completed panel tied V31 at 29–19 across
Sinbad, tf05, grad1, and x04, while shifting results from tf05 (V31 9–3, V32
5–7) toward x04 (V31 8–4, V32 10–2). This version keeps the same support radius
and cap but halves the bonus to test whether a smaller combat adjustment keeps
the x04 gain without the tf05 regression.

The native comparison uses a stable map/opponent seed shared by both sides and
all candidate versions. CPU safety still requires separate judge-sandbox
validation; this inherits V31's sprint guard.

## Results

The 108-game six-map panel scored 74–34 with zero errors or runtime faults:
6–6 vs V31, 7–5 vs V32, 10–2 vs V23, 9–3 vs V17, 9–3 vs Sinbad, 8–4 vs tf05,
8–4 vs grad1, 8–4 vs x04, and 9–3 vs Monte. The four-family record was 33–15.
Judge-sandbox validation on Big Empty and Trauma, both sides vs V31, reached
91.9–99.6M max and 74.6–76.2M p99 on Big Empty, and 85.6–95.5M max and
60.6–61.4M p99 on Trauma. Those peaks are too close to the 100M ceiling for
promotion.
