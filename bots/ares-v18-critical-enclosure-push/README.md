# Ares V18 — critical enclosure push

V18 uses V16's narrow activation gate (current reach <=8 cells) and five-step, body-blocked post-move reach delta. It changes only `enclosure_reach_weight`, from 0.35 to 1.2, matching Ares' existing `goal_weight`. The intended effect is to prioritize opening a path out of the highest-risk pocket without changing choices outside that state.

V17's all-10-map, both-seat seed-1 screen reduced pooled `death_rate_enclosed_per1k` from 88.08 to 78.61, but scored 8-12 and reduced mean r100 total length from 49.4 to 37.8. Replay reach histograms localized the sharpest hazard to <=8 reachable cells: 675.6 deaths per 1k sampled exposures for V09 versus 628.5 for V17. V18 targets only that state with a stronger score.

Development screen: all 10 active maps, both seats, seed 1 against Ares V09, sandbox enabled. Compare exact replay reach-band rates, pooled enclosure hazard, W/L, r100 economy and retention, and sandbox CPU points.
