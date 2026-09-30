# Ares V43 — exploration-only teammate separation

V43 branches from V42 and retains its memory discount for exploration in
remembered sectors without known pearl beds. It keeps the Devil lane bonus
removed, as requested.

V42 charged moves that closed on a visible teammate even while pursuing a
pearl or prey. V43 applies that bounded cost only when the selected goal is
exploration, including fallback exploration targets. Pearl and prey routes
keep their normal movement scores; crown and feeder roles remain exempt.

In a native ten-map, both-seat screen against V41, V43 scored **12–8** with no
runner errors, replay-analysis errors, or runtime faults. It swept Default,
Dilemma, Queen of Spades, Slithery Fight, and Trophy. V41 swept Devil, Portals,
and Schooltime; Autarky and Trauma split. This is one generated-seed screen;
V43 remains experimental. Logs, replays, and the report are in
`experiment_data/ares-v43-exploration-only-dispersion_20260930125019196045/`.
See the [V43 finding](../../docs/findings/2026-09-30-ares-v43-exploration-only-dispersion.md).

The contest accepted the upload as submission **v95**, reported as processing.
Submission does not promote the local candidate.
