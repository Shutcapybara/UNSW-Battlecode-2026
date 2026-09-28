# Bifröst v07 — stronger anti-dither

This experiment keeps Bifröst v01's policy and raises only the existing visited-head-cell penalty from 0.15 to 0.5. It tests whether repeated low-value routes can be broken without adding new route memory. The Devil, corridor and Trophy observations motivate the screen; the experiment uses the same focused six-map panel and matched V01 control.


## Test result

Rejected after a 60-game focused screen: 36 wins and 24 losses, with no errors or runtime faults. It lost 4–8 to Bifröst v01. On 48 external fixtures paired by opponent, map, side and seed, v01 scored 43–5 and v07 scored 32–16; v07 gained zero results and regressed on 11. The stronger global visit penalty is not retained. See the candidate report (`../../experiment_data/bifrost-v07-stronger-anti-dither_20260927123050410233/summary.md`) and matched V01 control (`../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md`).
