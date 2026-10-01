# Ares V23 — farm-gated salvage split

V23 branches from Ares V19. It preserves V19's action scores and routine size-2 split unless the best move is a pearl-rich farm in a room smaller than the simulated body. If the selected action is then a smaller split and a safe tail exit exists, V23 upgrades it to the largest legal child, leaving two front segments at the feeding point.

The farm signal reuses V19's existing condition: the room is under-sized for the body, the room's pearls bring the dragon to at least the split threshold and exceed room capacity, and the team is below its unit limit. This targets the dead-end spawner cases in the Tyr V01 loss review without widening the general critical-reach trigger.

Development screen: all 10 maps and both seats, seed 1 versus Ares V19: 10-10 with zero runner errors. The farm-gated largest-child upgrade did not beat V19.
