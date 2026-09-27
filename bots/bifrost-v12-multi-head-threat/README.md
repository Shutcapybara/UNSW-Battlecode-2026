# Bifröst v12 — multi-head threat cost

This experiment retains Bifröst v01's policy and discounts no change outside enemy-head threat evaluation. When multiple enemy heads can reach the same destination, it keeps the strongest threat estimate and adds half of the remaining estimated costs. The hypothesis follows replay reviews showing 27 head-to-head deaths in Bifröst's Devil loss to Godel and 88 in its Trophy loss to Gavroche.

The screen uses the same six maps and five opponent entries, with `fixture_hash_v1` seeds. See the [family notes](../../docs/bifrost-family.md) and [matched V01 control](../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md).


## Test result

Rejected after a 60-game focused screen: 35 wins and 25 losses, with no errors or runtime faults. It lost 3–9 to Bifröst v01. On 48 external fixtures paired by opponent, map, side and seed, v01 scored 43–5 and v12 scored 32–16; v12 gained zero results and regressed on 11. See the [candidate report](../../experiment_data/bifrost-v12-multi-head-threat_20260927125442323133/summary.md) and [matched V01 control](../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md).
