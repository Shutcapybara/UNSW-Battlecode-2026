# Gavroche V41 CPU profile

Parent: V36. The policy is unchanged; this diagnostic records per-turn counts
from round 350 onward for simulations, threat search, floods, target search, and
visible-body vacancy traversal. Counter updates and log output add some CPU
overhead, so the measured point totals are for hotspot attribution only.

Among the 20 highest-CPU candidate turns in the four-game sandbox sample, 18
evaluated all 52 paths, including 36 three-step paths. Those turns had 23–43
live units, below the 45-unit threshold for the reduced dense-phase caps. The
target search visited 116–125 nodes and flood traversals reached 333 nodes;
threat-map work was comparatively low. This points to late sparse-phase triple
enumeration as the next CPU probe.

Run: `experiment_data/gavroche-v41-cpu-profile_20260927173000000000`.
