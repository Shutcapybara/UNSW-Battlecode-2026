# Ares V29 — finish dead-end feeding before splitting

V29 branches from V28. Match 658569 showed a length-4 dragon split 2+2 at round 25, before moving to the final known pearl in an under-room dead-end farm. The parent then collected that pearl, reached length 3, and wall-died at the endpoint two rounds later.

V29 carries the existing under-room farm signal from movement scoring into split selection. When the best move continues toward a known pearl or bed in that farm, it defers routine, opening, and emergency splits and takes the movement. Split choices resume once the farm condition or pearl target ends. Outside that case, V28's two-segment critical escape and all other decisions remain.

Development screen: pending.
