# Ares V17 — enclosed-only reach score

V17 keeps V16's five-step, body-blocked post-move reach delta and 0.35 score weight. It changes only the activation threshold from current reach <=8 to <=15 cells, matching the benchmark's definition of an enclosed position. The score is applied only when the current dragon is enclosed; candidate moves that enter an enclosed state from open space are not penalized.

V16 screened all 10 active maps, both seats, seed 1 against V09. It scored 9-11. The pooled enclosed-death rate was 83.59 vs 80.21 per 1k for V09, while mean r100 pearls were 114.6 vs 118.4 and mean r100 units were 17.8 vs 19.0. The <=8 activation was too narrow to fix the measured leak.

Development screen: all 10 active maps, both seats, seed 1 against Ares V09, sandbox enabled. Compare exact replay features, W/L, r100 economy and retention, and sandbox CPU points.
