# Akaashi 10 — ranked hotspot capacity

Experimental fork of immutable Akaashi 08. It carries forward the 01–08
queen safety, visible strike, threatened split, body-occupancy, sprint escape,
late-material, hotspot, and queen-intercept behavior. The only strategy
change is to rank surplus heads around a resource target: after the two
nearest heads plus visible enemy pressure, the next head values that target
at 12%, later ranks taper to a 3% floor. Opening, queen/crown/feed roles, and
crowded-production suppression are unchanged.

This is a retuned alternative after Akaashi 09's 45% first-surplus value
underperformed across the initial 96-game development screen. The steeper
graded rule aims to preserve dispersal while protecting the two reserved
collectors' resource lead. It uses current observations only and has no
map-specific conditions. See the experiment log for the full Akaashi-line
comparison; this snapshot remains experimental until that screen finishes.
