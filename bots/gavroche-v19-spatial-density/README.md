# Gavroche v19: spatially indexed density

Parent: Gavroche v18. It keeps v17's policy and parameters, including the
single flood-fill for trap and gradient scoring. The density field now buckets
active sonar reports into radius-sized toroidal cells; a tile query checks only
its own and adjacent buckets, then applies the original distance kernel in the
original report order. Scores and communication are intended to remain
unchanged while reducing Python work per queried tile on dense 64×64 maps.

The v18 judge-sandbox Big Empty run completed all 500 rounds without invalid
actions, but peaked at 99.5M CPU points with p99 76.6M/81.0M. This version
addresses the remaining CPU margin before adding the independent late-feed
experiment.
