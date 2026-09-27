# Bifröst v14 — proactive corridor rescue

This experiment keeps Bifröst v01's normal movement and production splits. It adds the existing tail-escape split as a scored action when no legal move leaves at least two extra reachable cells beyond the body and the best action score is below 1.5. The rescue split only wins when it can preserve the long tail branch, and targets the reported narrow-corridor case where the dragon remains alive but blocks the route.

The screen uses the same six maps and five opponent entries as earlier experiments. Slithery Flight is not included in the local map set, so this panel measures collateral effects on available maps. See the [family notes](../../docs/bifrost-family.md).


## Test result

Rejected after a 60-game focused screen: 34 wins and 26 losses, with no errors or runtime faults. It lost 4–8 to Bifröst v01. On 48 external fixtures with the same opponent, map, side and fixture seed, v01 scored 43–5 and v14 scored 30–18; v14 gained zero results and regressed on 13. The broad rescue trigger is not retained; Slithery Flight was absent from the local map set. See the [candidate report](../../experiment_data/bifrost-v14-proactive-corridor-rescue_20260927130543949170/summary.md) and [matched V01 control](../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md).
