# Bifröst v04 — net-growth farms

This experiment retains Bifröst v01's portal memory, movement policy, and endgame schedule. It changes the dead-end farm test: the pocket is only treated as a viable farm when its currently visible pearl surplus leaves at least one extra segment after the two-segment escape split.

The threshold targets the reported Autarky and Prisoner's Dilemma cases where a pearl-filled dead end led to a split but no net growth. It is a focused hypothesis; the result will be recorded in the [family notes](../../docs/bifrost-family.md).


## Test result

Rejected after a 60-game focused screen: 36 wins and 24 losses, with no errors or runtime faults. It went 5–7 against Bifröst v01. On 48 external fixtures paired by opponent, map, side and seed, v01 scored 43–5 and v04 scored 31–17; v04 gained one result and regressed on 13. It swept Prisoner's Dilemma against the selected opponents but lost on Autarky and Queen of Spades. See the candidate report (`../../experiment_data/bifrost-v04-net-growth-farms_20260927121518462201/summary.md`) and matched V01 control (`../../experiment_data/bifrost-v01-portal-memory_20260927121857063579/summary.md`).
