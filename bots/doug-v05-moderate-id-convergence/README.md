# Doug V05 — moderate ID-aware convergence

**Base:** Tyr V12, including its Devil scouting tie-break and reduced search
caps.

**Changes:** V05 uses a moderate earlier length phase: production and the
non-crown value ramp begin at round 330, crown claims at round 220 require a
length-6 dragon, and feeding opens slightly earlier. It keeps the conservative
early-game population signal. Engine dragon IDs are sequential, so Doug tracks
the highest recently observed enemy-owned ID and combines that frontier with
its exact own unit count and observed positive population deltas. With a safety
margin for unseen deaths and same-turn birth/death pairs, an equal-length
head-to-head gets extra value only when the opponent is estimated to be ahead
and only during rounds 20–180. The signal expires when the ID frontier is
stale; it never treats a local/stale ID as a global count.

This is an early-convergence experiment, not a promotion claim. Results are
recorded with the Doug comparison panels as they are run. V04's more aggressive
round-260 phase was rejected after a 1–9 direct screen against Tyr V12.
