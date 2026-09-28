# Ed v10: route-conditioned feeding with staggered donor cohorts

This experiment descends from Ed v08. It keeps the same route-aware time and
state gate, but admits only one modulo-id donor cohort in each 32-round window.
An admitted donor keeps its role for the window so it can complete the route to
the current crown. This tests whether limiting simultaneous donor departures
avoids the mass-feeding observed in the v08 verbose traces.

The production default remains off (`feed_mode=0`). The experiment override
selects `feed_mode=4`; `feed_cohort_count=32` and
`feed_cohort_rounds=32` define the deterministic schedule.
