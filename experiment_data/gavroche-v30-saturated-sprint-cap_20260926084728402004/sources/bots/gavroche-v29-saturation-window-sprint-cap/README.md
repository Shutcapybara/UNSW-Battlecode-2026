# Gavroche v29: saturation-window sprint cap

Parent: Gavroche v19 (v17 policy plus behavior-preserving flood/density work).

The v17 Big Empty missing-action deaths occurred at rounds 49–199 while the
team had 44–64 units of a 64-unit cap. That is the early saturated phase where
long-body sprint candidate enumeration raises CPU cost. V23 capped
three-step candidates to lengths 4–7 for the whole game and lost 4–8 to v17 on
the replay maps.

V29 keeps v17's full three-step range (lengths 4–11) except while density
policy is enabled, before round 200, and the team has at least 70% of its unit
slots filled. During that load window it caps three-step candidates at lengths
4–7. This condition is independent of the optional information-gradient push,
which is disabled in this policy line.
