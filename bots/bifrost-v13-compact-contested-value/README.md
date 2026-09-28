# Bifröst v13 — compact contested-resource value

This experiment keeps Bifröst v01's movement, split and threat policies. Through round 200 on maps up to 625 cells, it raises `enemy_disc` from 0.6 to 0.85 when an enemy is closer to a pearl or bed. It tests whether discounting contested resources causes Bifröst to concede pearl-rich territory on Devil, Prisoner's Dilemma and Trophy.

The screen uses the same maps, opponents and fixture seeds as the prior experiments. See the [family notes](../../docs/bifrost-family.md).


## Test result

Rejected after a 60-game focused screen: 38 wins and 22 losses, with no errors or runtime faults. It lost 4–8 to Bifröst v01. On 48 external fixtures paired by opponent, map, side and seed, v01 scored 43–5 and v13 scored 34–14; v13 gained two results and regressed on 11. It swept Avery on Devil and Trophy but did not improve the overall panel. See the candidate report (`../../experiment_data/bifrost-v13-compact-contested-value_20260927125904217355/summary.md`) and matched V01 control (`../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md`).
