# Gavroche v16: informed dive cap

Parent: Gavroche v15. This combines the Sinbad v07 portal-value reduction
(v_dive 7 to 3) with the leading Von Neumann x06 gradient idea. During the
opening, a forager whose team is at least 70% saturated gets a room-normalised
push toward locally enemy-controlled space. The existing resource discount
still selects targets; the added push applies only after the team is crowded,
and it weakens in tight space.

Von Neumann x06 measures enemy-minus-ally length density with its information
layer. Gavroche adapts the same direction from its existing communicated head
density and bounds the gain by a 12-cell local flood. This keeps the candidate
self-contained and leaves Gavroche's messaging and resource valuation intact.

The supplied replay set has four 11-map series with strongly
opponent-dependent results (Team A: 6/11, 4/11, 7/11, and 2/11). Big Empty,
Prisoner's Dilemma, and Trophy recur as losses; results on other maps vary by
opponent. v15 isolates the dive change, while v16 tests whether the density
gradient recovers expansion without sacrificing the matchups v13 already
handles.

Pending comparison on the full 13-map roster, both sides, against the v13
baseline, Sinbad v07, Von Neumann x06 grad1 and tf-05, Von Neumann x04 support, and Monte
Christo x12.
