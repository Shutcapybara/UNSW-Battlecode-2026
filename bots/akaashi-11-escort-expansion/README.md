# Akaashi 11 — escort expansion

Experimental fork of immutable Akaashi 08. It keeps the Akaashi 01–06
survival and queen-strike logic, plus Akaashi 08's queen escort and the
crowded-production suppression introduced in 07. It disables only the
per-resource nearby-head discount: each resource retains its normal target
value regardless of local collector rank.

This control tests whether Akaashi 07's target reservation harms the best
earlier strategies by steering surplus units away from resources they can
still safely collect. The 07 production rule remains active, so this does
not disable expansion when too many allies crowd the current head. No
map-specific conditions are used. This local snapshot is experimental pending
the full focused comparison against Akaashi 01–10.
