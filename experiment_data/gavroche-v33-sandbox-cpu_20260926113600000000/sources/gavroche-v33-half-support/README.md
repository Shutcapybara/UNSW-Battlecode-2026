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
