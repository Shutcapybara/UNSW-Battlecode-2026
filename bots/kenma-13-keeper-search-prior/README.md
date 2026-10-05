# Kenma 13 — keeper model inside movement search

Parent: kenma-08-lossless-direction (strategy equivalent to 03). For original queens only, replace the Heartbreaker first-step log prior with the existing Kenma 04 keeper model's four movement probabilities, conditioned on movement and mapped F/R/B/L to absolute directions. Keep the parent's prior weight 1.0. All search terms, candidate paths, splits, sealed-pocket rescue, population reserve and nonqueen behavior remain parent code. No direct action override, orbit, retraining, map identity or tuned cutoff.

Motivation: direct keeper action variants 04/05/07 improved some queen survival but scored below 03. This tests whether their direction information helps when evaluated alongside parent room, threat, growth and sprint scoring. The model's existing export parity is already verified; this variant changes only integration. Seven-class split mass is removed by normalizing the four movement probabilities, so it cannot distort move-versus-split scores simply because the teacher preferred to split.

Status: prepared, unmeasured. Reserved seeds 11–13 and new maps untouched. Candidate must complete the standard 102-game Carthage screen before a strength claim.
