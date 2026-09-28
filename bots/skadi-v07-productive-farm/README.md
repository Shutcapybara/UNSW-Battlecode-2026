# Skadi v07: productive-farm-only probe

Starts from V54 and tightens only its existing trap/farm discount. Pearls
already eaten on a simulated path are excluded; a pocket receives the farm
discount only when a forager can reach split length and recover the two
segments left behind as a trapped parent without losing net team length. The
exit guard and Fafnir support are disabled in this ablation.

Panel results are recorded in `docs/skadi.md` after the seeded comparison.
