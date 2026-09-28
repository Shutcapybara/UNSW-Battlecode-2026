# Skadi v03: exit-guard-only ablation

Starts from Gavroche V54 and adds only Scholze's exit guard. It penalizes
zero-exit moves, except when visible pearls can fund a net-productive split and
a bounded room check finds space for the escape child. One-exit moves receive
a smaller penalty. V54's original trap and farm scoring is unchanged.

This ablation is measured on the same 108 seeded fixtures as V54. Results are
recorded in `docs/skadi.md` after the comparison completes.
