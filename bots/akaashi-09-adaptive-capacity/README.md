# Akaashi 09 — adaptive hotspot capacity

Experimental fork of immutable Akaashi 08. It inherits the Akaashi 01–08
queen safety, strike, split, body-occupancy, sprint escape, late-material,
hotspot, and queen-intercept behavior. Its only strategy change is the
surplus-resource discount from Akaashi 07: after the two-nearest-head
reservation (plus visible enemy pressure), the third nearby collector values
that resource at 45%, the fourth at 22.5%, and further surplus ranks taper to
a 12% floor. This replaces the flat 3% value. The opening, queen/crown/feed
roles, and ordinary crowded-production suppression are unchanged.

The hypothesis is that a smooth penalty keeps surplus dragons expanding while
avoiding a near-binary target cutoff that can strand a unit when alternate
resources are distant, hidden, or unavailable. The rule uses only visible
heads and target distances; it does not use map IDs or replay coordinates.
The candidate is local and experimental until compared against the complete
Akaashi line, including the previously untested 07 and 08 snapshots.
