# Bifröst v09 — shorter-enemy trade safety

This experiment retains Bifröst v01's policy and changes only threat-cost accounting for shorter enemies. When a shorter enemy can reach our longer dragon, it discounts none of the enemy's value as compensation for losing our dragon. The target case is the reported Default turn-63 move that gave a smaller enemy a profitable suicide trade.

The focused screen uses the same six maps, five opponent entries and deterministic seeds as the earlier Bifröst experiments. See the [family notes](../../docs/bifrost-family.md).


## Test result

Rejected after a 60-game focused screen: 33 wins and 27 losses, with no errors or runtime faults. It lost 4–8 to Bifröst v01. On 48 external fixtures paired by opponent, map, side and seed, v01 scored 43–5 and v09 scored 29–19; v09 gained zero results and regressed on 14. The shorter-enemy trade cost is not retained. See the [candidate report](../../experiment_data/bifrost-v09-shorter-enemy-trade-safety_20260927123913152596/summary.md) and [matched V01 control](../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md).
