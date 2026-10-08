# Akaashi 05 — bounded sprint queen escapes

Fork of immutable Akaashi 04, preserving visible-body safety, queen attacks,
queen terrain continuation and threatened-split dodging. Atlas disabled.

When the incumbent landing is risky or a split needs a dodge, compare fully
observed paths of one to three steps in shortest-first order. Exact prefix
simulation checks own/other bodies, pearls and sprint affordability. Accept
only endpoints with lower existing risk (or a surviving alternative to a
forced split), with six continuation moves after the whole path. Stop at
the first zero-risk endpoint. Safe incumbent moves are unchanged.

The former guard evaluated the final cell of an incumbent sprint but only
proposed single-step replacements. Trigger: Around UNSW 1410660 queen at
r388, length 27, chooses N into an enemy's sprint reach; NN passes the full
continuation test and escapes that recorded attack. An official-engine
scripted branch confirms avoidance at r388, but the queen dies in another
head-on at r397. This is a targeted correction, not guaranteed survival.

Synthetic test: `python3 tests/test_akaashi_sprint_escape.py`. All earlier
Akaashi regression suites also cover 05. See [campaign review](../../docs/finals-campaign/HEARTBREAKER_ITERATION.md).
