# Ares V15 — bounded enclosure reach cost

Ares V15 branches from V14 and keeps the same five-step, 15-cell, body-blocked reach probe. It replaces V14's hard choice of an open move with a bounded score adjustment proportional to the post-move reach change. The adjustment applies while the current dragon is enclosed, and when a move would enter an enclosed state; open-space target ranking remains V09's.

V14 lowered the exact enclosed-death rate by only 4% on the all-10-map screen (78.25 vs 81.67 per 1k enclosed dragon-turns), while losing 5–15 and reducing r100 pearls and length. The hard escape selection was too disruptive. V15 tests a gradual adjustment to the same single enclosure signal.

Completed development screen: all 10 active maps, both seats, seed 1 against V09, sandbox enabled; 20/20 replays decoded without errors. V15 scored 6-14. Pooled `death_rate_enclosed_per1k` was 71.00 vs V09's 82.95, enclosed share 0.125 vs 0.232, wall deaths 7.40 vs 9.66 per 1k dragon-turns, mean r100 pearls 74.4 vs 134.0, and mean r100 units 14.8 vs 23.2. The leak metric improved, but the economy and W/L regression reject this broad activation. V16 narrows the same score to current reach <=8 cells.
