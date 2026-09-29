# Doug V24 — crowd-neutral resource frontier

**Base:** Tyr V12, including its Devil scouting tie-break and reduced search
caps.

**Changes:** V24 keeps Tyr V12's round-380 production and non-crown growth
schedule, but starts crown claims at round 200 once a dragon reaches length 6.
The crown's segment value rises to 4.5 and feeding opens earlier. This lets
one large dragon begin converging while the rest of the team preserves the
population race. It keeps the conservative early-game population signal and
ID-aware own-lead equal trades. It removes only the Yuna-derived directional
momentum term to test whether momentum interferes with large-dragon banking.
Engine dragon IDs are sequential, so Doug tracks
the highest recently observed enemy-owned ID and combines that frontier with
its exact own unit count and observed positive population deltas. With a
same-turn birth/death assumption, an equal-length head-to-head gets extra value
only when Doug's estimated living population is ahead, and only during rounds
20–240. V20 removes the two-snake uncertainty haircut, keeps the frontier
fresh for 20 rounds, and raises the equal-trade bonus modestly. The signal
still expires when the ID frontier is stale; it never treats a local/stale ID
as a global count. The early crown schedule is limited to maps of area at
least 3000, leaving medium and constrained maps on Tyr's production-preserving
schedule. V24 removes only the ally-density discount from resource scoring, so
nearby friendly scouts no longer make a pearl or bed look less valuable while
the early population race is still unresolved.

This is an early-convergence experiment, not a promotion claim. Results are
recorded with the Doug comparison panels as they are run. The global early
split-stop variants were rejected because they gave up too much population.
