# Gavroche v22: bounded late feeding

Parent: Gavroche v21. It keeps v21's Big Empty CPU cap on three-step sprint
candidate fanout and changes only the endgame crown donation rule, adapting
Avery v06's conservative feeder.

A fresh, longer crown can recruit only donors of length 10 or less. On a
64x64 map, donors wait until round 410 and travel toward the crown; within two
tiles of the visible crown they deliberately submit no action and die in
place. The feeder sends no sonar on its final turn. The hypothesis is that
short donors can bank length for the longest dragon without exposing a long
crown or feeding too early.

The CPU cap and feeding behavior are separate from the replay-inferred
opponent identity: public records do not reveal which of the two archive sets
was Nick versus Tom. This variant needs a focused cross-family comparison
before promotion.
