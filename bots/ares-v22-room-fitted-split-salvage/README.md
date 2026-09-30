# Ares V22 — room-fitted split salvage

V22 branches from Ares V19. It preserves V19's movement policy, routine size-2 split choice, and critical enclosure fallback unless the size-2 split leaves the parent below its room requirement. In that case, V22 evaluates larger tail children and chooses the smallest split size for which both resulting dragons have enough forecast room to continue.

The child room requirement scales with its starting length; the parent uses V19's existing length-plus-slack requirement. If no larger split satisfies both forecasts, V22 keeps V19's split. This targets the live-loss review's dead-end feeding cases while avoiding V21's unconditional critical-state upgrade.

Development screen: all 10 maps and both seats, seed 1 versus Ares V19: 10-10 with zero runner errors. The room-fitted size upgrade did not beat V19.
