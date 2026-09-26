# Gavroche v20: bounded late feeding

Parent: Gavroche v19. Keeps the replay-driven CPU optimizations and changes
only the crown donation policy, adapting Avery v06's conservative endgame rule.

A fresh, longer crown can recruit only donors of length 10 or less. On a
64x64 map, donors wait until round 410 and move toward the crown; once within
two tiles of the visible crown, they deliberately submit no action and die in
place. This banks the existing body as pearls without risking a longer dragon
or sacrificing the donor while it is still far away. The feeder sends no sonar
on its final turn.

This is a strategic experiment prompted by the replays' longest-dragon losses.
It is separate from v19's behavior-preserving CPU work and needs a focused
cross-family comparison before promotion.
