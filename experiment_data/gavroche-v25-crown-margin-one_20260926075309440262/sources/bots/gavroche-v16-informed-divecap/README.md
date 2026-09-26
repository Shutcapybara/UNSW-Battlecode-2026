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

## Cross-family comparison

Native, both sides, 13 maps, 182 games, no runner or runtime errors:
111–71 overall (61.0%). It scored 77–53 (59.2%) against the five model-family
references: Sinbad v07 13–13, x06 tf-05 12–14, reconstructed x06 grad1 21–5,
x04 support 15–11, and Monte Christo x12 16–10. It beat the Gavroche v13
baseline 21–5 and split v15 13–13. The five-family pool is essentially tied with v15. V17 halves the push and
scored 84–46 (64.6%) against the same five references, compared with v16 at
77–53 (59.2%). On the shared seven-opponent panel, v17 scored 112–70 after
excluding its 13–13 v16 head-to-head, versus v16 at 111–71. Treat the overall
results as close and keep v16 as the high-push alternative; v17 is the stronger
current generalist against the pulled model families. These are native results,
not judge CPU validation.

Replay trouble-map results across all seven references: Big Empty 7–7,
Prisoner's Dilemma 13–1, and Trophy 6–8. This confirms the Dilemma result is
strong, while Big Empty and Trophy remain opponent-sensitive.

Full report: `experiment_data/gavroche-v16-informed-divecap_20260926052903274524/summary.md`.
