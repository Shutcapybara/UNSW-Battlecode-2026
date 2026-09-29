# Doug V10 — own-lead equal trades

**Base:** Tyr V12, including its Devil scouting tie-break and reduced search
caps.

**Changes:** V10 keeps Tyr V12's round-380 production and non-crown growth
schedule, but starts crown claims at round 200 once a dragon reaches length 6.
The crown's segment value rises to 4.5 and feeding opens earlier. This lets
one large dragon begin converging while the rest of the team preserves the
population race. It keeps the conservative early-game population signal, but
correctly values equal-length trades only when Doug estimates that its own
living population is ahead. A 1-for-1 exchange then preserves the lead and
denies the opponent a catch-up route.
Engine dragon IDs are sequential, so Doug tracks
the highest recently observed enemy-owned ID and combines that frontier with
its exact own unit count and observed positive population deltas. With a safety
margin for unseen deaths and same-turn birth/death pairs, an equal-length
head-to-head gets extra value only when Doug is estimated to be ahead
and only during rounds 20–180. The signal expires when the ID frontier is
stale; it never treats a local/stale ID as a global count.

This is an early-convergence experiment, not a promotion claim. Results are
recorded with the Doug comparison panels as they are run. The global early
split-stop variants were rejected because they gave up too much population.
