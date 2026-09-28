# Bifröst V29 — tuned net-growth farms

V29 starts from the complete Bifröst V01 source and retains all 13 V01
overrides. It retests V04's dead-end farm rule: a pocket is treated as a viable
farm only when its visible pearl surplus leaves at least one segment of net
growth after the two-segment escape split. This targets the Autarky and
Prisoner's Dilemma cases reported by the user.

The focused native screen finished 47–13 over 60 games, with no errors or
runtime faults. It went 7–5 head-to-head against V01. On the 48 external
fixtures, it scored 40–8 versus the V01 control's 43–5, with one paired gain
and four regressions. Devil improved by one result, while Autarky regressed by
two, Dilemma by one and Default by one. Queen of Spades and Trophy matched the
control. The net-growth farm rule was rejected and is not the strongest family.

See the [benchmark report](../../experiment_data/bifrost-v29-tuned-net-growth-farms_20260928050537354662/summary.md),
[per-map summary](../../experiment_data/bifrost-v29-tuned-net-growth-farms_20260928050537354662/summary_by_map.csv),
and [family notes](../../docs/bifrost-family.md). The strongest tested
candidate remains V01; V28 tied its external panel but did not change outcomes.
