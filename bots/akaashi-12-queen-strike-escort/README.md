# Akaashi 12 — queen strike escort

Experimental fork of Akaashi 02, the highest-ranked snapshot in the measured
01–06 round robin. It preserves 01's queen escape and 02's visible affordable
queen strikes, then ports 08's nearest-ally escort potential for a comparable
enemy near the queen. The normal body simulator, queen threat costs, and
existing safety rules remain active. No per-target hotspot discount is added.

This variant tests whether the 08 escort is compatible with the stronger 02
baseline. It deliberately starts from 02 because the cumulative 08-derived
variants have not yet shown an aggregate advantage over the full line. Local
and experimental; see the Akaashi family experiment log for the head-to-head
screen against every existing snapshot, including untested 07–11.
