# Bifröst v08 — opening sector spread

This experiment keeps Bifröst v01's movement, split and endgame policy. For the first 40 rounds on maps up to 625 cells, it adds a 2.5-point target-value bonus to unseen cells in an identity-assigned exploration sector. The preferred sector uses the dragon ID, so neighboring allied units receive different frontier preferences. This isolates the reported Trophy opening-route overlap.

The screen uses the same six maps and four external opponents as the previous Bifröst experiments. See the [family notes](../../docs/bifrost-family.md).


## Test result

Rejected after a 60-game focused screen: 37 wins and 23 losses, with no errors or runtime faults. It lost 5–7 to Bifröst v01. On 48 external fixtures paired by opponent, map, side and seed, v01 scored 43–5 and v08 scored 32–16; v08 gained zero results and regressed on 11. It won both direct Trophy fixtures but did not preserve the rest of the panel. See the candidate report (`../../experiment_data/bifrost-v08-opening-sector-spread_20260927123457377306/summary.md`) and matched V01 control (`../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md`).
