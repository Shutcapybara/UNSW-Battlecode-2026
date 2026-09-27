# Bifröst v10 — arrival-ready beds

This experiment retains Bifröst v01's portal memory, production and combat policy. It changes only `bed_wait`, from 12 rounds to zero: a predicted pearl bed is a target only if it will be ready by the dragon's arrival. This borrows the arrival-only bed rule from the Witten X03 confirmed-fastbed line and tests whether stale or not-yet-ready beds cause low-impact circling on Devil and related maps.

The screen uses the same six maps, five opponent entries and deterministic seeds as the other focused experiments. See the [family notes](../../docs/bifrost-family.md).


## Test result

Rejected after a 60-game focused screen: 1 win and 59 losses, with no errors or runtime faults. It lost all 12 direct games to Bifröst v01. Witten X03's arrival-only bed rule does not transfer as a standalone change. See the [candidate report](../../experiment_data/bifrost-v10-arrival-ready-beds_20260927124438424001/summary.md).
