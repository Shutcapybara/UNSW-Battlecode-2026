# Bifröst v06 — local split crowding

This experiment keeps Bifröst v01's production schedule and adds only a local head-crowding gate to ordinary and opening production splits. A dragon may split when at most one allied head is within four movement steps. The gate targets the reported Queen of Spades portal congestion while avoiding V05's team-wide unit cap.

The focused screen uses the same fixtures as V04 and V05. See the [family notes](../../docs/bifrost-family.md).


## Test result

Rejected after a 60-game focused screen: 32 wins and 28 losses, with no errors or runtime faults. It lost 3–9 to Bifröst v01. On 48 external fixtures paired by opponent, map, side and seed, v01 scored 43–5 and v06 scored 29–19; v06 gained two results and regressed on 16. The local split gate is not retained. See the [candidate report](../../experiment_data/bifrost-v06-local-split-crowding_20260927122649557512/summary.md) and [matched V01 control](../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md).
