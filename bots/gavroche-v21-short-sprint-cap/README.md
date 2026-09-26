# Gavroche v21: short-sprint CPU cap

Parent: Gavroche v19. The v19 Big Empty sandbox mirror completed but still
peaked at 99.1M CPU points (p99 82.7M/83.3M). Profiling by inspection points
to up to 36 three-step paths being added for every dragon whenever an enemy is
within four tiles. V21 disables only those three-step candidates; one- and
two-step action candidates remain unchanged. This isolates the most obvious
candidate-count expansion and is intended to create CPU margin before the
cross-family screen. Strategic effects require comparison.
