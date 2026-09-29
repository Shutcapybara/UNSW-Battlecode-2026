# Doug V17 — no-momentum early crown

**Base:** Tyr V12, including its Devil scouting tie-break and reduced search
caps.

**Changes:** V17 keeps Tyr V12's round-380 production and non-crown growth
schedule, but starts crown claims at round 200 once a dragon reaches length 6.
The crown's segment value rises to 4.5 and feeding opens earlier. This lets
one large dragon begin converging while the rest of the team preserves the
population race. It keeps the conservative early-game population signal and
ID-aware own-lead equal trades. It removes only the Yuna-derived directional
momentum term to test whether momentum interferes with large-dragon banking.
Engine dragon IDs are sequential, so Doug tracks
the highest recently observed enemy-owned ID and combines that frontier with
its exact own unit count and observed positive population deltas. With a safety
margin for unseen deaths and same-turn birth/death pairs, an equal-length
head-to-head gets extra value only when the opponent is estimated to be ahead
and only during rounds 20–180. The signal expires when the ID frontier is
stale; it never treats a local/stale ID as a global count.

This is an early-convergence experiment, not a promotion claim. Results are
recorded with the Doug comparison panels as they are run. The global early
split-stop variants were rejected because they gave up too much population.
