# Ares V27 — no portal farm upgrade

V27 branches from V26. It keeps the pearl-farm and critical-enclosure gates, and applies the size upgrade only while no portal edge is known on the map. The check uses Ares's matched map atlas when populated and otherwise scans the remembered edge grid. V19's original critical escape split remains active on portal maps.

This is a topology-based guard for the observed Portal regression; it does not identify maps by name.

Development screen: Portal and Slithery Fight, both seats, seed 1 versus Ares V19: 0-4 with zero runner errors. The known-portal gate suppressed the Slithery gain and did not beat V19.
