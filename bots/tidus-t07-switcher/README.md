# tidus-t07-switcher: contextual posture switching (owner's idea) — UNBUILT-OUT

t05 (mid-crowd relaxation) screens +3 but fails the gauntlet (141-41, −4).
t07's scaffold implements the owner's contextual-switching proposal: each
dragon latches a map classification from observed terrain (seen-kelp
fraction >= kelp_thresh after >= switch_min_edges learned edges) and applies
the mid-crowd relaxation only on classified-contested maps.

**Not activated**: the t05 gauntlet response labels do not replicate across
panels (devil +2 screen → 0 gauntlet; Schooltime's −4 contains +2 wins and
−5 losses by opponent; feature ranges fully overlap between responding
maps). Any threshold fit on n=14-games-per-map labels fits knife-edge noise.
Stable labels need ~50+ games per map per arm (~650 games). The scaffold
stays default-off (`crowd_mid_switch 0`); fill `kelp_thresh` from
replicating labels if that compute is ever spent.
