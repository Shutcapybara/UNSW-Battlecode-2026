# Gavroche v28: gradient-window sprint cap

Parent: Gavroche v19 (v17 policy plus behavior-preserving flood/density work).
The v17 Big Empty missing-action deaths occurred at rounds 49–199 while the
team had 44–64 units of a 64-unit cap. That overlaps the high-saturation early
density-gradient branch. V23 capped three-step candidates to lengths 4–7 for
the whole game and lost 4–8 to v17 on the replay maps.

V28 keeps v17's full three-step range (lengths 4–11) except while the early
density-gradient branch is active; in that window only lengths 4–7 retain
three-step candidates. This tests the CPU hotspot directly while restoring
longer sprint tactics after the gradient phase or before saturation.
